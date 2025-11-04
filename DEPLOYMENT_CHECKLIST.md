# 🚀 Deployment Checklist

## ✅ Pre-Deployment (Complete)

- [x] Code updated for serverless deployment
- [x] Vercel configuration ready (`vercel.json`)
- [x] API wrapper created (`api/index.py`)
- [x] Dependencies updated (`requirements.txt`)
- [x] UI updated to slate/emerald theme
- [x] Citation system working

---

## 📋 Deployment Steps

### Step 1: Create Supabase Database (5 mins)

1. **Go to Supabase**
   - Visit: https://supabase.com
   - Sign in with GitHub
   - Click "New Project"

2. **Configure Project**
   ```
   Organization: [Your org or create new]
   Project name: druginteract-db
   Database Password: [Generate strong password - SAVE THIS!]
   Region: US East (or closest to you)
   Pricing: Free
   ```

3. **Wait for initialization** (2-3 minutes)

4. **Get Connection String**
   - Go to: Project Settings (gear icon) → Database
   - Find: "Connection string" section
   - Copy: **Transaction** pooler URL
   - Should look like:
     ```
     postgresql://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
     ```
   - Replace `[YOUR-PASSWORD]` with your actual password!

5. **Initialize Database**
   - In Supabase: SQL Editor → New Query
   - Open: `backend/db/init.sql` from your project
   - Copy entire contents
   - Paste in SQL Editor
   - Click "Run" (or Cmd+Enter)
   - Should see: "Success. No rows returned"

6. **Verify Tables Created**
   - Go to: Table Editor
   - Should see: `chat_sessions`, `chat_logs`, `drug_interactions`, `references`

---

### Step 2: Push to GitHub (1 min)

```bash
cd /Users/iannjenga/Desktop/chatbot

# Stage all changes
git add .

# Commit
git commit -m "Configure for serverless deployment with Supabase"

# Push to GitHub
git push origin main
```

---

### Step 3: Deploy to Vercel (5 mins)

1. **Import Project**
   - Go to: https://vercel.com
   - Click: "Add New..." → "Project"
   - Import: `Jenks18/chatbot` from GitHub
   - Click: "Import"

2. **Configure Build Settings**
   - Framework Preset: **Next.js** (auto-detected)
   - Root Directory: `./` (leave as default)
   - Build Command: `npm run build` (auto-filled)
   - Output Directory: `.next` (auto-filled)

3. **Add Environment Variables**
   
   Click "Environment Variables" and add these **one by one**:

   | Name | Value |
   |------|-------|
   | `GROQ_API_KEY` | Your Groq API key from console.groq.com |
   | `DATABASE_URL` | Your Supabase connection string from Step 1 |
   | `GROQ_MODEL` | `llama-3.1-8b-instant` |
   | `NEXT_PUBLIC_API_URL` | `/api` |
   | `CORS_ORIGINS` | `*` |
   | `ENABLE_RAG` | `false` |

   **Important:**
   - Mark `GROQ_API_KEY` and `DATABASE_URL` as **Sensitive**
   - Apply to: **Production, Preview, and Development**

4. **Deploy!**
   - Click "Deploy"
   - Wait 2-3 minutes
   - Watch build logs for any errors

---

### Step 4: Test Deployment (2 mins)

1. **Visit Your Site**
   - You'll get a URL like: `https://chatbot-jenks18.vercel.app`
   - Or: `https://your-custom-domain.vercel.app`

2. **Test Features**
   - ✅ Page loads
   - ✅ Ask a question: "Tell me about acetaminophen toxicity"
   - ✅ Response appears
   - ✅ Citations work [1], [2]
   - ✅ Simple/Technical toggle works
   - ✅ References modal opens
   - ✅ Dark theme looks good

3. **Check Health Endpoint**
   - Visit: `https://your-app.vercel.app/api/health`
   - Should see:
     ```json
     {
       "status": "healthy",
       "database": "healthy",
       "model_server": "healthy",
       "timestamp": "2025-11-04T..."
     }
     ```

---

## 🔧 Troubleshooting

### Build Fails
- Check build logs in Vercel
- Common issues:
  - Missing environment variables
  - Syntax errors (check `get_errors` output)
  - Python version mismatch

### Database Connection Error
- Verify `DATABASE_URL` is correct
- Must use **Transaction pooler** URL (with `pgbouncer=true`)
- Check password is correct (no special char issues)
- Ensure Supabase project is active

### API Returns 500 Error
- Check: Vercel → Your Project → Logs → Functions
- Look for Python errors
- Common issues:
  - Missing Groq API key
  - Database schema not initialized
  - Import errors

### CORS Errors
- Make sure `CORS_ORIGINS` includes `*` or your Vercel domain
- Backend is on same domain (`/api`), so CORS shouldn't be an issue

---

## 🎉 Success!

Once deployed, your app will be live at:
- **Production**: `https://chatbot-jenks18.vercel.app`
- **API**: `https://chatbot-jenks18.vercel.app/api`
- **Docs**: `https://chatbot-jenks18.vercel.app/api/docs`

---

## 📊 Monitoring

- **Vercel Analytics**: Dashboard → Analytics
- **Supabase Usage**: Dashboard → Database → Reports
- **Groq Usage**: https://console.groq.com/usage

---

## 🚀 Next Steps

1. **Custom Domain** (optional)
   - Vercel → Settings → Domains
   - Add your domain

2. **Update CORS** (optional)
   - Change `CORS_ORIGINS` to your specific domain
   - Redeploy

3. **Add Features**
   - User authentication (Supabase Auth)
   - Document upload (Supabase Storage)
   - Real-time chat (Supabase Realtime)

---

**Total Deployment Time**: ~15 minutes  
**Total Cost**: $0/month (free tier)

**Ready to deploy?** Follow the steps above!
