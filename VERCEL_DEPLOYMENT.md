# Vercel Deployment Guide

## ✅ What's Ready

Your repository is now **Vercel-ready**! The Next.js app is at the root level, which is exactly what Vercel expects.

## 🚀 Deploy to Vercel

### Option 1: Use the Deploy Button

Click this button in your README:
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/Jenks18/chatbot)

### Option 2: Import from GitHub

1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Select your GitHub repository: `Jenks18/chatbot`
4. Vercel will auto-detect Next.js
5. Configure environment variables (see below)
6. Click "Deploy"

## 🔧 Environment Variables

In Vercel dashboard, add this environment variable:

```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

**Important**: Replace `https://your-backend-url.com` with your actual backend URL.

## �� Backend Deployment Options

Your FastAPI backend needs to be deployed separately. Here are your options:

### Option 1: Render.com (Recommended - Free Tier)
1. Go to [render.com](https://render.com)
2. Create new Web Service
3. Connect your GitHub repo
4. Root Directory: `backend`
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Add environment variables:
   - `DATABASE_URL` (use Render PostgreSQL)
   - `MODEL_SERVER_URL` (if using external Ollama)
   - `CORS_ORIGINS` (your Vercel URL)

### Option 2: Railway.app
1. Go to [railway.app](https://railway.app)
2. Create new project from GitHub
3. Add PostgreSQL database
4. Deploy backend from `backend/` directory

### Option 3: Your Own Server
- Deploy backend to your VPS/cloud server
- Ensure it's publicly accessible
- Configure CORS to allow your Vercel domain

## 🔒 CORS Configuration

Update `backend/main.py` to allow your Vercel domain:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-app.vercel.app",  # Add your Vercel URL
]
```

## 📝 Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] PostgreSQL database set up
- [ ] `NEXT_PUBLIC_API_URL` set in Vercel
- [ ] CORS configured in backend
- [ ] Frontend deployed to Vercel
- [ ] Test chat functionality
- [ ] Test admin dashboard

## 🧪 Testing

After deployment:
1. Visit your Vercel URL
2. Try sending a chat message
3. Check admin dashboard at `/admin`
4. Verify geolocation tracking works

## ⚠️ Important Notes

- **Ollama**: Not available on Vercel/Render free tiers. You'll need:
  - A VPS with Ollama installed, OR
  - Switch to OpenAI/Anthropic API
- **Database**: Use managed PostgreSQL (Render, Railway, Supabase)
- **Environment Variables**: Never commit `.env` file to GitHub

## 🆘 Troubleshooting

### Build fails on Vercel
- Check that `package.json` is at root level ✅
- Verify all dependencies are listed
- Check build logs for errors

### Can't connect to backend
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check backend is running (visit `/health` endpoint)
- Ensure CORS is configured properly

### Database connection errors
- Check `DATABASE_URL` format
- Ensure database allows external connections
- Verify credentials are correct

## 📚 Next Steps

1. Deploy backend to Render/Railway
2. Get backend URL
3. Deploy frontend to Vercel
4. Set environment variable
5. Test everything works

---

Your project is ready for Vercel! 🎉
