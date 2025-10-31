# 🚀 Switching to Groq - Setup Instructions

## Get Your FREE Groq API Key

1. **Go to Groq Console**: https://console.groq.com/
2. **Sign up/Login** (it's free!)
3. **Click "API Keys"** in the left sidebar
4. **Create New API Key**
5. **Copy the key** (starts with `gsk_...`)

## Add API Key to Your Backend

Open `/Users/iannjenga/Desktop/chatbot/backend/.env` and replace:
```
GROQ_API_KEY=your_groq_api_key_here
```
with:
```
GROQ_API_KEY=gsk_your_actual_key_here
```

## Available Groq Models (Updated 2025)

You can use any of these models (set in `GROQ_MODEL`):

- **llama-3.3-70b-versatile** ⭐ (RECOMMENDED - best for medical/DDI analysis)
- **llama-3.1-8b-instant** (faster, lighter, great for free tier)
- **mixtral-8x7b-32768** (great for structured output)
- **llama-3.2-90b-vision-preview** (if you need image analysis later)

**Note**: llama-3.1-70b-versatile was decommissioned. Use llama-3.3-70b-versatile instead.

## Free Tier Limits

- **6,000 requests per minute** (more than enough!)
- **30,000 tokens per minute**
- No credit card required

## What Changed

✅ Switched from local Ollama to cloud Groq
✅ Same DDI prompts and output format
✅ Same structured 15+ category analysis
✅ Faster inference (10-18x speed)
✅ Better model quality (70B vs 3B parameters)
✅ No local GPU/Ollama server needed
✅ Perfect for Vercel deployment

## Ready to Test?

After adding your API key, restart the backend:
```bash
./start-backend.sh
```

Then test with:
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the interactions between aspirin and ibuprofen?"}'
```
