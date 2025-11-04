"""
Model Service - Using DeepSeek API
"""
print("[Model Service] Using DeepSeek API")
from services.deepseek_service import deepseek_service as model_service

# Export the active model service
__all__ = ["model_service"]
