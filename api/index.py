"""
Vercel serverless function entry point for FastAPI backend
"""
import sys
import os
import traceback
import json

# Add backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Suppress startup logs in serverless environment
os.environ['VERCEL'] = '1'

# Try to import and wrap in error handler
try:
    from backend.main import app
    handler = app
except Exception as e:
    # If import fails, create a minimal error handler
    print(f"ERROR importing backend.main: {e}")
    traceback.print_exc()
    
    # Create a minimal WSGI handler that returns the error
    class ErrorHandler:
        def __call__(self, scope, receive, send):
            if scope['type'] == 'http':
                import asyncio
                return asyncio.ensure_future(self.handle_http(scope, receive, send))
        
        async def handle_http(self, scope, receive, send):
            await send({
                'type': 'http.response.start',
                'status': 500,
                'headers': [[b'content-type', b'application/json']],
            })
            error_response = {
                "error": "Failed to initialize backend",
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            await send({
                'type': 'http.response.body',
                'body': json.dumps(error_response).encode(),
            })
    
    handler = ErrorHandler()

