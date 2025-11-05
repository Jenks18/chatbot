# Vercel Deployment Fix Guide

## Problem Analysis

Your 401 errors on `/favicon.svg` are **NOT authentication errors** - they're Vercel returning 401 for missing static files. The real issue is likely:

1. ❌ **NEXT_PUBLIC_API_URL not set** - frontend tries to call localhost instead of `/api`
2. ❌ **Environment variables not in Vercel** - backend can't start
3. ⚠️  Missing favicon.svg (minor issue)

## Solution Steps

### Step 1: Add Environment Variables to Vercel

Go to your Vercel project → **Settings** → **Environment Variables**

Add these for **ALL THREE** environments (Production, Preview, Development):

```bash
# Frontend (CRITICAL - fixes API calls)
NEXT_PUBLIC_API_URL=/api

# Supabase (optional - not currently used)
NEXT_PUBLIC_SUPABASE_URL=https://zzeycmksnujfdvasxoti.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6ZXljbWtzbnVqZmR2YXN4b3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODUxMTYsImV4cCI6MjA3Nzg2MTExNn0.gX37n0KQK9__8oea55JA1JP-JJhF2wUG18jIeaV81oM

# Backend (CRITICAL - needed for API to work)
DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d
DEEPSEEK_MODEL=deepseek-chat
DATABASE_URL=postgresql://postgres.zzeycmksnujfdvasxoti:kMOFPkWLvHmRWATc@aws-0-us-west-1.pooler.supabase.com:6543/postgres
OPENFDA_API_KEY=rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb
NCBI_API_KEY=5141dbd81188ce3fc0547dbcf18a3fbe9209
API_CACHE_DURATION_DAYS=30
ENABLE_API_CACHING=true
```

### Step 2: Redeploy

1. Go to **Deployments** tab
2. Find the latest deployment
3. Click the **three dots** menu (...)
4. Click **Redeploy**
5. Wait 2-3 minutes

### Step 3: Test Deployment

1. Visit your Vercel URL: `https://chatbot-y1ar.vercel.app`
2. Open browser console (F12 → Console)
3. Check for errors
4. Try asking: "Tell me about acetaminophen"

### Expected Results

✅ Homepage loads without errors  
✅ Health check shows "healthy" (green)  
✅ Chat queries work and return results  
✅ No more 401 errors (except favicon.svg - harmless)  

## Why This Fixes the 401s

The 401 errors you're seeing are **NOT** authentication failures. They're Vercel's way of saying:

- `/favicon.svg` - File not found (we can add this)
- Backend API calls failing because `NEXT_PUBLIC_API_URL` defaults to `localhost:8000`

When `NEXT_PUBLIC_API_URL=/api`, the frontend will call:
- ❌ `http://localhost:8000/health` (fails in production)
- ✅ `https://your-app.vercel.app/api/health` (works!)

## Debugging After Deployment

If it still doesn't work:

1. **Check Vercel Function Logs:**
   - Deployments → Latest → Functions tab
   - Look for Python errors

2. **Check Browser Console:**
   - F12 → Console
   - Look for API call errors

3. **Test Backend Directly:**
   - Visit: `https://your-app.vercel.app/api/health`
   - Should return: `{"status":"healthy","database":"healthy","model_server":"healthy"}`

4. **Common Issues:**
   - ❌ Env vars only set for Production (need all 3)
   - ❌ Forgot to redeploy after adding env vars
   - ❌ DATABASE_URL has wrong password
   - ❌ DEEPSEEK_API_KEY is invalid

## Quick Test Commands

Test the deployed API:

```bash
# Test health endpoint
curl https://your-app.vercel.app/api/health

# Test chat endpoint
curl -X POST https://your-app.vercel.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about aspirin", "user_mode": "patient"}'
```

## File Structure (Correct)

```
✅ api/index.py - Serverless entry point
✅ backend/ - FastAPI backend code
✅ requirements.txt - Python dependencies
✅ vercel.json - Deployment config
✅ next.config.js - Next.js config
✅ package.json - Node.js dependencies
```

All files are correct! Just need environment variables.
