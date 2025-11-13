from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..schemas import ChatMessage, ChatResponse
from ..services.model_router import model_service  # DeepSeek model service
from ..services.log_service import log_service
from ..services.geo_service import geo_service
from ..services.interaction_service import interaction_service, build_consumer_summary_from_evidence
from ..services.data_aggregator_service import DrugDataAggregator, extract_drug_names
import uuid
import time
import re
import json

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Main chat endpoint - processes user questions and returns AI responses
    """
    # Generate or use existing session ID
    session_id = message.session_id or str(uuid.uuid4())
    
    # Capture tracking information
    user_agent = request.headers.get("user-agent", "unknown")
    client_ip = request.client.host if request.client else "unknown"
    
    # Get geolocation data from IP
    geo_data = await geo_service.get_location_data(client_ip)
    
    # Update session tracking with geolocation
    log_service.create_or_update_session(
        db, 
        session_id, 
        user_agent, 
        client_ip,
        geo_data=geo_data
    )
    
    # Start timing
    start_time = time.time()
    
    try:
        # Get user mode from message (defaults to 'patient' if not specified)
        user_mode = getattr(message, 'user_mode', 'patient') or 'patient'
        
        # Initialize data aggregator
        aggregator = DrugDataAggregator(db)
        
        # Extract potential drug names from the query
        drug_names = extract_drug_names(message.message)
        
        # Build context from external APIs if drugs are mentioned
        external_context = None
        if drug_names:
            print(f"[Chat] Detected drugs: {drug_names}")
            
            # Fetch comprehensive data for all drugs
            drugs_data = await aggregator.get_multiple_drugs_data(drug_names)
            
            # Format the aggregated data for the LLM context
            context_parts = []
            for drug_data in drugs_data:
                if isinstance(drug_data, dict) and not drug_data.get("error"):
                    context_parts.append(f"""
Drug: {drug_data.get('drug_name', 'Unknown')}

Identifiers: {json.dumps(drug_data.get('identifiers', {}), indent=2)}

FDA Label Info: {json.dumps(drug_data.get('fda_label', {}), indent=2)}

Chemical Data: {json.dumps(drug_data.get('chemical_data', {}), indent=2)}

Known Interactions: {json.dumps(drug_data.get('interactions', []), indent=2)}

Adverse Events (OpenFDA): {json.dumps(drug_data.get('adverse_events', [])[:10], indent=2)}

Recent Literature: {json.dumps(drug_data.get('literature', []), indent=2)}
""")
            
            if context_parts:
                external_context = "\n\n=== COMPREHENSIVE DRUG DATABASE ===\n" + "\n---\n".join(context_parts)
                print(f"[Chat] Built context from {len(context_parts)} drug(s), {len(external_context)} characters")
        
        # Generate response from model with external context and user mode
        answer = await model_service.generate_response(
            question=message.message,
            context=external_context,
            user_mode=user_mode
        )

        # If model service returned an empty string (disabled or error), trigger fallback
        if not answer or not answer.strip():
            raise RuntimeError("model-unavailable")
        
        # Extract references from the model's response if it includes a REFERENCES section
        model_references = []
        if "## REFERENCES" in answer or "## References" in answer:
            # Split response into main content and references
            ref_pattern = r'##\s*REFERENCES?\s*\n(.*?)(?=\n##|\Z)'
            import re as regex_module
            ref_match = regex_module.search(ref_pattern, answer, regex_module.IGNORECASE | regex_module.DOTALL)
            
            if ref_match:
                ref_section = ref_match.group(1)
                # Parse individual references like [1] Author, Year. Title. Journal. PMID: 12345
                ref_lines = regex_module.findall(r'\[(\d+)\]\s*(.+?)(?=\[\d+\]|\Z)', ref_section, regex_module.DOTALL)
                
                for num, ref_text in ref_lines:
                    ref_text = ref_text.strip()
                    if ref_text:
                        # Try to extract URL/DOI if present
                        url_match = regex_module.search(r'(https?://[^\s]+|DOI:\s*[^\s]+|PMID:\s*\d+)', ref_text)
                        url = url_match.group(0) if url_match else "#"
                        
                        # Convert PMID to URL
                        if "PMID:" in url:
                            pmid = regex_module.search(r'PMID:\s*(\d+)', url)
                            if pmid:
                                url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid.group(1)}/"
                        
                        model_references.append({
                            "id": int(num),
                            "title": ref_text[:200],  # Truncate if too long
                            "url": url,
                            "excerpt": ref_text if len(ref_text) > 200 else None,
                            "unverified": False  # Model-generated, considered verified
                        })

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Prepare metadata including geolocation
        metadata = {
            "geo_data": geo_data
        }

        # Attempt to find structured interactions/evidence for the user's question
        evidence = interaction_service.search_interactions_in_text(db, message.message)
        evidence_serializable = []
        for e in evidence:
            refs = []
            for r in getattr(e, 'references', []) or []:
                refs.append({"id": r.id, "title": r.title, "url": r.url, "excerpt": r.excerpt})
            evidence_serializable.append({
                "id": e.id,
                "drug_name": e.drug_name,
                "title": e.title,
                "summary": e.summary,
                "mechanism": e.mechanism,
                "food_groups": e.food_groups,
                "recommended_actions": e.recommended_actions,
                "evidence_quality": e.evidence_quality,
                "references": refs
            })
        # attach to metadata for logging
        metadata["evidence"] = evidence_serializable
        
        # If no DB evidence but we have model-generated references, create evidence from them
        if not evidence_serializable and model_references:
            # Group all model references into a single evidence item
            evidence_serializable.append({
                "id": 1,
                "drug_name": "Model Citation",
                "title": "Evidence-Based Medical Literature",
                "summary": "References cited by the AI model based on medical literature and clinical guidelines.",
                "mechanism": None,
                "food_groups": None,
                "recommended_actions": None,
                "evidence_quality": "Model-Generated",
                "references": model_references
            })
            metadata["evidence"] = evidence_serializable
        
        # If no DB evidence found, try to extract any URLs or markdown links from the model answer
        # and present them as an unverified reference block so the frontend can show clickable links.
        if not evidence_serializable and answer:
            model_links = []
            seen_urls = set()

            # Find markdown links [text](url)
            for m in re.finditer(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", answer):
                title = m.group(1).strip()
                url = m.group(2).strip()
                if url not in seen_urls:
                    seen_urls.add(url)
                    model_links.append({"id": len(model_links) + 1, "title": title or url, "url": url, "excerpt": None, "unverified": True})

            # Find bare URLs
            for m in re.finditer(r"(https?://[^\s)]+)", answer):
                url = m.group(1).strip().rstrip(').,')
                if url not in seen_urls:
                    seen_urls.add(url)
                    model_links.append({"id": len(model_links) + 1, "title": url, "url": url, "excerpt": None, "unverified": True})

            if model_links:
                evidence_serializable = [
                    {
                        "id": 0,
                        "drug_name": None,
                        "title": "Model-extracted links (unverified)",
                        "summary": "Links extracted from the AI-generated response. Not verified by our database.",
                        "mechanism": None,
                        "food_groups": [],
                        "recommended_actions": None,
                        "evidence_quality": "unverified",
                        "references": model_links,
                    }
                ]
                metadata["model_extracted_links"] = [l["url"] for l in model_links]

        # No consumer_summary needed - using three-tier persona system
        # The answer already contains persona-specific content based on user_mode
        
        # Log the interaction with tracking data
        metadata['model_enabled'] = getattr(model_service, 'enabled', False)
        log_service.create_chat_log(
            db=db,
            session_id=session_id,
            question=message.message,
            answer=answer,
            model_used=model_service.model_name,
            response_time_ms=response_time_ms,
            ip_address=client_ip,
            user_agent=user_agent,
            extra_metadata=metadata
        )
        
        return ChatResponse(
            answer=answer,
            session_id=session_id,
            model_used=model_service.model_name,
            response_time_ms=response_time_ms,
            consumer_summary=None,  # No longer using dual-view system
            sources=None,
            evidence=evidence_serializable,
            provenance=None  # No longer tracking consumer summary provenance
        )
        
    except Exception as e:
        # If model generation fails, attempt to return a useful fallback built from the
        # stored interaction database so the frontend can still display evidence and recommendations.
        response_time_ms = int((time.time() - start_time) * 1000)
        error_msg = str(e)

        # Build fallback answer from found evidence (evidence_serializable may have been set above)
        fallback_parts = []
        if 'evidence_serializable' in locals() and evidence_serializable:
            for ev in evidence_serializable:
                part = f"{ev.get('title') or ev.get('drug_name')}: {ev.get('summary')}"
                if ev.get('recommended_actions'):
                    part += f" Recommendation: {ev.get('recommended_actions')}"
                fallback_parts.append(part)

        if fallback_parts:
            answer = "\n\n".join(fallback_parts)
            model_used = "fallback-db"
        else:
            # Generic fallback message when no DB evidence available
            answer = "I can't reach the AI model right now. I don't have stored references that match your question — please try again later or consult a clinician."
            model_used = "fallback-generic"

        # Prepare metadata including the error for logs
        metadata = metadata if 'metadata' in locals() else {}
        metadata['error'] = error_msg
        
        # Log the fallback interaction
        log_service.create_chat_log(
            db=db,
            session_id=session_id,
            question=message.message,
            answer=answer,
            model_used=model_used,
            response_time_ms=response_time_ms,
            ip_address=client_ip,
            user_agent=user_agent,
            extra_metadata=metadata
        )

        return ChatResponse(
            answer=answer,
            session_id=session_id,
            model_used=model_used,
            response_time_ms=response_time_ms,
            consumer_summary=None,  # No longer using dual-view system
            sources=None,
            evidence=evidence_serializable if 'evidence_serializable' in locals() else None,
            provenance=None
        )

@router.get("/history/{session_id}")
async def get_chat_history(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Retrieve chat history for a specific session
    """
    logs = log_service.get_chat_logs(db, session_id=session_id, limit=limit)
    return {"session_id": session_id, "history": logs}

@router.get("/session/{session_id}/stats")
async def get_session_stats(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific session
    """
    stats = log_service.get_session_stats(db, session_id)
    return stats
