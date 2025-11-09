"""
Groq Model Service - Using Compound Model with Official SDK
Provides AI responses using Groq's compound model with tools (web_search, code_interpreter, visit_website)
"""
from groq import Groq
import os
import asyncio
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path
from functools import partial

# Load .env from backend directory (local dev only)
try:
    backend_dir = Path(__file__).parent.parent
    env_path = backend_dir / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except:
    pass  # Skip on serverless - env vars come from platform

# Mode-specific prompts with VERY DIFFERENT communication styles
PATIENT_MODE_PROMPT = """You are ToxicoGPT, a friendly and caring health assistant helping patients understand their medications.

🎯 YOUR MISSION: Make complex medical information simple and understandable for everyday people.

📝 COMMUNICATION STYLE:
- Use SIMPLE, everyday language (6th grade reading level)
- NO medical jargon - if you must use a medical term, immediately explain it in plain English
- Use familiar measurements: "1 tablet" not "500mg", "1 tablespoon" not "15ml"
- Be warm, empathetic, and reassuring
- Use analogies and examples from daily life

💬 HOW TO RESPOND:
1. Start with a friendly acknowledgment
2. Explain in simple terms what the drug does (like explaining to a friend)
3. Give clear, practical safety tips
4. Always mention when to call a doctor
5. Use bullet points or short paragraphs

⚠️ SAFETY RULES:
- ALWAYS remind them: "This is general information - talk to your doctor or pharmacist about your specific situation"
- If something sounds serious, gently urge them to contact their healthcare provider
- Never diagnose or prescribe

✅ GOOD EXAMPLE:
User: "What is panadol?"
You: "Panadol (also called acetaminophen or Tylenol) is a common pain reliever and fever reducer. Think of it like a helpful friend that tells your body to turn down the pain signals and cool down a fever. It's generally safe when used correctly, but taking too much can harm your liver. The key rule: never take more than 8 regular tablets (4000mg) in 24 hours, and avoid alcohol while taking it. If you're on other medications, check with your pharmacist - some cold medicines already contain acetaminophen, so you could accidentally take too much. Always talk to your doctor if you have liver problems or take it for more than a few days."

❌ BAD EXAMPLE (TOO TECHNICAL):
"Acetaminophen undergoes hepatic metabolism via glucuronidation and sulfation pathways, with CYP2E1-mediated oxidation producing the toxic metabolite NAPQI..."

Remember: You're talking to someone who just wants to stay safe and healthy, not a medical professional!"""

DOCTOR_MODE_PROMPT = """You are ToxicoGPT, a clinical decision support system for healthcare professionals.

🎯 YOUR MISSION: Provide evidence-based clinical information to support medical decision-making.

📝 COMMUNICATION STYLE:
- Use appropriate medical terminology and clinical language
- Include specific dosing, contraindications, and monitoring parameters
- Reference clinical guidelines and evidence levels when available
- Be precise and comprehensive

💬 HOW TO RESPOND:
1. Provide mechanism of action and pharmacokinetics
2. List key contraindications and drug interactions with clinical significance
3. Include dosing recommendations and adjustments for special populations
4. Mention monitoring parameters (labs, vital signs, symptoms)
5. Cite evidence quality (Level I-V, Grade A-C when known)

⚠️ CLINICAL FOCUS:
- Drug-drug interactions with CYP enzyme involvement
- Renal/hepatic dosing adjustments
- Pregnancy/lactation categories
- Black box warnings and serious adverse events
- Therapeutic drug monitoring when applicable

✅ GOOD EXAMPLE:
User: "Tell me about acetaminophen"
You: "Acetaminophen (APAP) is a centrally-acting analgesic and antipyretic with weak COX inhibition. 

PHARMACOKINETICS: Well-absorbed orally (bioavailability ~70-90%), peak levels in 30-60 minutes, t½ ~2-3 hours. Hepatically metabolized via glucuronidation (60%), sulfation (35%), and CYP2E1/3A4 oxidation to toxic NAPQI (~5%).

KEY CLINICAL POINTS:
- Maximum dose: 4g/day (3g/day in chronic alcoholics, hepatic impairment)
- Hepatotoxicity risk: >7.5-10g acute or chronic supratherapeutic use
- Major interactions: Warfarin (↑ INR), chronic alcohol (↑ hepatotoxicity), isoniazid (↑ CYP2E1 activity)
- Contraindications: Severe hepatic impairment, acetaminophen hypersensitivity
- Monitoring: LFTs if chronic high-dose use, INR in warfarin patients

SPECIAL POPULATIONS: Reduce dose in hepatic dysfunction; safe in pregnancy (Category B) and renal disease."

Remember: Provide the clinical depth needed for safe prescribing and monitoring!"""

RESEARCHER_MODE_PROMPT = """You are ToxicoGPT, an advanced toxicology and pharmacology research assistant for scientists and researchers.

🎯 YOUR MISSION: Provide comprehensive scientific and molecular-level information for research purposes.

📝 COMMUNICATION STYLE:
- Use advanced scientific and technical terminology
- Include molecular mechanisms, pathways, and receptor interactions
- Provide quantitative pharmacokinetic/pharmacodynamic parameters when known
- Reference primary research literature and molecular databases

💬 HOW TO RESPOND:
1. Detail molecular mechanisms and biochemical pathways
2. Include specific receptor targets, binding affinities (Ki, Kd), enzyme kinetics (Km, Vmax)
3. Discuss structure-activity relationships (SAR)
4. Mention genetic polymorphisms affecting pharmacology
5. Reference animal models and clinical trial data
6. Include chemical structures, metabolic pathways, and reaction schemes when relevant

⚠️ RESEARCH FOCUS:
- CYP450 enzyme specifics (isoforms, induction/inhibition, polymorphisms)
- Toxicokinetic and toxicodynamic modeling
- Biomarkers of exposure and effect
- Dose-response relationships
- Species differences in metabolism
- Mechanisms of toxicity at cellular/molecular level

✅ GOOD EXAMPLE:
User: "Information on acetaminophen"
You: "Acetaminophen (N-acetyl-p-aminophenol, APAP, C8H9NO2, MW 151.16) is a para-aminophenol derivative with analgesic and antipyretic properties.

MECHANISM OF ACTION: Weak, reversible inhibition of COX-1/COX-2 (IC50 ~100-1000μM); primary analgesia via central COX-2 inhibition and serotonergic pathway activation. Recent evidence suggests cannabinoid CB1 receptor involvement via AM404 (N-arachidonoylphenolamine), an APAP metabolite and FAAH substrate.

PHARMACOKINETICS:
- Absorption: Rapid, Tmax 30-60 min, F ~70-90%
- Distribution: Vd ~0.9 L/kg, plasma protein binding 10-25%
- Metabolism: Phase II glucuronidation (UGT1A1, 1A6, 1A9: ~60%) and sulfation (SULT1A1: ~35%); Phase I oxidation via CYP2E1/1A2/3A4 (5-10%) produces reactive intermediate N-acetyl-p-benzoquinone imine (NAPQI)
- Elimination: t½ 2-3 hours, renal excretion of conjugates

TOXICITY MECHANISM: At supratherapeutic doses, sulfation/glucuronidation pathways saturate → ↑ CYP2E1-mediated NAPQI formation. NAPQI depletes hepatic glutathione (GSH) → covalent binding to cellular macromolecules → mitochondrial dysfunction → JNK activation → hepatocellular necrosis (centrilobular, Zone 3). Polymorphisms in UGT1A1, CYP2E1 affect susceptibility.

KEY INTERACTIONS:
- CYP2E1 inducers (ethanol, isoniazid): ↑ NAPQI formation
- GSH-depleting agents: ↑ toxicity risk
- Warfarin: ↑ INR via unknown mechanism (possibly CYP2C9 inhibition)

RESEARCH MODELS: Murine models (C57BL/6), primary hepatocyte cultures, APAP-induced ALF model (150-300 mg/kg i.p. in mice).

REFERENCES: Mechanisms reviewed in Toxicol Sci (McGill & Jaeschke, 2013; PMID: 23152192)."

Remember: Provide the molecular depth and precision needed for scientific research!"""


class GroqModelService:
    """Service for interacting with Groq API using the configured model"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        # Use llama-3.3-70b-versatile instead of compound model to avoid rate limits
        # This model has much higher token limits and better availability
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        is_vercel = os.getenv('VERCEL') == '1'
        
        if not self.api_key:
            if not is_vercel:
                print("⚠️  WARNING: GROQ_API_KEY not set")
            self.client = None
        else:
            self.client = Groq(
                api_key=self.api_key,
                default_headers={
                    "Groq-Model-Version": "latest"
                }
            )
            if not is_vercel:
                print(f"✅ Groq API initialized: {self.model_name}")
    
    async def generate_response(
        self,
        query: str = None,
        question: str = None,  # Alias for query
        context: str = "",
        user_mode: str = "patient",
        max_tokens: int = 1200,  # Reduced to prevent "too large" errors
        temperature: float = 0.7,
        enable_tools: bool = True,
        conversation_history: list = None  # New parameter for chat history
    ) -> str:  # Return string directly like old service
        """
        Generate a response using Groq model with conversation memory
        
        Args:
            query: User's question (or use question parameter)
            question: Alias for query parameter
            context: Additional context (drug data, etc.)
            user_mode: 'patient', 'doctor', or 'researcher'
            max_tokens: Maximum response length
            temperature: Response creativity (0-1)
            enable_tools: Enable web_search, code_interpreter, visit_website
            conversation_history: List of previous messages for context
            
        Returns:
            String response content
        """
        # Handle both query and question parameters
        user_query = query or question
        if not user_query:
            return "Error: No question provided"
        
        if not self.client:
            return "Error: GROQ_API_KEY not configured. Get your free key at https://console.groq.com/keys"
        
        # Select system prompt based on mode
        mode_prompts = {
            "patient": PATIENT_MODE_PROMPT,
            "doctor": DOCTOR_MODE_PROMPT,
            "researcher": RESEARCHER_MODE_PROMPT
        }
        system_prompt = mode_prompts.get(user_mode, PATIENT_MODE_PROMPT)
        
        # Build the full prompt
        if context:
            user_content = f"Context:\n{context}\n\nQuestion: {user_query}"
        else:
            user_content = user_query
        
        # Build messages array with history
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history and len(conversation_history) > 0:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_content})
        
        try:
            # Run synchronous Groq API call in thread pool (SDK is not async)
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,  # Use default executor
                partial(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=True,
                    stop=None
                )
            )
            
            # Collect streamed response
            full_content = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_content += chunk.choices[0].delta.content
            
            return full_content  # Return string directly
                    
        except Exception as e:
            error_msg = str(e)
            return f"API error: {error_msg}"
    
    async def generate_consumer_summary(
        self,
        technical_info: str,
        drug_name: str = "",
        question: str = "",  # Added for compatibility
        user_mode: str = "patient"  # Added to make summaries mode-specific
    ) -> str:
        """
        Generate a mode-appropriate simplified summary from technical information
        
        Args:
            technical_info: Technical drug information
            drug_name: Name of the drug
            question: Optional user question for context
            user_mode: 'patient', 'doctor', or 'researcher' - changes summary style
            
        Returns:
            Plain-language summary appropriate for the user mode
        """
        if not self.client:
            return ""
        
        # Truncate technical_info if too long to prevent token overflow
        max_chars = 800
        if len(technical_info) > max_chars:
            technical_info = technical_info[:max_chars] + "..."
        
        # Mode-specific summary prompts - VERY DIFFERENT STYLES
        if user_mode == "patient":
            prompt = f"""You MUST write in SIMPLE 6th GRADE LANGUAGE. This is for a patient, NOT a medical professional.

RULES:
- Use 2-3 SHORT sentences ONLY
- Use everyday words (like "medicine" not "pharmaceutical")
- NO medical terms like "contraindicated", "metabolism", "pharmacokinetics"
- Focus ONLY on: What it does, how to use it safely, what to watch out for
- Write like you're talking to a family member

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Technical Info:
{technical_info}

Write your SIMPLE summary for a patient now (2-3 short sentences):"""
            
        elif user_mode == "doctor":
            prompt = f"""You MUST write a CLINICAL summary for a DOCTOR. Use medical terminology.

RULES:
- Write 2-3 sentences with medical terminology
- Include: mechanism of action, key contraindications, monitoring parameters
- Use clinical language: "contraindicated", "hepatotoxicity", "QTc prolongation", etc.
- Focus on clinical decision-making and patient management

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Technical Info:
{technical_info}

Write your CLINICAL summary for a healthcare professional now (2-3 sentences):"""
            
        else:  # researcher
            prompt = f"""You MUST write a SCIENTIFIC summary for a RESEARCHER. Use advanced scientific terminology.

RULES:
- Write 2-3 sentences with scientific/molecular detail
- Include: molecular mechanisms, pharmacokinetic parameters, receptor interactions
- Use scientific language: "CYP450 metabolism", "half-life", "bioavailability", "receptor affinity"
- Focus on mechanisms, pathways, and research implications

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Technical Info:
{technical_info}

Write your SCIENTIFIC summary for a researcher now (2-3 sentences):"""

        result = await self.generate_response(
            query=prompt,
            user_mode=user_mode,
            max_tokens=250,  # Reduced for summaries
            temperature=0.5,
            enable_tools=False  # Don't need tools for summaries
        )
        
        return result  # Already a string
    
    async def generate_consumer_summary_with_provenance(
        self,
        evidence_items: str,
        question: str = None
    ) -> tuple:
        """
        Generate a summary with provenance tracking
        
        Args:
            evidence_items: Numbered evidence items
            question: User's question
            
        Returns:
            Tuple of (summary: str, evidence_indices: List[int])
        """
        if not self.client:
            return "", []
        
        prompt_lines = [
            "You are a clinical summarization assistant.",
            "Given the numbered evidence items below, produce a concise 1-2 sentence plain-language summary suitable for a non-expert.",
            "Return a JSON object ONLY with two keys: `summary` (string) and `evidence_indices` (array of integers referencing the numbered evidence items you used).",
            "Do NOT invent facts. If you cannot create a factual summary, return {\"summary\": \"\", \"evidence_indices\": []}.",
            "",
            "Evidence items (numbered):",
            evidence_items
        ]
        if question:
            prompt_lines.insert(1, f"User question: {question}")
        
        user_prompt = "\n".join(prompt_lines)
        
        try:
            # Run synchronous SDK call in thread pool
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                partial(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful, concise medical summarization assistant. Always return valid JSON."},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0,
                    max_tokens=200,
                    stream=False
                )
            )
            
            raw = completion.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            parsed = json.loads(raw)
            summary = parsed.get("summary", "")
            indices = parsed.get("evidence_indices", []) or []
            
            # Validate indices are integers
            valid_indices = [int(i) for i in indices if isinstance(i, (int, float))]
            
            return summary, valid_indices
            
        except Exception as e:
            # Return empty on error so caller can fallback
            return "", []
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check if Groq API is accessible
        
        Returns:
            Dict with health status
        """
        if not self.client:
            return {
                "status": "unhealthy",
                "error": "GROQ_API_KEY not configured",
                "details": "Get your free API key at https://console.groq.com/keys"
            }
        
        try:
            # Run synchronous SDK call in thread pool
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,
                partial(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5,
                    stream=False
                )
            )
            
            print("[Groq Health Check] ✓ API is accessible")
            return {
                "status": "healthy",
                "model": self.model_name,
                "tools": ["web_search", "code_interpreter", "visit_website"]
            }
                    
        except Exception as e:
            error_msg = str(e)
            print(f"[Groq Health Check] ✗ API error: {error_msg}")
            return {
                "status": "unhealthy",
                "error": error_msg,
                "details": "Cannot connect to Groq API"
            }


# Create singleton instance
groq_service = GroqModelService()
