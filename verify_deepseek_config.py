#!/usr/bin/env python3
"""
DeepSeek Configuration Verification Script
Tests that all model configuration is correct for DeepSeek (not Groq)
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def check_env_file():
    """Check .env file for correct configuration"""
    print("=" * 60)
    print("1. Checking backend/.env file...")
    print("=" * 60)
    
    env_path = backend_dir / ".env"
    if not env_path.exists():
        print("❌ backend/.env file not found!")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Check for Groq references (should NOT exist)
    if "GROQ" in content or "groq" in content:
        print("❌ FOUND GROQ references in .env file!")
        print("   Lines containing 'groq':")
        for i, line in enumerate(content.split('\n'), 1):
            if 'groq' in line.lower():
                print(f"   Line {i}: {line}")
        return False
    
    # Check for DeepSeek (should exist)
    if "DEEPSEEK_API_KEY" not in content:
        print("❌ DEEPSEEK_API_KEY not found in .env file!")
        return False
    
    print("✅ .env file is clean - no Groq references")
    print("✅ DEEPSEEK_API_KEY is present")
    return True

def check_model_router():
    """Check model_router.py for correct imports"""
    print("\n" + "=" * 60)
    print("2. Checking backend/services/model_router.py...")
    print("=" * 60)
    
    router_path = backend_dir / "services" / "model_router.py"
    if not router_path.exists():
        print("❌ model_router.py not found!")
        return False
    
    with open(router_path, 'r') as f:
        content = f.read()
    
    # Check for Groq imports (should NOT exist)
    if "groq_model_service" in content:
        print("❌ FOUND import from groq_model_service!")
        return False
    
    # Check for DeepSeek import (should exist)
    if "deepseek_service" not in content:
        print("❌ DeepSeek import not found!")
        return False
    
    print("✅ model_router.py correctly imports deepseek_service")
    print("✅ No groq_model_service imports found")
    return True

def check_groq_files_deleted():
    """Check that Groq files are deleted"""
    print("\n" + "=" * 60)
    print("3. Checking for deleted Groq files...")
    print("=" * 60)
    
    groq_file = backend_dir / "services" / "groq_model_service.py"
    if groq_file.exists():
        print("❌ groq_model_service.py still exists!")
        return False
    
    print("✅ groq_model_service.py is deleted")
    return True

def check_deepseek_service():
    """Check DeepSeek service configuration"""
    print("\n" + "=" * 60)
    print("4. Checking DeepSeek service configuration...")
    print("=" * 60)
    
    deepseek_file = backend_dir / "services" / "deepseek_service.py"
    if not deepseek_file.exists():
        print("❌ deepseek_service.py not found!")
        return False
    
    with open(deepseek_file, 'r') as f:
        content = f.read()
    
    # Check for correct API endpoint
    if "https://api.deepseek.com/v1" not in content:
        print("❌ DeepSeek API endpoint not found!")
        return False
    
    # Check for model name
    if "deepseek-chat" not in content:
        print("❌ deepseek-chat model not found!")
        return False
    
    # Check for health check method
    if "async def check_health" not in content:
        print("❌ check_health method not found!")
        return False
    
    # Check for generate_response method
    if "async def generate_response" not in content:
        print("❌ generate_response method not found!")
        return False
    
    print("✅ DeepSeek API endpoint: https://api.deepseek.com/v1")
    print("✅ Model: deepseek-chat")
    print("✅ check_health() method exists")
    print("✅ generate_response() method exists")
    return True

def check_imports():
    """Check that all files import from model_router"""
    print("\n" + "=" * 60)
    print("5. Checking imports in backend files...")
    print("=" * 60)
    
    # Check main.py
    main_file = backend_dir / "main.py"
    with open(main_file, 'r') as f:
        content = f.read()
    
    if "from services.model_router import model_service" not in content:
        print("❌ main.py doesn't import from model_router!")
        return False
    
    print("✅ main.py imports from model_router")
    
    # Check chat.py
    chat_file = backend_dir / "routers" / "chat.py"
    with open(chat_file, 'r') as f:
        content = f.read()
    
    if "from services.model_router import model_service" not in content:
        print("❌ chat.py doesn't import from model_router!")
        return False
    
    if "groq" in content.lower():
        print("❌ Found 'groq' reference in chat.py!")
        return False
    
    print("✅ chat.py imports from model_router")
    print("✅ No groq references in chat.py")
    return True

def main():
    """Run all checks"""
    print("\n🔍 DeepSeek Configuration Verification")
    print("=" * 60)
    
    checks = [
        check_env_file(),
        check_model_router(),
        check_groq_files_deleted(),
        check_deepseek_service(),
        check_imports()
    ]
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION RESULTS")
    print("=" * 60)
    
    if all(checks):
        print("✅ ALL CHECKS PASSED!")
        print("\n✨ Configuration is correct for DeepSeek")
        print("\n⚠️  REMINDER: Add environment variables to Vercel:")
        print("   - DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d")
        print("   - DEEPSEEK_MODEL=deepseek-chat")
        print("   Then redeploy to fix 'degraded' status")
        return 0
    else:
        print(f"❌ {sum(not c for c in checks)} CHECK(S) FAILED!")
        print("\n⚠️  Fix the issues above before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())
