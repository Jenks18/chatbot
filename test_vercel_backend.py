#!/usr/bin/env python3
"""
Test script to verify Vercel deployment structure
Checks file structure and configuration without importing packages
"""
import json
import os
from pathlib import Path

print("=" * 60)
print("🔍 Testing Vercel Backend Configuration")
print("=" * 60)

root = Path(__file__).parent
errors = []
warnings = []

# Test 1: Check api/index.py exists
print("\n1. Checking api/index.py...")
api_file = root / "api" / "index.py"
if api_file.exists():
    content = api_file.read_text()
    if "from backend.main import app" in content:
        print("   ✅ api/index.py exists and imports FastAPI app")
    else:
        errors.append("api/index.py doesn't import backend.main.app")
        print("   ❌ api/index.py doesn't import backend.main.app")
    
    if "handler = app" in content:
        print("   ✅ Handler is exported correctly")
    else:
        errors.append("api/index.py doesn't export handler")
        print("   ❌ Handler not exported")
else:
    errors.append("api/index.py not found")
    print("   ❌ api/index.py not found!")

# Test 2: Check requirements.txt at root
print("\n2. Checking requirements.txt...")
req_file = root / "requirements.txt"
if req_file.exists():
    packages = req_file.read_text().strip().split('\n')
    packages = [p.strip() for p in packages if p.strip() and not p.startswith('#')]
    
    print(f"   ✅ requirements.txt exists ({len(packages)} packages)")
    
    required = {
        'fastapi': False,
        'sqlalchemy': False,
        'httpx': False,
        'psycopg2-binary': False,
        'python-dotenv': False
    }
    
    for pkg in packages:
        pkg_name = pkg.split('==')[0].strip()
        for req in required.keys():
            if req in pkg_name.lower():
                required[req] = True
    
    for pkg, found in required.items():
        if found:
            print(f"      ✅ {pkg}")
        else:
            errors.append(f"{pkg} not in requirements.txt")
            print(f"      ❌ {pkg} MISSING!")
else:
    errors.append("requirements.txt not found")
    print("   ❌ requirements.txt not found!")

# Test 3: Check vercel.json
print("\n3. Checking vercel.json...")
vercel_file = root / "vercel.json"
if vercel_file.exists():
    config = json.loads(vercel_file.read_text())
    print(f"   ✅ vercel.json exists")
    
    # Check for Python build
    if 'builds' in config:
        python_build = any('@vercel/python' in str(b.get('use', '')) for b in config['builds'])
        if python_build:
            print(f"      ✅ Python build configured")
        else:
            warnings.append("No @vercel/python build found")
            print(f"      ⚠️  No @vercel/python build")
    
    # Check routes
    if 'routes' in config:
        api_route = any('/api' in str(r.get('src', '')) for r in config['routes'])
        if api_route:
            print(f"      ✅ API routes configured")
        else:
            errors.append("No /api route in vercel.json")
            print(f"      ❌ No /api route")
else:
    errors.append("vercel.json not found")
    print("   ❌ vercel.json not found!")

# Test 4: Check backend structure
print("\n4. Checking backend structure...")
backend_dir = root / "backend"
if backend_dir.exists():
    print(f"   ✅ backend/ directory exists")
    
    # Check main.py
    main_file = backend_dir / "main.py"
    if main_file.exists():
        content = main_file.read_text()
        if "FastAPI" in content:
            print(f"      ✅ backend/main.py has FastAPI app")
        if "model_router" in content:
            print(f"      ✅ backend/main.py imports model_router")
        else:
            errors.append("main.py doesn't import model_router")
            print(f"      ❌ main.py doesn't import model_router")
    else:
        errors.append("backend/main.py not found")
        print(f"      ❌ backend/main.py not found!")
    
    # Check services
    services_dir = backend_dir / "services"
    if services_dir.exists():
        files = list(services_dir.glob("*.py"))
        print(f"      ✅ backend/services/ ({len(files)} files)")
        
        # Check for model_router.py
        if (services_dir / "model_router.py").exists():
            print(f"         ✅ model_router.py")
        else:
            errors.append("model_router.py not found")
            print(f"         ❌ model_router.py MISSING!")
        
        # Check for deepseek_service.py
        if (services_dir / "deepseek_service.py").exists():
            content = (services_dir / "deepseek_service.py").read_text()
            if "api.deepseek.com" in content:
                print(f"         ✅ deepseek_service.py (DeepSeek API configured)")
            else:
                warnings.append("DeepSeek API endpoint not found")
                print(f"         ⚠️  deepseek_service.py (API endpoint unclear)")
        else:
            errors.append("deepseek_service.py not found")
            print(f"         ❌ deepseek_service.py MISSING!")
        
        # Check for Groq files (should NOT exist)
        if (services_dir / "groq_model_service.py").exists():
            errors.append("groq_model_service.py still exists!")
            print(f"         ❌ groq_model_service.py SHOULD BE DELETED!")
        else:
            print(f"         ✅ No Groq files (correct)")
    else:
        errors.append("backend/services/ not found")
        print(f"      ❌ backend/services/ not found!")
else:
    errors.append("backend/ directory not found")
    print(f"   ❌ backend/ directory not found!")

# Test 5: Check .env file structure
print("\n5. Checking .env file...")
env_file = backend_dir / ".env"
if env_file.exists():
    content = env_file.read_text()
    print(f"   ✅ backend/.env exists")
    
    if "DEEPSEEK_API_KEY" in content:
        print(f"      ✅ DEEPSEEK_API_KEY present")
    else:
        warnings.append("DEEPSEEK_API_KEY not in .env")
        print(f"      ⚠️  DEEPSEEK_API_KEY not found")
    
    if "GROQ" in content or "groq" in content:
        warnings.append("Groq references in .env file")
        print(f"      ⚠️  Groq references found (should be removed)")
    else:
        print(f"      ✅ No Groq references")
else:
    warnings.append("backend/.env not found (will use Vercel env vars)")
    print(f"   ⚠️  backend/.env not found (OK for Vercel, uses env vars)")

# Summary
print("\n" + "=" * 60)
print("📊 VERIFICATION RESULTS")
print("=" * 60)

if errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for error in errors:
        print(f"   - {error}")
    print("\n⚠️  FIX THESE BEFORE DEPLOYING TO VERCEL!")
    exit(1)
elif warnings:
    print(f"\n⚠️  {len(warnings)} WARNING(S):")
    for warning in warnings:
        print(f"   - {warning}")
    print("\n✅ Structure is OK, but review warnings")
else:
    print("\n✅ ALL CHECKS PASSED!")

print("\n" + "=" * 60)
print("� VERCEL DEPLOYMENT CHECKLIST")
print("=" * 60)
print("\n1. ✅ File structure is correct")
print("2. ⚠️  Add environment variables to Vercel:")
print("      - DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d")
print("      - DEEPSEEK_MODEL=deepseek-chat")
print("      - DATABASE_URL=postgresql://...")
print("      - NEXT_PUBLIC_SUPABASE_URL=https://...")
print("      - NEXT_PUBLIC_SUPABASE_ANON_KEY=...")
print("      - OPENFDA_API_KEY=...")
print("      - NCBI_API_KEY=...")
print("      - API_CACHE_DURATION_DAYS=30")
print("      - ENABLE_API_CACHING=true")
print("\n3. ⚠️  Redeploy after adding environment variables")
print("\n4. ✅ Backend will be available at: https://your-app.vercel.app/api/*")
print("\n" + "=" * 60)
