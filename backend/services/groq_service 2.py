"""
Groq Model Service - Using Compound Model with Official SDK
Provides AI responses using Groq's compound model with tools (web_search, code_interpreter, visit_website)
"""
from groq import Groq
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from pathlib import Path

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
        query: str,
        context: str = "",
        user_mode: str = "patient",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        enable_tools: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a response using Groq compound model
        
        Args:
            query: User's question
            context: Additional context (drug data, etc.)
            user_mode: 'patient', 'doctor', or 'researcher'
            max_tokens: Maximum response length
            temperature: Response creativity (0-1)
            enable_tools: Enable web_search, code_interpreter, visit_website
            
        Returns:
            Dict with 'content' and metadata
        """
        if not self.client:
            return {
                "content": "Error: GROQ_API_KEY not configured. Get your free key at https://console.groq.com/keys",
                "error": "missing_api_key"
            }
        
        # Select system prompt based on mode
        mode_prompts = {
            "patient": PATIENT_MODE_PROMPT,
            "doctor": DOCTOR_MODE_PROMPT,
            "researcher": RESEARCHER_MODE_PROMPT
        }
        system_prompt = mode_prompts.get(user_mode, PATIENT_MODE_PROMPT)
        
        # Build the full prompt
        if context:
            user_content = f"Context:\n{context}\n\nQuestion: {query}"
        else:
            user_content = query
        
        try:
            # Prepare compound_custom for tools
            compound_config = {}
            if enable_tools:
                compound_config = {
                    "tools": {
                        "enabled_tools": ["web_search", "code_interpreter", "visit_website"]
                    }
                }
            
            # Make the API call (streaming)
            completion = self.client.chat.completions.create(
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
            
            # Collect streamed response
            full_content = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_content += chunk.choices[0].delta.content
            
            return {
                "content": full_content,
                "model": self.model_name,
                "tools_enabled": enable_tools
            }
                    
        except Exception as e:
            error_msg = str(e)
            return {
                "content": f"API error: {error_msg}",
                "error": "exception",
                "exception": error_msg
            }
    
    async def generate_consumer_summary(
        self,
        technical_info: str,
        drug_name: str = ""
    ) -> str:
        """
        Generate a patient-friendly summary from technical information
        
        Args:
            technical_info: Technical drug information
            drug_name: Name of the drug
            
        Returns:
            Plain-language summary
        """
        prompt = f"""Create a brief, patient-friendly summary of this drug information.
Use simple language and focus on what patients need to know.

Drug: {drug_name}

Technical Information:
{technical_info}

Provide a clear, concise summary in 2-3 paragraphs."""

        result = await self.generate_response(
            query=prompt,
            user_mode="patient",
            max_tokens=500,
            temperature=0.5,
            enable_tools=False  # Don't need tools for summaries
        )
        
        return result.get("content", "")
    
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
            # Simple test request
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "test"}],
                max_completion_tokens=5,
                stream=False
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

import httpx
import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

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
    """Service for interacting with Groq API using compound model"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        self.base_url = "https://api.groq.com/openai/v1"
        
        if not self.api_key:
            print("⚠️  WARNING: GROQ_API_KEY not set")
        else:
            print(f"✅ Groq API initialized: {self.model_name}")
    
    async def generate_response(
        self,
        query: str,
        context: str = "",
        user_mode: str = "patient",
        max_tokens: int = 2000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Generate a response using Groq compound model
        
        Args:
            query: User's question
            context: Additional context (drug data, etc.)
            user_mode: 'patient', 'doctor', or 'researcher'
            max_tokens: Maximum response length
            temperature: Response creativity (0-1)
            
        Returns:
            Dict with 'content' and metadata
        """
        if not self.api_key:
            return {
                "content": "Error: GROQ_API_KEY not configured",
                "error": "missing_api_key"
            }
        
        # Select system prompt based on mode
        mode_prompts = {
            "patient": PATIENT_MODE_PROMPT,
            "doctor": DOCTOR_MODE_PROMPT,
            "researcher": RESEARCHER_MODE_PROMPT
        }
        system_prompt = mode_prompts.get(user_mode, PATIENT_MODE_PROMPT)
        
        # Build the full prompt
        if context:
            full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nQuestion: {query}"
        else:
            full_prompt = f"{system_prompt}\n\nQuestion: {query}"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": full_prompt}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "content": data["choices"][0]["message"]["content"],
                        "model": self.model_name,
                        "usage": data.get("usage", {})
                    }
                else:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("error", {}).get("message", error_detail)
                    except:
                        pass
                    
                    return {
                        "content": f"API error: {error_detail}",
                        "error": f"http_{response.status_code}",
                        "status_code": response.status_code
                    }
                    
        except httpx.TimeoutException:
            return {
                "content": "Request timed out. Please try again.",
                "error": "timeout"
            }
        except Exception as e:
            return {
                "content": f"Error: {str(e)}",
                "error": "exception",
                "exception": str(e)
            }
    
    async def generate_consumer_summary(
        self,
        technical_info: str,
        drug_name: str = ""
    ) -> str:
        """
        Generate a patient-friendly summary from technical information
        
        Args:
            technical_info: Technical drug information
            drug_name: Name of the drug
            
        Returns:
            Plain-language summary
        """
        prompt = f"""Create a brief, patient-friendly summary of this drug information.
Use simple language and focus on what patients need to know.

Drug: {drug_name}

Technical Information:
{technical_info}

Provide a clear, concise summary in 2-3 paragraphs."""

        result = await self.generate_response(
            query=prompt,
            user_mode="patient",
            max_tokens=500,
            temperature=0.5
        )
        
        return result.get("content", "")
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check if Groq API is accessible
        
        Returns:
            Dict with health status
        """
        if not self.api_key:
            return {
                "status": "unhealthy",
                "error": "GROQ_API_KEY not configured",
                "details": "Set GROQ_API_KEY in environment variables"
            }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 5
                    }
                )
                
                if response.status_code == 200:
                    print("[Groq Health Check] ✓ API is accessible")
                    return {
                        "status": "healthy",
                        "model": self.model_name,
                        "endpoint": self.base_url
                    }
                else:
                    error_msg = f"HTTP {response.status_code}"
                    try:
                        error_json = response.json()
                        error_msg = error_json.get("error", {}).get("message", error_msg)
                    except:
                        pass
                    
                    print(f"[Groq Health Check] ✗ API error: {error_msg}")
                    return {
                        "status": "unhealthy",
                        "error": error_msg,
                        "status_code": response.status_code
                    }
                    
        except Exception as e:
            print(f"[Groq Health Check] ✗ Connection failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "details": "Cannot connect to Groq API"
            }


# Create singleton instance
groq_service = GroqModelService()
