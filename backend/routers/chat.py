from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from db.database import get_db
from schemas import ChatMessage, ChatResponse
from services.groq_model_service import model_service
from services.log_service import log_service
from services.geo_service import geo_service
from services.interaction_service import interaction_service, build_consumer_summary_from_evidence
import uuid
import time
import re

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
        # Generate response from model (RAG disabled for production)
        answer = await model_service.generate_response(
            question=message.message,
            context=None
        )

        # If model service returned an empty string (disabled or error), trigger fallback
        if not answer or not answer.strip():
            raise RuntimeError("model-unavailable")

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
        
        # Add citation numbers to the answer if we have evidence
        answer_with_citations = answer
        if evidence_serializable:
            # Add citation at the end of relevant sentences
            citation_num = 1
            for ev in evidence_serializable:
                drug_name = ev.get('drug_name', '')
                if drug_name and drug_name.lower() in answer.lower():
                    # Add citation after mentions of the drug
                    pattern = re.compile(r'\b' + re.escape(drug_name) + r'\b', re.IGNORECASE)
                    # Only add citation to first occurrence
                    answer_with_citations = pattern.sub(f'{drug_name} [{citation_num}]', answer_with_citations, count=1)
                    citation_num += 1
            
            # If no drug names matched, add citations at paragraph ends
            if '[' not in answer_with_citations and evidence_serializable:
                paragraphs = answer_with_citations.split('\n\n')
                cited_paragraphs = []
                for i, para in enumerate(paragraphs):
                    if i < len(evidence_serializable) and para.strip():
                        # Add citation at end of paragraph
                        para = para.rstrip('.') + f' [{i+1}].'
                    cited_paragraphs.append(para)
                answer_with_citations = '\n\n'.join(cited_paragraphs)
        
        # Use the answer with citations for the main response
        answer = answer_with_citations

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

        # Build a short consumer-friendly summary. Model-first with provenance; DB-only deterministic fallback.
        consumer_summary = ""
        consumer_summary_source = None
        consumer_summary_evidence_ids = []

        # Prepare an enumerated evidence block (1-based indices) for the model to reference.
        evidence_block_lines = []
        index_to_ev_id = {}
        for idx, ev in enumerate(evidence_serializable[:6], start=1):
            index_to_ev_id[idx] = ev.get('id')
            # prefer excerpt when available
            excerpt = ''
            if ev.get('references') and len(ev.get('references')) > 0:
                excerpt = ev.get('references')[0].get('excerpt') or ''
            title = ev.get('title') or ev.get('drug_name') or ''
            evidence_block_lines.append(f"{idx}. {title}\nExcerpt: {excerpt}")

        evidence_block = "\n\n".join(evidence_block_lines)

        # If the model is enabled, prefer a model-generated summary. Try several strategies in order
        # to maximize the chance of producing a short, factual consumer summary.
        if getattr(model_service, 'enabled', False):
            try:
                # 1) If we have DB evidence, ask the model for a provenance-anchored summary
                if evidence_block:
                    model_summary, model_indices = await model_service.generate_consumer_summary_with_provenance(evidence_block, question=message.message)
                    valid_indices = [i for i in model_indices if i in index_to_ev_id]
                    if model_summary and valid_indices:
                        consumer_summary = model_summary
                        consumer_summary_source = 'model'
                        consumer_summary_evidence_ids = [index_to_ev_id[i] for i in valid_indices]

                # 2) If still empty, ask the model to summarize the assistant's full answer
                if not consumer_summary:
                    model_summary = await model_service.generate_consumer_summary(answer, question=message.message)
                    if model_summary:
                        consumer_summary = model_summary
                        consumer_summary_source = 'model'
                        consumer_summary_evidence_ids = []

                # 3) If still empty, ask the model to summarize the user's question (short prompt)
                if not consumer_summary:
                    model_summary = await model_service.generate_consumer_summary(message.message, question=message.message)
                    if model_summary:
                        consumer_summary = model_summary
                        consumer_summary_source = 'model'
                        consumer_summary_evidence_ids = []
                
                # Add citations to consumer summary if we have evidence
                if consumer_summary and evidence_serializable:
                    citation_num = 1
                    for ev in evidence_serializable:
                        drug_name = ev.get('drug_name', '')
                        if drug_name and drug_name.lower() in consumer_summary.lower():
                            pattern = re.compile(r'\b' + re.escape(drug_name) + r'\b', re.IGNORECASE)
                            consumer_summary = pattern.sub(f'{drug_name} [{citation_num}]', consumer_summary, count=1)
                            citation_num += 1
                    
                    # If no matches, add citation at end of first paragraph
                    if '[' not in consumer_summary and evidence_serializable:
                        sentences = consumer_summary.split('. ')
                        if sentences:
                            sentences[0] = sentences[0].rstrip('.') + ' [1].'
                            consumer_summary = '. '.join(sentences)
                            
            except Exception:
                # leave consumer_summary for DB-only fallback below
                consumer_summary = ""
        

        # If no valid model summary, derive a deterministic DB summary from evidence (no hybrid)
        if not consumer_summary and evidence_serializable:
            # Simple deterministic fallback: use top evidence item(s) to create a short summary
            parts = []
            ids = []
            for ev in evidence_serializable[:2]:
                ids.append(ev.get('id'))
                s = (ev.get('summary') or ev.get('title') or ev.get('drug_name') or '').strip()
                rec = ev.get('recommended_actions')
                if rec:
                    parts.append(f"{s.rstrip('.')} — Recommendation: {rec.rstrip('.')}.")
                else:
                    parts.append(s)
            consumer_summary = " ".join([p for p in parts if p])
            consumer_summary_source = 'db'
            consumer_summary_evidence_ids = ids

        # If still no consumer_summary at this point, attempt a final model-only summarization of the assistant answer
        # (this is a last-resort model-only path to populate Simple view; will be marked as model source)
        if not consumer_summary and getattr(model_service, 'enabled', False) and answer:
            try:
                final_model_summary = await model_service.generate_consumer_summary(answer, question=message.message)
                if final_model_summary:
                    consumer_summary = final_model_summary
                    consumer_summary_source = consumer_summary_source or 'model'
                    consumer_summary_evidence_ids = consumer_summary_evidence_ids or []
            except Exception:
                # ignore and leave consumer_summary as-is
                pass
        
        # Log the interaction with tracking data and provenance
        metadata['consumer_summary'] = consumer_summary
        # Construct a typed provenance object for the consumer summary
        provenance = None
        if consumer_summary_source:
            provenance = {
                'source': consumer_summary_source,
                'evidence_ids': consumer_summary_evidence_ids or []
            }
            # also store a copy in top-level metadata for easy inspection
            metadata['consumer_summary_provenance'] = provenance
        # include a minimal debug flag about model availability for dev ops
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
            consumer_summary=consumer_summary,
            sources=None,
            evidence=evidence_serializable,
            provenance=provenance
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
        # Prepare metadata including the error for logs
        metadata = metadata if 'metadata' in locals() else {}
        metadata['error'] = error_msg

        # Provide a short consumer summary for fallback responses as well (DB-only deterministic)
        if 'evidence_serializable' in locals() and evidence_serializable:
            db_summary, db_ids = build_consumer_summary_from_evidence(db, evidence_serializable, max_items=2)
            if db_summary:
                consumer_summary = db_summary
                metadata['consumer_summary_source'] = 'db'
                metadata['consumer_summary_evidence_ids'] = db_ids
            else:
                consumer_summary = "I can't reach the AI model right now. I don't have stored references that match your question — please try again later or consult a clinician."
        else:
            consumer_summary = "I can't reach the AI model right now. I don't have stored references that match your question — please try again later or consult a clinician."

        # attach summary to metadata and log
        metadata['consumer_summary'] = consumer_summary
        # Attach provenance info for fallback (if available)
        provenance = None
        if 'consumer_summary_evidence_ids' in metadata:
            provenance = {
                'source': metadata.get('consumer_summary_source', 'db'),
                'evidence_ids': metadata.get('consumer_summary_evidence_ids', [])
            }
            metadata['consumer_summary_provenance'] = provenance
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
            consumer_summary=consumer_summary,
            sources=None,
            evidence=evidence_serializable if 'evidence_serializable' in locals() else None,
            provenance=provenance
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
