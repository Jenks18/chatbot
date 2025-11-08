"""
Model Service - Using Groq SDK with Compound Model
"""
import os

# Only print in local development
if os.getenv('VERCEL') != '1':
    print("[Model Service] Using Groq SDK (groq/compound with tools)")

from .groq_service import groq_service as model_service

# Export the active model service
__all__ = ["model_service"]
