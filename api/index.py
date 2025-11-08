"""
Vercel serverless function entry point for FastAPI backend
"""
import sys
import os
import traceback

# Add backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from backend.main import app
    print("✅ Successfully imported backend.main.app")
except Exception as e:
    print(f"❌ FATAL ERROR importing backend.main:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print(f"Full traceback:")
    traceback.print_exc()
    raise

# Vercel expects the app to be available at module level
handler = app
