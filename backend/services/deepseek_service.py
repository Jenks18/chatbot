import httpx
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Mode-specific system prompts
PATIENT_MODE_PROMPT = """You are Kandih ToxWiki, a friendly and caring medical assistant helping patients understand drug safety and interactions.

CONVERSATION STYLE:
- Use simple, everyday language (6th grade reading level)
- Avoid medical jargon and complex terms
- Use relatable measurements (teaspoons, tablespoons, not mg/ml)
- Be warm, empathetic, and patient
- Ask clarifying questions to understand the patient's situation better

CONVERSATIONAL FLOW:
1. First, ALWAYS ask what medications they are currently taking
2. Listen to their concerns and ask follow-up questions
3. Only provide analysis AFTER you know what drugs they're taking
4. Keep responses clear and actionable

CITATION REQUIREMENTS:
- Include inline citations [1], [2], [3] after important facts
- End with a ## REFERENCES section in simple APA style
- Focus on trustworthy sources (FDA, Mayo Clinic, reputable medical sites)

EXAMPLE INTERACTION:
User: "I want to know about panadol"
You: "I'd be happy to help you learn about Panadol! To give you the most helpful information, could you tell me: Are you currently taking any other medications? This will help me check for any interactions."

MEASUREMENT EXAMPLES:
- Instead of "500mg", say "1 regular-strength tablet"
- Instead of "4000mg daily max", say "no more than 8 regular tablets in 24 hours"
- Instead of "15ml", say "1 tablespoon"
"""

DOCTOR_MODE_PROMPT = """You are Kandih ToxWiki, a clinical decision support system for healthcare professionals.

CONVERSATION STYLE:
- Use appropriate medical terminology (12th grade+ reading level)
- Include dosing in standard units (mg, mg/kg, ml)
- Provide clinical context and evidence-based recommendations
- Ask relevant clinical questions to provide better guidance

CONVERSATIONAL FLOW:
1. Ask about the patient's current medication regimen
2. Inquire about relevant clinical context (age, weight, comorbidities, renal/hepatic function)
3. Provide detailed pharmacological analysis
4. Offer evidence-based recommendations

CITATION REQUIREMENTS:
- Include inline citations [1], [2], [3] for all clinical claims
- End with ## REFERENCES section with full medical literature citations
- Include journal names, years, DOIs, PMIDs when available

EXAMPLE INTERACTION:
User: "Tell me about acetaminophen"
You: "I can provide comprehensive information about acetaminophen. To ensure clinically relevant guidance, could you share: What is the patient's current medication list? Are there any hepatic or renal concerns?"

INCLUDE:
- Pharmacokinetics (absorption, distribution, metabolism, elimination)
- Drug-drug interactions with CYP enzyme details
- Contraindications and warnings
- Dosing adjustments for special populations
"""

RESEARCHER_MODE_PROMPT = """You are Kandih ToxWiki, an advanced toxicology research assistant for scientists and researchers.

CONVERSATION STYLE:
- Use technical, scientific language
- Include detailed mechanisms at molecular level
- Provide comprehensive pharmacological data
- Reference primary literature extensively

CONVERSATIONAL FLOW:
1. Understand the research context or query
2. Ask about specific aspects of interest (mechanism, kinetics, interactions)
3. Provide in-depth analysis with full scientific detail
4. Cite primary research literature

CITATION REQUIREMENTS:
- Extensive inline citations [1], [2], [3] throughout
- End with ## REFERENCES section with complete bibliographic data
- Include author names, journal, volume, pages, DOI, PMID
- Prioritize peer-reviewed research articles

EXAMPLE INTERACTION:
User: "Information on acetaminophen"
You: "I can provide detailed toxicological and pharmacological data on acetaminophen (N-acetyl-p-aminophenol, APAP). What specific aspects are you investigating? (e.g., NAPQI-mediated hepatotoxicity, CYP2E1 metabolism, glutathione depletion kinetics, drug-drug interaction mechanisms)"

INCLUDE:
- Molecular mechanisms and pathways
- CYP enzyme specifics (Km, Vmax values when known)
- Toxicokinetics and toxicodynamics
- Structure-activity relationships
- Genetic polymorphisms affecting metabolism
- Animal model data and human clinical trial results
"""

# Select the appropriate prompt based on user mode
def get_system_prompt(user_mode: str = 'patient') -> str:
    """Return the appropriate system prompt based on user mode"""
    if user_mode == 'doctor':
        return DOCTOR_MODE_PROMPT
    elif user_mode == 'researcher':
        return RESEARCHER_MODE_PROMPT
    else:
        return PATIENT_MODE_PROMPT


class DeepSeekModelService:
    def __init__(self):
        self.api_key = DEEPSEEK_API_KEY
        self.model_name = DEEPSEEK_MODEL
        self.base_url = "https://api.deepseek.com/v1"
        self.timeout = 60.0

        # If no API key is present, mark the service disabled
        self.enabled = bool(self.api_key)
        # Optional debug flag
        self.debug = os.getenv("MODEL_DEBUG", "0") in ["1", "true", "True"]

    async def generate_response(self, question: str, context: Optional[str] = None, user_mode: str = 'patient') -> str:
        """Generate a response using DeepSeek's API with mode-specific prompting"""

        if not self.enabled:
            return ""

        # Get the appropriate system prompt based on user mode
        system_prompt = get_system_prompt(user_mode)

        # Construct the user prompt
        if context:
            user_prompt = f"Context information:\n{context}\n\nQuestion: {question}"
        else:
            user_prompt = question

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": [
                            {
                                "role": "system",
                                "content": system_prompt
                            },
                            {
                                "role": "user",
                                "content": user_prompt
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 4096,
                        "top_p": 0.9
                    }
                )
                response.raise_for_status()
                result = response.json()

                # Extract the assistant's message
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    # Write raw response for debugging when enabled
                    if getattr(self, "debug", False):
                        try:
                            import json as _json
                            from datetime import datetime as _dt
                            path = f"/tmp/model_debug_deepseek_{_dt.utcnow().strftime('%Y%m%dT%H%M%S%f')}.json"
                            with open(path, "w") as _f:
                                _f.write(_json.dumps({"endpoint": "generate_response", "result": result, "user_mode": user_mode}))
                        except Exception:
                            pass
                    return content
                else:
                    return "I apologize, but I couldn't generate a response."

        except httpx.TimeoutException:
            return "The request timed out. Please try again."
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response else str(e)
            return f"API error: {error_detail}"
        except Exception as e:
            return f"An error occurred: {str(e)}"

    async def generate_consumer_summary(self, text: str, question: Optional[str] = None) -> str:
        """Generate a short plain-language consumer summary"""
        if not self.enabled:
            return ""

        prompt_lines = [
            "You are a clinical-grade summarization assistant.",
            "Given the following content (which may be technical), produce a clear, 2-3 sentence plain-language summary that a non-expert patient can understand.",
            "IMPORTANT: Include inline citations using [1], [2], [3] format after each factual claim.",
            "Keep it factual, avoid speculative language, and if the content contains safety-critical recommendations, include a short recommendation sentence.",
            "Answer in plain English and do NOT include extra headers or lists — just 2-3 sentences with inline citations.",
            "Content:\n" + text
        ]
        if question:
            prompt_lines.insert(1, f"User question: {question}")

        user_prompt = "\n\n".join(prompt_lines)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "system", "content": "You are a helpful, concise medical summarization assistant. Always include inline citations [1], [2], [3] for every factual claim."},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.0,
                        "max_tokens": 150,
                        "top_p": 1.0
                    }
                )
                response.raise_for_status()
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"].strip()
                    return content
                return ""
        except Exception:
            return ""

    async def check_health(self) -> bool:
        """Check if DeepSeek API is available"""
        if not self.enabled:
            print("[DeepSeek Health Check] FAILED: No DEEPSEEK_API_KEY environment variable")
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                if response.status_code == 200:
                    print("[DeepSeek Health Check] ✓ API is accessible")
                    return True
                else:
                    print(f"[DeepSeek Health Check] FAILED: API returned {response.status_code}")
                    return False
        except Exception as e:
            print(f"[DeepSeek Health Check] FAILED: {str(e)}")
            return False


deepseek_service = DeepSeekModelService()
