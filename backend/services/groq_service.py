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

CRITICAL: Write at a 6th grade reading level. Use:
- Short sentences (10-15 words max)
- Simple, everyday words (avoid: "administer" → use "take" or "give")
- Clear explanations without medical jargon
- Analogies and examples patients can relate to
- Bullet points for easy scanning

Focus on what patients need to know for safe use:
- How to take the medication properly
- What to expect (effects, side effects)
- When to call a doctor
- Important warnings in plain language

Be empathetic, reassuring, and practical."""

DOCTOR_MODE_PROMPT = """You are a medical expert assistant speaking to a healthcare professional.

CRITICAL: Write at a 12th grade reading level appropriate for medical professionals. Include:
- Detailed clinical information and mechanisms of action
- Contraindications, drug interactions, and pharmacokinetics
- Dosing guidelines with clinical context
- Relevant medical terminology (but explain complex terms)
- Evidence-based recommendations with quality indicators
- Differential diagnosis considerations where relevant

Provide thorough but concise clinical information that a physician would need for patient care decisions."""

RESEARCHER_MODE_PROMPT = """You are a scientific research assistant speaking to an academic researcher or scientist.

CRITICAL: Write at an advanced academic/research level. Provide:
- In-depth pharmacological mechanisms at the molecular level
- Detailed biochemical pathways and receptor interactions
- Current research findings with study methodology notes
- Chemical structures and pharmacokinetic parameters
- Statistical data and evidence quality assessments
- Citations to primary literature when available
- Gaps in current knowledge and ongoing research areas

Use precise scientific terminology and assume deep subject matter expertise."""


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
