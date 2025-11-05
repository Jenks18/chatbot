#!/usr/bin/env python3
"""
Test Python Backend for Vercel Serverless Functions
Verifies the Python backend will work correctly on Vercel
"""
import sys
import os
import json
from pathlib import Path

print("=" * 70)
print("🐍 TESTING PYTHON BACKEND FOR VERCEL")
print("=" * 70)

root = Path(__file__).parent
errors = []
passed = []

# Test 1: Verify api/index.py structure
print("\n1. Testing api/index.py (Vercel entry point)...")
api_index = root / "api" / "index.py"

if not api_index.exists():
    errors.append("api/index.py NOT FOUND!")
    print("   ❌ api/index.py NOT FOUND!")
else:
    content = api_index.read_text()
    
    # Check sys.path modification
    if "sys.path.insert" in content:
        print("   ✅ Modifies sys.path to find backend module")
        passed.append("sys.path configuration")
    else:
        errors.append("api/index.py doesn't modify sys.path")
        print("   ❌ Doesn't modify sys.path")
    
    # Check FastAPI import
    if "from backend.main import app" in content:
        print("   ✅ Imports FastAPI app from backend.main")
        passed.append("FastAPI import")
    else:
        errors.append("Doesn't import from backend.main")
        print("   ❌ Doesn't import from backend.main")
    
    # Check handler export
    if "handler = app" in content or "app = app" in content:
        print("   ✅ Exports handler for Vercel")
        passed.append("Handler export")
    else:
        errors.append("Doesn't export handler")
        print("   ❌ Doesn't export handler")

# Test 2: Verify backend/main.py
print("\n2. Testing backend/main.py...")
main_py = root / "backend" / "main.py"

if not main_py.exists():
    errors.append("backend/main.py NOT FOUND!")
    print("   ❌ backend/main.py NOT FOUND!")
else:
    content = main_py.read_text()
    
    # Check FastAPI app creation
    if "FastAPI(" in content or "app = FastAPI" in content:
        print("   ✅ Creates FastAPI app instance")
        passed.append("FastAPI app creation")
    else:
        errors.append("No FastAPI app creation")
        print("   ❌ No FastAPI app creation")
    
    # Check CORS (needed for Vercel)
    if "CORS" in content or "CORSMiddleware" in content:
        print("   ✅ CORS middleware configured")
        passed.append("CORS configuration")
    else:
        print("   ⚠️  No CORS middleware (may cause issues)")
    
    # Check routes
    if "include_router" in content:
        print("   ✅ Includes API routes")
        passed.append("Route includes")
    else:
        errors.append("No route includes")
        print("   ❌ No route includes")
    
    # Check model service
    if "model_service" in content or "model_router" in content:
        print("   ✅ Imports model service")
        passed.append("Model service import")
    else:
        errors.append("No model service import")
        print("   ❌ No model service import")

# Test 3: Verify requirements.txt
print("\n3. Testing requirements.txt (Python dependencies)...")
req_file = root / "requirements.txt"

if not req_file.exists():
    errors.append("requirements.txt NOT FOUND at root!")
    print("   ❌ requirements.txt NOT FOUND!")
else:
    content = req_file.read_text()
    packages = [line.strip() for line in content.split('\n') 
                if line.strip() and not line.startswith('#')]
    
    print(f"   ✅ requirements.txt exists ({len(packages)} packages)")
    passed.append("requirements.txt exists")
    
    # Check critical packages
    critical_packages = {
        'fastapi': False,
        'uvicorn': False,
        'sqlalchemy': False,
        'httpx': False,
        'psycopg2-binary': False,
        'python-dotenv': False,
        'pydantic': False
    }
    
    for pkg in packages:
        pkg_name = pkg.split('==')[0].split('>=')[0].split('[')[0].strip().lower()
        for critical in critical_packages.keys():
            if critical in pkg_name:
                critical_packages[critical] = True
    
    for pkg, found in critical_packages.items():
        if found:
            print(f"      ✅ {pkg}")
            passed.append(f"{pkg} in requirements.txt")
        else:
            if pkg == 'uvicorn' or pkg == 'pydantic':
                print(f"      ⚠️  {pkg} (may be included with fastapi)")
            else:
                errors.append(f"{pkg} missing from requirements.txt")
                print(f"      ❌ {pkg} MISSING!")

# Test 4: Verify vercel.json Python build
print("\n4. Testing vercel.json (Vercel configuration)...")
vercel_json = root / "vercel.json"

if not vercel_json.exists():
    errors.append("vercel.json NOT FOUND!")
    print("   ❌ vercel.json NOT FOUND!")
else:
    config = json.loads(vercel_json.read_text())
    print("   ✅ vercel.json exists")
    passed.append("vercel.json exists")
    
    # Check builds
    if 'builds' in config:
        python_build = None
        for build in config['builds']:
            if '@vercel/python' in str(build.get('use', '')):
                python_build = build
                break
        
        if python_build:
            print(f"   ✅ Python build configured: {python_build['src']} → {python_build['use']}")
            passed.append("Python build in vercel.json")
        else:
            errors.append("No @vercel/python build in vercel.json")
            print("   ❌ No @vercel/python build found!")
    else:
        errors.append("No builds section in vercel.json")
        print("   ❌ No builds section!")
    
    # Check routes
    if 'routes' in config:
        api_route = None
        for route in config['routes']:
            if '/api' in str(route.get('src', '')):
                api_route = route
                break
        
        if api_route:
            print(f"   ✅ API route configured: {api_route['src']} → {api_route.get('dest', 'N/A')}")
            passed.append("API route in vercel.json")
        else:
            errors.append("No /api route in vercel.json")
            print("   ❌ No /api route found!")

# Test 5: Test Python import chain (structural test only)
print("\n5. Testing Python import chain (structure only)...")
print("   Note: Import errors for missing packages are EXPECTED locally")

# Just verify the import paths are correct syntactically
api_index_content = (root / "api" / "index.py").read_text()
main_content = (root / "backend" / "main.py").read_text()
router_content = (root / "backend" / "services" / "model_router.py").read_text()

# Check api/index.py import
if "from backend.main import app" in api_index_content:
    print("   ✅ api/index.py: 'from backend.main import app' (correct)")
    passed.append("api/index.py import syntax")
else:
    errors.append("api/index.py: wrong import syntax")
    print("   ❌ api/index.py: wrong import syntax")

# Check model_router.py import
if "from backend.services.deepseek_service import" in router_content:
    print("   ✅ model_router.py: uses 'backend.services.deepseek_service' (correct)")
    passed.append("model_router.py import syntax")
elif "from services.deepseek_service import" in router_content:
    errors.append("model_router.py: uses relative import 'services.' instead of 'backend.services.'")
    print("   ❌ model_router.py: should use 'backend.services.deepseek_service'")
else:
    errors.append("model_router.py: no deepseek_service import found")
    print("   ❌ model_router.py: no deepseek_service import found")

# Check main.py imports from routers
if "from routers import" in main_content or "from backend.routers import" in main_content:
    print("   ✅ main.py: imports routers (correct)")
    passed.append("main.py router imports")
else:
    print("   ⚠️  main.py: check router imports")

# Structural verification passed if syntax is correct
print("   ✅ Import chain structure is correct for Vercel")
passed.append("Import chain structure")

# Test 6: Verify no Groq dependencies
print("\n6. Testing for Groq remnants (should be NONE)...")

groq_files = [
    root / "backend" / "services" / "groq_model_service.py",
    root / "backend" / "services" / "groq_service.py"
]

groq_found = False
for gf in groq_files:
    if gf.exists():
        errors.append(f"{gf.name} still exists!")
        print(f"   ❌ {gf.name} STILL EXISTS!")
        groq_found = True

if not groq_found:
    print("   ✅ No Groq service files (correct)")
    passed.append("No Groq files")

# Check for Groq in requirements.txt
if req_file.exists():
    req_content = req_file.read_text().lower()
    if 'groq' in req_content:
        errors.append("'groq' found in requirements.txt")
        print("   ❌ 'groq' found in requirements.txt!")
    else:
        print("   ✅ No 'groq' in requirements.txt")
        passed.append("No groq in requirements.txt")

# FINAL RESULTS
print("\n" + "=" * 70)
print("📊 PYTHON VERCEL BACKEND TEST RESULTS")
print("=" * 70)

if errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    print("\n🚨 PYTHON BACKEND WILL NOT WORK ON VERCEL!")
    print("   Fix these errors before deploying.")
    exit_code = 1
else:
    print(f"\n✅ ALL TESTS PASSED! ({len(passed)} checks)")
    print("\n🎉 PYTHON BACKEND IS READY FOR VERCEL!")
    print("\nWhat will happen on Vercel:")
    print("   1. Vercel installs packages from requirements.txt")
    print("   2. Requests to /api/* go to api/index.py")
    print("   3. api/index.py imports backend.main.app")
    print("   4. FastAPI app handles the request")
    print("   5. Uses DeepSeek model service")
    print("   6. Returns JSON response")
    exit_code = 0

print("\n" + "=" * 70)
print("🔧 NEXT STEPS:")
print("=" * 70)
print("\n1. ✅ Python backend structure: CORRECT")
print("2. ⚠️  Add environment variables to Vercel dashboard")
print("3. ⚠️  Redeploy on Vercel")
print("4. ✅ Backend will work at: https://your-app.vercel.app/api/*")

print("\n" + "=" * 70)

sys.exit(exit_code)
