"""
Vercel serverless function entry point for FastAPI backend
"""
import sys
import os

# Add backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Suppress startup logs in serverless environment
os.environ['VERCEL'] = '1'

# Import the FastAPI app
from backend.main import app

# Vercel expects the handler at module level
handler = app

