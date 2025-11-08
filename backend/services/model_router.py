"""
Model Service - Using Groq SDK with Compound Model
"""
print("[Model Service] Using Groq SDK (groq/compound with tools)")
from .groq_service import groq_service as model_service

# Export the active model service
__all__ = ["model_service"]
