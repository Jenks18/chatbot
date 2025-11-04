"""
Vercel serverless function entry point for FastAPI backend
"""
import sys
import os

# Add backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.main import app

# Vercel expects the app to be available at module level
handler = app
