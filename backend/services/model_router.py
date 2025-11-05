"""
Model Service - Using Groq API with Llama 3.3 70B
"""
print("[Model Service] Using Groq API (llama-3.3-70b-versatile)")
from services.groq_service import groq_service as model_service

# Export the active model service
__all__ = ["model_service"]
