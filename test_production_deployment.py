#!/usr/bin/env python3
"""
Production Deployment Test
Tests all critical components as they would run on Vercel
"""
import os
import json
import sys
from pathlib import Path

print("=" * 70)
print("🔬 PRODUCTION DEPLOYMENT TEST")
print("=" * 70)

# Load environment from backend/.env for testing
backend_env = Path(__file__).parent / "backend" / ".env"
if backend_env.exists():
    print("\n📋 Loading backend/.env for testing...")
    try:
        from dotenv import load_dotenv
        load_dotenv(backend_env)
        print("   ✅ Environment loaded")
    except ImportError:
        print("   ℹ️  python-dotenv not installed, reading .env manually")
        with open(backend_env, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("   ✅ Environment loaded manually")

errors = []
warnings = []
critical = []

# Test 1: Check Supabase Configuration
print("\n" + "=" * 70)
print("1. TESTING SUPABASE CONFIGURATION")
print("=" * 70)

supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
supabase_anon = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

if supabase_url:
    print(f"✅ NEXT_PUBLIC_SUPABASE_URL: {supabase_url}")
else:
    critical.append("NEXT_PUBLIC_SUPABASE_URL not set")
    print("❌ NEXT_PUBLIC_SUPABASE_URL: NOT SET")

if supabase_anon:
    print(f"✅ NEXT_PUBLIC_SUPABASE_ANON_KEY: {supabase_anon[:20]}...{supabase_anon[-10:]}")
else:
    critical.append("NEXT_PUBLIC_SUPABASE_ANON_KEY not set")
    print("❌ NEXT_PUBLIC_SUPABASE_ANON_KEY: NOT SET")

# Test 2: Check Frontend API Configuration
print("\n" + "=" * 70)
print("2. TESTING FRONTEND API CONFIGURATION")
print("=" * 70)

api_ts = Path(__file__).parent / "services" / "api.ts"
if api_ts.exists():
    content = api_ts.read_text()
    print(f"✅ services/api.ts exists")
    
    # Check for hardcoded URLs
    if "localhost" in content and "process.env" not in content:
        warnings.append("api.ts may have hardcoded localhost")
        print("⚠️  Contains 'localhost' - check if it's hardcoded")
    
    # Check Supabase initialization
    if "createClient" in content:
        print("✅ Supabase client initialization found")
        
        # Check if it uses environment variables
        if "process.env.NEXT_PUBLIC_SUPABASE_URL" in content:
            print("✅ Uses NEXT_PUBLIC_SUPABASE_URL env var")
        else:
            critical.append("api.ts doesn't use NEXT_PUBLIC_SUPABASE_URL")
            print("❌ Doesn't use NEXT_PUBLIC_SUPABASE_URL env var")
        
        if "process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY" in content:
            print("✅ Uses NEXT_PUBLIC_SUPABASE_ANON_KEY env var")
        else:
            critical.append("api.ts doesn't use NEXT_PUBLIC_SUPABASE_ANON_KEY")
            print("❌ Doesn't use NEXT_PUBLIC_SUPABASE_ANON_KEY env var")
    else:
        errors.append("api.ts doesn't initialize Supabase client")
        print("❌ No Supabase client initialization found")
else:
    critical.append("services/api.ts not found")
    print("❌ services/api.ts not found!")

# Test 3: Check _app.tsx
print("\n" + "=" * 70)
print("3. TESTING _APP.TSX CONFIGURATION")
print("=" * 70)

app_tsx = Path(__file__).parent / "pages" / "_app.tsx"
if app_tsx.exists():
    content = app_tsx.read_text()
    print(f"✅ pages/_app.tsx exists")
    
    if "localhost" in content:
        warnings.append("_app.tsx contains 'localhost'")
        print("⚠️  Contains 'localhost' - verify it's not hardcoded")
    else:
        print("✅ No hardcoded localhost")
    
    # Check if it imports supabase
    if "supabase" in content.lower():
        print("✅ Imports Supabase")
    
else:
    warnings.append("pages/_app.tsx not found")
    print("⚠️  pages/_app.tsx not found")

# Test 4: Check environment variables needed
print("\n" + "=" * 70)
print("4. CHECKING REQUIRED ENVIRONMENT VARIABLES")
print("=" * 70)

required_env = {
    "Backend": [
        "DEEPSEEK_API_KEY",
        "DEEPSEEK_MODEL",
        "DATABASE_URL",
        "OPENFDA_API_KEY",
        "NCBI_API_KEY"
    ],
    "Frontend": [
        "NEXT_PUBLIC_SUPABASE_URL",
        "NEXT_PUBLIC_SUPABASE_ANON_KEY"
    ]
}

for category, vars in required_env.items():
    print(f"\n{category}:")
    for var in vars:
        value = os.getenv(var)
        if value:
            if "KEY" in var or "URL" in var:
                masked = f"{value[:15]}...{value[-10:]}" if len(value) > 25 else value[:10] + "..."
                print(f"   ✅ {var}: {masked}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            critical.append(f"{var} not set")
            print(f"   ❌ {var}: NOT SET")

# Test 5: Check database connection string format
print("\n" + "=" * 70)
print("5. TESTING DATABASE URL FORMAT")
print("=" * 70)

db_url = os.getenv("DATABASE_URL")
if db_url:
    if db_url.startswith("postgresql://"):
        print("✅ DATABASE_URL uses postgresql://")
        
        # Check components
        if "supabase.co" in db_url:
            print("✅ Points to Supabase")
        else:
            warnings.append("DATABASE_URL doesn't point to supabase.co")
            print("⚠️  Doesn't point to supabase.co")
        
        if ":5432/" in db_url:
            print("✅ Uses correct port (5432)")
        else:
            warnings.append("DATABASE_URL doesn't use port 5432")
            print("⚠️  Doesn't use port 5432")
        
        # Check if password is placeholder
        if "[" in db_url and "]" in db_url:
            critical.append("DATABASE_URL has placeholder password")
            print("❌ Contains placeholder [YOUR_PASSWORD] - MUST UPDATE!")
        else:
            print("✅ No placeholders detected")
            
    else:
        errors.append("DATABASE_URL doesn't start with postgresql://")
        print("❌ Should start with postgresql://")
else:
    critical.append("DATABASE_URL not set")
    print("❌ DATABASE_URL not set")

# Test 6: Check Vercel configuration
print("\n" + "=" * 70)
print("6. TESTING VERCEL CONFIGURATION")
print("=" * 70)

vercel_json = Path(__file__).parent / "vercel.json"
if vercel_json.exists():
    config = json.loads(vercel_json.read_text())
    print("✅ vercel.json exists")
    
    # Check env vars in vercel.json
    if "env" in config:
        print(f"✅ Environment variables defined in vercel.json:")
        for key in config["env"].keys():
            print(f"   - {key}")
    else:
        warnings.append("No env vars in vercel.json - must set in Vercel dashboard")
        print("⚠️  No env section in vercel.json")
        print("   ℹ️  You must add env vars via Vercel dashboard")
else:
    critical.append("vercel.json not found")
    print("❌ vercel.json not found!")

# Test 7: Test Supabase connection (if possible)
print("\n" + "=" * 70)
print("7. TESTING SUPABASE CONNECTION")
print("=" * 70)

try:
    # Try to import and test database connection
    sys.path.insert(0, str(Path(__file__).parent))
    from backend.db.database import engine, SessionLocal
    
    print("✅ Database module imported")
    
    # Try to create a session
    db = SessionLocal()
    print("✅ Database session created")
    
    # Try a simple query
    result = db.execute("SELECT 1 as test").fetchone()
    if result and result[0] == 1:
        print("✅ Database connection successful!")
        print("✅ Can execute queries")
    else:
        warnings.append("Database query returned unexpected result")
        print("⚠️  Query executed but result unexpected")
    
    db.close()
    
except Exception as e:
    error_msg = str(e)
    if "password authentication failed" in error_msg:
        critical.append("Database password is incorrect")
        print("❌ PASSWORD AUTHENTICATION FAILED!")
        print(f"   Error: {error_msg}")
    elif "could not connect" in error_msg:
        critical.append("Cannot connect to database")
        print("❌ CANNOT CONNECT TO DATABASE!")
        print(f"   Error: {error_msg}")
    elif "No module named" in error_msg:
        warnings.append("Cannot test database (missing dependencies)")
        print("⚠️  Cannot test database connection (missing dependencies)")
    else:
        warnings.append(f"Database connection error: {error_msg}")
        print(f"⚠️  Database connection error: {error_msg}")

# Test 8: Check for common Vercel deployment issues
print("\n" + "=" * 70)
print("8. CHECKING COMMON DEPLOYMENT ISSUES")
print("=" * 70)

# Check next.config.js
next_config = Path(__file__).parent / "next.config.js"
if next_config.exists():
    content = next_config.read_text()
    print("✅ next.config.js exists")
    
    # Check for serverless config
    if "target" in content and "serverless" in content:
        print("✅ Serverless target configured")
    
    # Check for env vars
    if "env:" in content or "publicRuntimeConfig" in content:
        print("ℹ️  Environment config found in next.config.js")
else:
    print("ℹ️  next.config.js not found (optional)")

# Check package.json for build scripts
package_json = Path(__file__).parent / "package.json"
if package_json.exists():
    pkg = json.loads(package_json.read_text())
    print("✅ package.json exists")
    
    if "scripts" in pkg and "build" in pkg["scripts"]:
        print(f"✅ Build script: {pkg['scripts']['build']}")
    else:
        errors.append("No build script in package.json")
        print("❌ No build script found!")
else:
    critical.append("package.json not found")
    print("❌ package.json not found!")

# FINAL SUMMARY
print("\n" + "=" * 70)
print("📊 TEST RESULTS SUMMARY")
print("=" * 70)

if critical:
    print(f"\n🚨 {len(critical)} CRITICAL ISSUE(S) - DEPLOYMENT WILL FAIL:")
    for issue in critical:
        print(f"   ❌ {issue}")
    print("\n   ⚠️  FIX THESE IMMEDIATELY!")

if errors:
    print(f"\n❌ {len(errors)} ERROR(S) FOUND:")
    for error in errors:
        print(f"   - {error}")

if warnings:
    print(f"\n⚠️  {len(warnings)} WARNING(S):")
    for warning in warnings:
        print(f"   - {warning}")

if not critical and not errors:
    print("\n✅ NO CRITICAL ERRORS FOUND!")
    if warnings:
        print("   Review warnings above")
    else:
        print("   All tests passed!")

# Deployment checklist
print("\n" + "=" * 70)
print("📋 VERCEL DEPLOYMENT CHECKLIST")
print("=" * 70)

print("""
1. Go to Vercel Dashboard → Settings → Environment Variables

2. Add these for Production, Preview, AND Development:
   
   Backend:
   ✓ DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d
   ✓ DEEPSEEK_MODEL=deepseek-chat
   ✓ DATABASE_URL=postgresql://postgres:[PASSWORD]@db.zzeycmksnujfdvasxoti.supabase.co:5432/postgres
   ✓ OPENFDA_API_KEY=rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb
   ✓ NCBI_API_KEY=5141dbd81188ce3fc0547dbcf18a3fbe9209
   ✓ API_CACHE_DURATION_DAYS=30
   ✓ ENABLE_API_CACHING=true
   
   Frontend (CRITICAL for 401 errors):
   ✓ NEXT_PUBLIC_SUPABASE_URL=https://zzeycmksnujfdvasxoti.supabase.co
   ✓ NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

3. Get Supabase password:
   - Go to Supabase Dashboard → Settings → Database
   - Copy password and update DATABASE_URL

4. Redeploy:
   - Deployments → Latest → Three dots → Redeploy
   - Wait 2-3 minutes

5. Test:
   - Visit https://your-app.vercel.app
   - Check browser console for errors
   - Try asking about a drug

Common 401 Error Causes:
❌ NEXT_PUBLIC_SUPABASE_ANON_KEY not set in Vercel
❌ NEXT_PUBLIC_SUPABASE_URL not set in Vercel
❌ Environment variables only set for Production (need all 3 environments)
❌ Forgot to redeploy after adding env vars
""")

print("=" * 70)

# Exit with error code if critical issues
if critical:
    sys.exit(1)
elif errors:
    sys.exit(2)
else:
    sys.exit(0)
