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

# Mode-specific prompts with reading level enforcement
PATIENT_MODE_PROMPT = """You are a helpful medical assistant speaking to a general patient audience.

CRITICAL FORMATTING - Write for patients (6th grade reading level):

**Structure:**
1. Start with a simple definition (1-2 sentences)
2. Use clear section headers with emojis (💊 How to Take It, ⚠️ Important Warnings, etc.)
3. Short paragraphs (2-3 sentences max)
4. Bullet points with simple language
5. Use bold for key safety information
6. End with reassuring advice

**Language Requirements:**
- Short sentences (10-15 words max)
- Simple, everyday words (avoid: "administer" → use "take" or "give")
- No medical jargon
- Use analogies and examples
- Active voice ("Take 2 pills" not "2 pills should be taken")

**Content Focus:**
- How to take it (dose, timing, with/without food)
- What it does (effects you'll feel)
- Common side effects in simple terms
- When to call a doctor (red flags)
- Storage and safety

**Tone:** Friendly, reassuring, like explaining to a family member."""

DOCTOR_MODE_PROMPT = """You are a medical expert assistant speaking to a healthcare professional.

CRITICAL FORMATTING - Write for physicians (12th grade medical level):

**Structure:**
1. Brief clinical summary (1-2 sentences)
2. Use clear, scannable sections:
   - **Clinical Indications** (bullet points)
   - **Dosing & Administration** (concise table or bullets)
   - **Key Considerations** (contraindications, interactions)
   - **Monitoring** (what to watch for)
   - **Evidence Base** (1-2 sentence summary)
3. Use tables ONLY when they improve clarity (not for everything)
4. Keep paragraphs to 4-5 lines max
5. Bold critical safety information

**Language Requirements:**
- Medical terminology is fine, but be concise
- Avoid excessive tables (use prose for readability)
- Use clinical abbreviations (PO, q6h, etc.)
- Focus on actionable information
- Include mechanism only if clinically relevant

**Content Focus:**
- Indications with evidence level
- Dosing (standard, renal/hepatic adjustment)
- Contraindications & precautions
- Significant drug interactions
- Monitoring parameters
- Key clinical pearls

**Tone:** Professional, concise, focused on clinical decision-making.
**Format:** Clean, scannable, NO dense paragraph walls."""

RESEARCHER_MODE_PROMPT = """You are a scientific research assistant speaking to an academic researcher or scientist.

CRITICAL FORMATTING - Write for researchers (academic level):

**Structure:**
1. Brief scientific context (1-2 sentences)
2. Use clear research-focused sections:
   - **Molecular Mechanisms** (pathways, targets)
   - **Pharmacokinetics** (ADME profile with parameters)
   - **Current Research** (recent findings, ongoing studies)
   - **Methodological Considerations**
   - **Knowledge Gaps** (what's unknown)
3. Include chemical formulas/structures when relevant
4. Cite study types (e.g., "Phase III RCT, n=1,203")
5. Use scientific notation and proper units

**Language Requirements:**
- Advanced scientific terminology
- Precise quantitative data (IC₅₀, Kd, t½, etc.)
- Pathway names (MAPK/ERK, PI3K/AKT, etc.)
- Statistical measures (p-values, confidence intervals)
- Gene/protein nomenclature (CYP2E1, NAPQI, etc.)

**Content Focus:**
- Molecular mechanisms and targets
- Biochemical pathways (with intermediates)
- Pharmacokinetic/pharmacodynamic parameters
- Recent research findings with methodology
- Study design considerations
- Analytical techniques used
- Gaps in current understanding

**Tone:** Academic, precise, hypothesis-driven.
**Format:** Scientific prose with embedded data, NOT clinical tables."""


class GroqModelService:
    """Service for interacting with Groq API using compound model with tools"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = "groq/compound"
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
                print(f"✅ Groq API initialized: {self.model_name} (with tools enabled)")
    
    async def generate_response(
        self,
        query: str = None,
        question: str = None,  # Alias for query
        context: str = "",
        user_mode: str = "patient",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        enable_tools: bool = True
    ) -> str:  # Return string directly like old service
        """
        Generate a response using Groq compound model
        
        Args:
            query: User's question (or use question parameter)
            question: Alias for query parameter
            context: Additional context (drug data, etc.)
            user_mode: 'patient', 'doctor', or 'researcher'
            max_tokens: Maximum response length
            temperature: Response creativity (0-1)
            enable_tools: Enable web_search, code_interpreter, visit_website
            
        Returns:
            String response content
        """
        # Handle both query and question parameters
        user_query = query or question
        if not user_query:
            return "Error: No question provided"
        
        if not self.client:
            return "Error: GROQ_API_KEY not configured. Get your free key at https://console.groq.com/keys"
        
        # Select system prompt based on mode with formatting enforcement
        mode_prompts = {
            "patient": PATIENT_MODE_PROMPT + "\n\nFORMATTING RULES:\n- Use emojis for section headers\n- Maximum 3 sentences per paragraph\n- Use **bold** for important safety info\n- End with a reassuring note",
            "doctor": DOCTOR_MODE_PROMPT + "\n\nFORMATTING RULES:\n- NO dense paragraph walls\n- Use bullet points liberally\n- Keep tables minimal (only when truly helpful)\n- Bold critical warnings\n- Prioritize clinical decision-making info",
            "researcher": RESEARCHER_MODE_PROMPT + "\n\nFORMATTING RULES:\n- Use scientific prose with embedded data\n- Include quantitative parameters inline\n- Cite study types and sample sizes\n- Avoid excessive tables\n- Focus on mechanisms and evidence quality"
        }
        system_prompt = mode_prompts.get(user_mode, mode_prompts["patient"])
        
        # Build the full prompt
        if context:
            user_content = f"Context:\n{context}\n\nQuestion: {user_query}"
        else:
            user_content = user_query
        
        try:
            # Run synchronous Groq API call in thread pool (SDK is not async)
            # The compound model automatically has tools enabled
            loop = asyncio.get_event_loop()
            completion = await loop.run_in_executor(
                None,  # Use default executor
                partial(
                    self.client.chat.completions.create,
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_content}
                    ],
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
        question: str = ""  # Added for compatibility
    ) -> str:
        """
        Generate a patient-friendly summary from technical information
        Written at 6th grade reading level for general public
        
        Args:
            technical_info: Technical drug information
            drug_name: Name of the drug
            question: Optional user question for context
            
        Returns:
            Plain-language summary at 6th grade reading level
        """
        if not self.client:
            return ""
        
        prompt = f"""Create a brief, patient-friendly summary of this information.

CRITICAL REQUIREMENTS:
- Write at a 6th grade reading level
- Use short sentences (10-15 words maximum)
- Use simple, everyday words (avoid medical jargon)
- Focus on practical information patients need
- Make it easy to understand and remember

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Information:
{technical_info}

Provide a clear, concise summary in 2-4 short sentences that anyone can understand."""

        result = await self.generate_response(
            query=prompt,
            user_mode="patient",
            max_tokens=500,
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
