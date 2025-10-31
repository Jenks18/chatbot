# 🚀 Complete Deployment Guide - DrugInteract AI

This guide walks you through deploying both the **frontend** (Vercel) and **backend** (Render) from scratch.

---

## 📋 Prerequisites

- [x] GitHub account
- [x] Groq API key (you have: gsk_aFxEb...)
- [x] Code pushed to GitHub (https://github.com/Jenks18/chatbot)

---

# PART 1: Deploy Backend to Render

## Step 1: Create Render Account

1. Go to **https://render.com**
2. Click **"Get Started for Free"**
3. Sign in with **GitHub** (this auto-connects your repos)
4. Authorize Render to access your repositories

---

## Step 2: Create PostgreSQL Database

1. From Render Dashboard, click **"New +"** → **"PostgreSQL"**

2. **Configuration**:
   ```
   Name: druginteract-db
   Database: toxicology_gpt
   User: toxgpt_user
   Region: Oregon (US West) or closest to you
   PostgreSQL Version: 15
   Instance Type: Free
   ```

3. Click **"Create Database"**

4. **Wait 2-3 minutes** for provisioning (watch the yellow → green status)

5. **CRITICAL: Save Database URL**
   - Once created, click on your database
   - Go to "Info" or "Connect" tab
   - Find **"Internal Database URL"** (starts with `postgresql://`)
   - **Copy this entire URL** - you'll need it in Step 3
   - Example format: `postgresql://toxgpt_user:PASSWORD@dpg-xxx.oregon-postgres.render.com/toxicology_gpt`

---

## Step 3: Deploy Backend Web Service

1. From Render Dashboard, click **"New +"** → **"Web Service"**

2. **Connect Repository**:
   - If not connected, click "Connect account"
   - Find and select: **`Jenks18/chatbot`**
   - Click **"Connect"**

3. **Configure Service**:
   ```
   Name: druginteract-api
   Region: Oregon (US West) - MUST MATCH YOUR DATABASE REGION
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

4. **Environment Variables** (Click "Advanced" → "Add Environment Variable"):
   
   Add these **one at a time**:

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | [Paste your Internal Database URL from Step 2] |
   | `GROQ_API_KEY` | [Paste your Groq API key from console.groq.com] |
   | `GROQ_MODEL` | `llama-3.3-70b-versatile` |
   | `BACKEND_HOST` | `0.0.0.0` |
   | `BACKEND_PORT` | `$PORT` |
   | `CORS_ORIGINS` | `http://localhost:3000` |
   | `ENABLE_RAG` | `false` |

   **Important**: We'll update `CORS_ORIGINS` after deploying the frontend

5. Click **"Create Web Service"**

6. **Watch the Build Logs**:
   - Deployment takes 5-10 minutes (first time)
   - Look for these success messages:
     ```
     ==> Building...
     ==> Installing dependencies
     ==> Starting server
     Application startup complete
     ```

7. **Get Your Backend URL**:
   - Once deployed, you'll see a URL like:
     ```
     https://druginteract-api.onrender.com
     ```
   - **SAVE THIS URL** - you need it for frontend deployment

8. **Test Your Backend**:
   - Click the URL or visit: `https://druginteract-api.onrender.com/docs`
   - You should see the FastAPI Swagger documentation
   - Try the health check: `https://druginteract-api.onrender.com/health`
   - Should return: `{"status":"healthy","database":"healthy","model_server":"healthy"}`

---

# PART 2: Deploy Frontend to Vercel

## Step 4: Create Vercel Account

1. Go to **https://vercel.com**
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel to access your repositories

---

## Step 5: Deploy Frontend

1. From Vercel Dashboard, click **"Add New..."** → **"Project"**

2. **Import Repository**:
   - Find: **`Jenks18/chatbot`**
   - Click **"Import"**

3. **Configure Project**:
   ```
   Project Name: druginteract-ai (or whatever you prefer)
   Framework Preset: Next.js (auto-detected)
   Root Directory: ./ (leave as root)
   Build Command: npm run build (auto-filled)
   Output Directory: .next (auto-filled)
   Install Command: npm install (auto-filled)
   ```

4. **Environment Variables** (Click "Environment Variables"):
   
   Add this variable:
   
   | Name | Value |
   |------|-------|
   | `NEXT_PUBLIC_API_URL` | `https://druginteract-api.onrender.com` |
   
   *(Use YOUR actual backend URL from Step 3)*

5. Click **"Deploy"**

6. **Wait for Deployment** (2-3 minutes):
   - Watch the build logs
   - Look for: "Build Completed" and "Deployment Ready"

7. **Get Your Frontend URL**:
   - You'll see something like:
     ```
     https://druginteract-ai.vercel.app
     ```
   - Or:
     ```
     https://chatbot-xyz123.vercel.app
     ```
   - **SAVE THIS URL**

8. **Test Your Frontend**:
   - Click on your Vercel URL
   - You should see the DrugInteract AI chat interface
   - BUT it won't connect yet - we need to update CORS!

---

# PART 3: Connect Frontend & Backend

## Step 6: Update CORS Settings

**Why?** Right now your backend only allows `localhost:3000`. We need to add your Vercel URL.

1. Go back to **Render Dashboard**
2. Click on your **`druginteract-api`** service
3. Click **"Environment"** in the left sidebar
4. Find **`CORS_ORIGINS`**
5. Click **"Edit"**
6. Update the value to:
   ```
   https://druginteract-ai.vercel.app,http://localhost:3000
   ```
   *(Replace with YOUR actual Vercel URL, keep localhost for local dev)*

7. Click **"Save Changes"**
8. Render will **auto-redeploy** (takes ~2 minutes)
9. Wait for "Live" status (green dot)

---

## Step 7: Test Your Live App! 🎉

1. **Visit your Vercel URL**: `https://druginteract-ai.vercel.app`

2. **Check Status**:
   - You should see a green "Online" indicator in the top right
   - If red, wait 30 seconds (Render free tier wakes up from sleep)

3. **Test Drug Interaction**:
   - Type: "What are the interactions between aspirin and warfarin?"
   - Press Enter
   - You should get a detailed DDI analysis with:
     - Comparison matrix
     - Interaction severity
     - Clinical recommendations
     - Safety warnings

4. **Check Admin Dashboard**:
   - Visit: `https://druginteract-ai.vercel.app/admin`
   - You should see your conversation logged with:
     - Session ID
     - Location (geolocation tracking)
     - Message count
     - Timestamp

---

# 🎯 Your Live URLs

After successful deployment:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | `https://druginteract-ai.vercel.app` | Main chat interface |
| **Admin** | `https://druginteract-ai.vercel.app/admin` | Analytics dashboard |
| **Backend API** | `https://druginteract-api.onrender.com` | API server |
| **API Docs** | `https://druginteract-api.onrender.com/docs` | Swagger/OpenAPI docs |
| **Health** | `https://druginteract-api.onrender.com/health` | System status |

---

# 🐛 Troubleshooting

## Frontend shows "Offline" status

**Cause**: Backend is sleeping (Render free tier sleeps after 15 min inactivity)

**Solution**: 
- Wait 30-60 seconds - it wakes up automatically
- The frontend auto-retries every 3 seconds
- Once awake, status turns green

## CORS Error in Browser Console

**Symptoms**: `Access-Control-Allow-Origin` error

**Solution**:
1. Go to Render → druginteract-api → Environment
2. Check `CORS_ORIGINS` includes your Vercel URL
3. Save and wait for redeployment

## Database Connection Error

**Symptoms**: Backend logs show "database connection failed"

**Solution**:
1. Verify `DATABASE_URL` in Render environment
2. Make sure it's the **Internal URL** (not External)
3. Ensure database and web service are in the **same region**

## Build Failed on Vercel

**Symptoms**: "Build failed" error during deployment

**Solution**:
1. Check build logs for specific error
2. Verify `NEXT_PUBLIC_API_URL` is set correctly
3. Make sure you're deploying from `main` branch
4. Try redeploying: Vercel Dashboard → Deployments → Redeploy

## Build Failed on Render

**Symptoms**: "Build failed" during backend deployment

**Solution**:
1. Check `requirements.txt` exists in `backend/` folder
2. Verify `Root Directory` is set to `backend`
3. Check logs for missing Python packages
4. Ensure Python version is 3.9 or higher

---

# 💰 Free Tier Limits

## Render Free Tier
- ✅ **750 hours/month** web service (1 service = 24/7 coverage)
- ✅ **PostgreSQL**: 90-day data retention, 1GB storage
- ⚠️ Sleeps after **15 minutes** of inactivity (wakes in ~30 seconds)
- ✅ 400 build hours/month

## Vercel Free Tier
- ✅ **100GB** bandwidth/month
- ✅ **Unlimited** deployments
- ✅ **Unlimited** projects
- ✅ Custom domains supported
- ✅ Automatic HTTPS

## Groq Free Tier
- ✅ **30 requests/minute**
- ✅ **14,400 requests/day**
- ✅ **No credit card** required
- ✅ Fast inference (10-18x faster than local)

**Total Cost**: $0/month for testing and light production use!

---

# 🚀 Post-Deployment Tasks

## Optional Enhancements

### 1. Custom Domain (Free on Vercel)
1. Go to Vercel → Your Project → Settings → Domains
2. Add your domain (e.g., `druginteract.ai`)
3. Update DNS records as shown
4. Update `CORS_ORIGINS` in Render to include new domain

### 2. Upgrade to Paid (If Needed)
- **Render**: $7/month (no sleep, better performance)
- **Vercel**: Free tier is usually sufficient
- **Groq**: Contact for higher limits (still free for most use)

### 3. Monitor Usage
- **Render**: Dashboard → Analytics (bandwidth, requests)
- **Vercel**: Analytics tab (pageviews, bandwidth)
- **Groq**: Console → Usage (API calls, tokens)

### 4. Set Up Alerts
- **UptimeRobot**: Free uptime monitoring (optional)
- Get notified if your app goes down

---

# 📝 Quick Reference Commands

## Test Backend (Local)
```bash
cd /Users/iannjenga/Desktop/chatbot
./start-backend.sh
# Visit: http://localhost:8000/docs
```

## Test Frontend (Local)
```bash
cd /Users/iannjenga/Desktop/chatbot
npm run dev
# Visit: http://localhost:3000
```

## Push Changes to Production
```bash
git add -A
git commit -m "Your changes here"
git push origin main
# Vercel auto-deploys instantly
# Render auto-deploys in ~2 minutes
```

## View Logs
- **Vercel**: Dashboard → Deployments → Click deployment → Logs
- **Render**: Dashboard → druginteract-api → Logs (live tail)

---

# ✅ Deployment Checklist

Before going live, verify:

- [ ] Backend deployed on Render (green "Live" status)
- [ ] Database created and connected
- [ ] Frontend deployed on Vercel (green checkmark)
- [ ] `NEXT_PUBLIC_API_URL` points to Render backend
- [ ] `CORS_ORIGINS` includes Vercel URL
- [ ] Health check returns "healthy" at `/health`
- [ ] Can send chat messages and get responses
- [ ] Admin dashboard shows logged conversations
- [ ] Geolocation tracking works (shows city/country)
- [ ] No CORS errors in browser console
- [ ] Status indicator shows "Online" (green)

---

# 🎓 What You've Built

You now have a **fully deployed, production-ready** drug interaction analysis platform:

- ✅ **AI-Powered Analysis**: Groq's llama-3.3-70b for medical-grade DDI analysis
- ✅ **Cloud Infrastructure**: Vercel (frontend) + Render (backend) + PostgreSQL
- ✅ **Analytics Dashboard**: Track conversations, locations, usage patterns
- ✅ **Geolocation Tracking**: IP → City, Country, Timezone
- ✅ **Structured Output**: 15+ category DDI analysis with severity ratings
- ✅ **Auto-Deploy**: Push to GitHub → Auto-deploys to production
- ✅ **Free Hosting**: $0/month for testing and moderate usage

**Congratulations! 🎉**

---

Need help? Check the logs or reach out!
