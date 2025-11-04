# 🚀 Serverless Deployment Guide - Full Stack on Vercel

## Why This Approach?

✅ **One platform** for frontend + backend  
✅ **No CORS issues** - same domain  
✅ **Free tier** - generous limits  
✅ **Auto-scaling** - pay only for what you use  
✅ **Fast deployments** - git push = live  

---

## 📋 What We Just Set Up

Your app is now configured as a **monorepo serverless deployment**:

```
Frontend: Next.js → Vercel Edge Network
Backend:  FastAPI → Vercel Serverless Functions
Database: PostgreSQL → Neon.tech (serverless)
```

---

## 🗄️ Step 1: Create Serverless Database (Supabase)

**Why Supabase?** Free tier, serverless PostgreSQL, built-in Auth, Storage, Realtime features

1. Go to **https://supabase.com**
2. Sign up with GitHub
3. Click **"New Project"**
   ```
   Organization: Create new or select existing
   Project name: druginteract-db
   Database Password: [Generate strong password - SAVE THIS!]
   Region: US East (closest to Vercel)
   Pricing Plan: Free
   ```
4. **Wait 2-3 minutes** for project to initialize

5. **Get your connection string**:
   - Click on "Project Settings" (gear icon)
   - Go to "Database" tab
   - Scroll to "Connection string" section
   - **Copy the "URI" format** (not the "psql" format)
   - Example: `postgresql://postgres.xxxxx:yourpassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres`
   
   **OR use the connection pooler** (recommended for serverless):
   - Under "Connection pooler" section
   - Copy the **"Transaction"** mode connection string
   - Example: `postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true`
   
   **IMPORTANT**: Replace `[YOUR-PASSWORD]` with the database password you created in step 3!

6. **Save this connection string** - you'll need it in Step 2!

---

## 🚀 Step 2: Deploy to Vercel

### A. Initial Setup

1. Go to **https://vercel.com**
2. Click **"Import Project"**
3. Select **`Jenks18/chatbot`** from GitHub
4. Vercel will auto-detect Next.js ✓

### B. Configure Environment Variables

Click **"Environment Variables"** and add these:

| Key | Value | How to get it |
|-----|-------|---------------|
| `GROQ_API_KEY` | `gsk_yourkey...` | From https://console.groq.com/keys |
| `DATABASE_URL` | `postgresql://postgres.xxxxx:...` | From Supabase (Step 1) - use Transaction pooler URL |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Leave as-is (or use `llama-3.3-70b-versatile` if you upgraded) |
| `CORS_ORIGINS` | `*` | Allow all origins (or use your Vercel domain later) |
| `ENABLE_RAG` | `false` | Disable RAG for now |
| `NEXT_PUBLIC_API_URL` | `/api` | Backend will be at /api/* |

**Important Notes:**
- Mark `GROQ_API_KEY` and `DATABASE_URL` as **"Secret"**
- Apply to **"Production, Preview, and Development"**

### C. Deploy!

1. Click **"Deploy"**
2. Wait 2-3 minutes (watch the build logs)
3. You'll get a URL like: `https://chatbot-jenks18.vercel.app`

---

## ✅ Step 3: Initialize Database

Your database is empty! You need to run the schema migration:

### Using Supabase SQL Editor (EASIEST)

1. Go to your Supabase project dashboard
2. Click **"SQL Editor"** in the left sidebar
3. Click **"New query"**
4. Copy the entire contents of `backend/db/init.sql`
5. Paste into the SQL editor
6. Click **"Run"** (or press Cmd/Ctrl + Enter)
7. You should see: "Success. No rows returned"

### Using psql (Alternative)

```bash
# If you have psql installed locally
psql "postgresql://postgres.xxxxx:yourpassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres" < backend/db/init.sql
```

### Verify Tables Were Created

1. In Supabase, go to **"Table Editor"**
2. You should see these tables:
   - `chat_sessions`
   - `chat_logs`
   - `drug_interactions`
   - `references`
   - Plus any other tables from your schema

---

## 🧪 Step 4: Test Your Deployment

1. Visit your Vercel URL: `https://your-app.vercel.app`
2. Try asking: **"Tell me about acetaminophen toxicity"**
3. Check:
   - ✅ Response appears
   - ✅ Citations work [1], [2]
   - ✅ Simple/Technical toggle works
   - ✅ References modal opens

---

## 🔧 Troubleshooting

### Cold Starts
**Symptom**: First request takes 2-5 seconds  
**Solution**: This is normal for serverless! Subsequent requests are fast.

### Database Connection Errors
**Symptom**: "unhealthy: connection refused"  
**Solution**: 
1. Verify `DATABASE_URL` is correct in Vercel env vars
2. Make sure you're using the **Transaction pooler** URL from Supabase (with `pgbouncer=true`)
3. Confirm your database password is correct (check for special characters that need URL encoding)
4. In Supabase, check "Database" → "Connection pooling" is enabled

### CORS Errors
**Symptom**: "blocked by CORS policy"  
**Solution**: Backend is on same domain! Update frontend to use `/api`:
- Change `NEXT_PUBLIC_API_URL` to `/api` (not a full URL)

### Model Errors
**Symptom**: "Rate limit reached"  
**Solution**: 
- Use `llama-3.1-8b-instant` (faster, cheaper)
- Or upgrade Groq to paid tier

---

## 💰 Cost Breakdown (Free Tier)

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Vercel** | 100GB bandwidth/mo | More than enough for MVP |
| **Supabase** | 500MB database, 2GB bandwidth | Includes Auth, Storage, Realtime! |
| **Groq** | 100K tokens/day | ~300 conversations/day |
| **TOTAL** | **$0/month** | 🎉 |

### When to upgrade:
- Vercel: ~10K+ users/month → $20/mo Pro
- Supabase: >500MB data → $25/mo Pro (8GB storage + more)
- Groq: >100K tokens/day → upgrade to Dev Tier

---

## 🎯 Next Steps After Deployment

1. **Add your Vercel domain to CORS**:
   ```
   CORS_ORIGINS=https://chatbot-jenks18.vercel.app
   ```

2. **Set up custom domain** (optional):
   - Vercel → Settings → Domains
   - Add: `druginteract.ai` or similar

3. **Monitor usage**:
   - Vercel Dashboard → Analytics
   - Supabase Dashboard → Database → Reports
   - Groq Console → Usage

4. **Use Supabase features** (optional but awesome):
   - **Auth**: Add user login (built-in!)
   - **Storage**: Store documents for RAG
   - **Realtime**: Live chat updates
   - **Edge Functions**: Additional serverless functions

---

## 🆚 Vercel vs Render Comparison

| Feature | Vercel (Serverless) | Render (Always-On) |
|---------|---------------------|-------------------|
| Cost | $0 (scales to usage) | $0 but sleeps after 15min |
| Cold starts | Yes (~1-2s) | No (but 30s wake-up) |
| Setup | One deployment | Separate frontend/backend |
| CORS | No issues | Need to configure |
| Scaling | Automatic | Manual |
| Best for | Low-medium traffic | Consistent traffic |

**My recommendation**: Start with Vercel (easier), switch to Render if you need always-on backend.

---

## 📚 Resources

- Vercel Docs: https://vercel.com/docs/frameworks/nextjs
- Supabase Docs: https://supabase.com/docs
- Supabase + Vercel Guide: https://supabase.com/docs/guides/getting-started/quickstarts/nextjs
- Groq API: https://console.groq.com/docs

---

**Ready to deploy?** Just push your changes and follow Steps 1-3 above!
