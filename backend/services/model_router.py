"""
Model Service Router
Switches between Groq and DeepSeek based on MODEL_PROVIDER environment variable
"""
import os
from typing import Optional

MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "groq").lower()

if MODEL_PROVIDER == "deepseek":
    print("[Model Router] Using DeepSeek API")
    from services.deepseek_service import deepseek_service as model_service
else:
    print("[Model Router] Using Groq API (default)")
    from services.groq_model_service import model_service

# Export the active model service
__all__ = ["model_service"]
