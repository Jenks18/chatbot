#!/usr/bin/env python3
"""
Quick test script for Groq API integration
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from services.groq_service import groq_service
import asyncio

async def test_groq():
    print("🧪 Testing Groq Compound Model Integration")
    print("=" * 60)
    
    # Test 1: Check initialization
    print(f"\n✓ Model Name: {groq_service.model_name}")
    print(f"✓ API Key Set: {groq_service.api_key is not None}")
    print(f"✓ Client Initialized: {groq_service.client is not None}")
    
    # Test 2: Health check
    print("\n📡 Testing health check...")
    try:
        health = await groq_service.check_health()
        print(f"✓ Health Status: {health}")
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return
    
    # Test 3: Generate response
    print("\n💬 Testing response generation...")
    try:
        query = "What is aspirin and how does it work?"
        context = "Drug information query"
        
        print(f"Query: {query}")
        print("Generating response...")
        
        response = await groq_service.generate_response(
            query=query,
            context=context,
            user_mode="patient",
            enable_tools=True
        )
        
        content = response.get("content", "")
        print(f"\n✓ Response received ({len(content)} characters)")
        print(f"\nResponse preview (first 500 chars):")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)
        
        if len(content) > 500:
            print(f"\n... (truncated, full response is {len(content)} characters)")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Response generation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_groq())
