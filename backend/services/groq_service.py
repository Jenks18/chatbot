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

# Load .env from backend directory
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / '.env'
load_dotenv(dotenv_path=env_path)

# Mode-specific prompts
PATIENT_MODE_PROMPT = """You are a helpful medical assistant speaking to a patient. 
Provide clear, simple explanations without medical jargon. Be empathetic and reassuring.
When discussing drug information, focus on what patients need to know for safe use."""

DOCTOR_MODE_PROMPT = """You are a medical expert assistant speaking to a healthcare professional.
Provide detailed clinical information, mechanisms of action, contraindications, and drug interactions.
Include relevant medical terminology and cite evidence when available."""

RESEARCHER_MODE_PROMPT = """You are a scientific research assistant speaking to a researcher.
Provide in-depth pharmacological information, mechanisms at molecular level, research findings,
and detailed chemical/biological pathways. Include citations and evidence quality assessments."""


class GroqModelService:
    """Service for interacting with Groq API using compound model with tools"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = "groq/compound"
        
        if not self.api_key:
            print("⚠️  WARNING: GROQ_API_KEY not set")
            self.client = None
        else:
            self.client = Groq(
                api_key=self.api_key,
                default_headers={
                    "Groq-Model-Version": "latest"
                }
            )
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
            # Prepare compound_custom for tools
            compound_config = {}
            if enable_tools:
                compound_config = {
                    "tools": {
                        "enabled_tools": ["web_search", "code_interpreter", "visit_website"]
                    }
                }
            
            # Run synchronous Groq API call in thread pool (SDK is not async)
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
                    max_completion_tokens=max_tokens,
                    top_p=1,
                    stream=True,
                    stop=None,
                    compound_custom=compound_config if compound_config else None
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
        
        Args:
            technical_info: Technical drug information
            drug_name: Name of the drug
            question: Optional user question for context
            
        Returns:
            Plain-language summary
        """
        if not self.client:
            return ""
        
        prompt = f"""Create a brief, patient-friendly summary of this information.
Use simple language and focus on what patients need to know.

{f'Question: {question}' if question else ''}
{f'Drug: {drug_name}' if drug_name else ''}

Information:
{technical_info}

Provide a clear, concise summary in 2-3 sentences."""

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
                    max_completion_tokens=200,
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
                    max_completion_tokens=5,
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
