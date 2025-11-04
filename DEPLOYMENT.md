# ToxicoGPT Deployment Guide (Vercel + DeepSeek)

## Prerequisites

1. **GitHub Account** - Code is already pushed
2. **Vercel Account** - Sign up at https://vercel.com
3. **Supabase Account** - You already have this set up
4. **DeepSeek API Key** - You already have: `sk-052da17567ab438bb0ea6e80b346a85d`

## Step 1: Deploy to Vercel

1. Go to https://vercel.com/dashboard
2. Click **"Add New..." → Project**
3. Import your GitHub repository: `Jenks18/chatbot`
4. Vercel will auto-detect it's a Next.js app
5. Click **Deploy** (don't add env vars yet, we'll do it next)

## Step 2: Add Environment Variables

Go to your project → **Settings → Environment Variables**

Add these variables for **Production, Preview, and Development**:

### AI Model (DeepSeek)
```
DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d
DEEPSEEK_MODEL=deepseek-chat
```

### Database (Supabase)
```
DATABASE_URL=postgresql://postgres:[YOUR_PASSWORD_HERE]@db.zzeycmksnujfdvasxoti.supabase.co:5432/postgres
NEXT_PUBLIC_SUPABASE_URL=https://zzeycmksnujfdvasxoti.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp6ZXljbWtzbnVqZmR2YXN4b3RpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIyODUxMTYsImV4cCI6MjA3Nzg2MTExNn0.gX37n0KQK9__8oea55JA1JP-JJhF2wUG18jIeaV81oM
```

**To get your DATABASE_URL password:**
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings → Database**
4. Copy the **Connection String** and replace `[YOUR-PASSWORD]` with your actual password

### Public API Keys
```
OPENFDA_API_KEY=rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb
NCBI_API_KEY=5141dbd81188ce3fc0547dbcf18a3fbe9209
```

### API Caching
```
API_CACHE_DURATION_DAYS=30
ENABLE_API_CACHING=true
```

## Step 3: Redeploy

After adding all environment variables:

1. Go to **Deployments** tab
2. Click the **three dots** on the latest deployment
3. Click **Redeploy**

## Step 4: Test Your Deployment

Once deployed, you'll get a URL like: `https://chatbot-xxx.vercel.app`

### Test the Frontend
Visit your Vercel URL directly - you should see the ToxicoGPT interface

### Test the API
Visit: `https://chatbot-xxx.vercel.app/api/health`

You should see:
```json
{
  "status": "healthy",
  "database": "connected",
  "model_server": true,
  "timestamp": "2025-11-04T..."
}
```

### Test a Query
Try asking: "Tell me about acetaminophen"

The AI should respond using **DeepSeek** (no more Groq/Llama rate limits!)

## Architecture

- **Frontend**: Next.js on Vercel Edge Network
- **Backend**: Python FastAPI as Vercel Serverless Functions
- **Database**: Supabase PostgreSQL (with API caching)
- **AI Model**: DeepSeek API (consistent quality, no rate limits)
- **Data Sources**: 6 FREE government APIs (RxNorm, FDA, PubChem, OpenFDA, PubMed, KEGG)

## Cost Breakdown

- **Vercel**: FREE (Hobby tier)
- **Supabase**: FREE (up to 500MB database)
- **DeepSeek**: ~$2-5/month (pay as you go)
- **Government APIs**: 100% FREE

## Troubleshooting

### "API error: Rate limit reached"
This means it's still trying to use Groq. Make sure:
1. You added `DEEPSEEK_API_KEY` to Vercel
2. You clicked **Redeploy** after adding env vars
3. Wait 1-2 minutes for deployment to complete

### "Database connection failed"
Check that:
1. `DATABASE_URL` has the correct password
2. Supabase project is active
3. You ran the migration: `migration_add_api_cache.sql`

### "DeepSeek API error"
Verify your API key is correct:
1. Log in to https://platform.deepseek.com
2. Go to API Keys
3. Copy the key exactly (starts with `sk-`)

## Support

If you need help, check:
- Vercel deployment logs: Project → Deployments → View Function Logs
- Supabase logs: Dashboard → Logs
- Browser console: F12 → Console tab

---

**You're all set!** 🎉 No more Groq rate limits, no more Render.com complexity - just clean DeepSeek-powered AI.
