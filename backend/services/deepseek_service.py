import httpx
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

# Mode-specific system prompts (imported from groq_model_service)
from services.groq_model_service import (
    PATIENT_MODE_PROMPT,
    DOCTOR_MODE_PROMPT,
    RESEARCHER_MODE_PROMPT,
    get_system_prompt
)


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
            return False
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                return response.status_code == 200
        except:
            return False


deepseek_service = DeepSeekModelService()
