# 🚀 Deploy to Render - Complete Guide

## Why Render?
- ✅ Free tier for backend APIs
- ✅ PostgreSQL database included
- ✅ Auto-deploys from GitHub
- ✅ Works perfectly with Vercel frontend
- ✅ No credit card required for free tier

---

## Step 1: Create Render Account

1. Go to https://render.com
2. Click "Get Started for Free"
3. Sign up with GitHub (easiest - auto-connects your repos)

---

## Step 2: Create PostgreSQL Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `toxicogpt-db`
   - **Database**: `toxicology_gpt`
   - **User**: `toxgpt_user`
   - **Region**: Choose closest to you
   - **PostgreSQL Version**: 15
   - **Plan**: **Free** (no credit card needed)

3. Click **"Create Database"**
4. Wait 2-3 minutes for provisioning
5. **SAVE THIS INFO** (you'll need it):
   - Go to "Info" tab
   - Copy **Internal Database URL** (starts with `postgresql://`)

---

## Step 3: Deploy Backend API

1. Click **"New +"** → **"Web Service"**

2. **Connect Repository**:
   - Click "Connect account" if not connected
   - Select: `Jenks18/chatbot`
   - Click "Connect"

3. **Configure Service**:
   ```
   Name: toxicogpt-api
   Region: Same as your database
   Branch: main
   Root Directory: backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Plan: Free
   ```

4. **Environment Variables** (click "Advanced" → "Add Environment Variable"):
   
   Add these **one by one**:
   
   ```bash
   DATABASE_URL = [paste your Internal Database URL from Step 2]
   
   GROQ_API_KEY = [paste your Groq API key from console.groq.com]
   
   GROQ_MODEL = llama-3.3-70b-versatile
   
   BACKEND_HOST = 0.0.0.0
   
   BACKEND_PORT = $PORT
   
   CORS_ORIGINS = http://localhost:3000,https://your-app.vercel.app
   
   ENABLE_RAG = false
   ```
   
   **Important**: Update `CORS_ORIGINS` after deploying to Vercel with your actual Vercel URL

5. Click **"Create Web Service"**

6. **Wait for deployment** (5-10 minutes first time)
   - Watch the logs for any errors
   - When you see "Application startup complete" → you're live! 🎉

7. **Copy your API URL**:
   - It will be something like: `https://toxicogpt-api.onrender.com`
   - Save this for the next step

---

## Step 4: Update Frontend for Render Backend

1. Update your local `.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=https://toxicogpt-api.onrender.com
   ```

2. Test locally:
   ```bash
   npm run dev
   ```
   
3. Try asking a drug interaction question - should work!

---

## Step 5: Deploy Frontend to Vercel

1. Go to https://vercel.com
2. Click "Add New..." → "Project"
3. Import `Jenks18/chatbot` from GitHub
4. Configure:
   ```
   Framework Preset: Next.js
   Root Directory: ./
   Build Command: npm run build
   Output Directory: .next
   Install Command: npm install
   ```

5. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL = https://toxicogpt-api.onrender.com
   ```
   (use your actual Render URL from Step 3)

6. Click **"Deploy"**

7. Wait 2-3 minutes

8. **Get your Vercel URL** (e.g., `https://chatbot-xyz123.vercel.app`)

---

## Step 6: Update CORS (Important!)

1. Go back to Render dashboard
2. Click on your `toxicogpt-api` service
3. Go to "Environment"
4. Find `CORS_ORIGINS`
5. Update to:
   ```
   https://your-actual-vercel-url.vercel.app
   ```
6. Click "Save Changes"
7. Service will auto-redeploy

---

## Step 7: Test Your Live App! 🎉

1. Go to your Vercel URL
2. Ask: "What are the interactions between aspirin and warfarin?"
3. Check admin page: `https://your-vercel-url.vercel.app/admin`
4. Verify database is logging conversations

---

## 🐛 Troubleshooting

### Backend won't start?
- Check Render logs for errors
- Verify all environment variables are set
- Make sure `requirements.txt` includes all dependencies

### Frontend can't connect to backend?
- Check CORS_ORIGINS includes your Vercel URL
- Verify NEXT_PUBLIC_API_URL is correct
- Check Render service is running (green checkmark)

### Database connection errors?
- Verify DATABASE_URL is the Internal URL (not External)
- Check database is running in Render dashboard
- Make sure it's the same region as your web service

### "Model decommissioned" error?
- Update GROQ_MODEL to: `llama-3.3-70b-versatile`
- Or use: `llama-3.1-8b-instant` (faster, free tier friendly)

---

## 💰 Free Tier Limits

**Render Free:**
- Backend sleeps after 15 mins of inactivity (wakes up in ~30 seconds)
- 750 hours/month (enough for 1 service running 24/7)
- PostgreSQL: 90 days of data retention, then oldest data deleted

**Groq Free:**
- 30 requests/minute
- 6,000 requests/day
- More than enough for testing and light production use

**Vercel Free:**
- 100GB bandwidth/month
- Unlimited deployments
- Custom domains supported

---

## 🚀 Your Live URLs

After deployment, you'll have:

1. **Backend API**: `https://toxicogpt-api.onrender.com`
   - API Docs: `https://toxicogpt-api.onrender.com/docs`
   - Health Check: `https://toxicogpt-api.onrender.com/health`

2. **Frontend**: `https://your-app.vercel.app`
   - Main Chat: `https://your-app.vercel.app`
   - Admin Dashboard: `https://your-app.vercel.app/admin`

3. **Database**: Managed by Render (internal only)

---

## 📝 Next Steps (Optional)

1. **Custom Domain**: Add your own domain in Vercel settings
2. **Analytics**: Monitor API usage in Render dashboard
3. **Upgrade**: If you get more users, upgrade to paid plans
4. **Monitoring**: Set up uptime monitoring (e.g., UptimeRobot)

Need help? Check the deployment logs or ask!
