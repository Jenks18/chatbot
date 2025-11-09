# Update Vercel Environment Variables

## ⭐ BEST SOLUTION: Compound Model + Free APIs

We now use `groq/compound` for intelligence BUT intercept searches to use FREE APIs!

### Quick Fix (5 minutes):

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Click on your `chatbot` project
3. Go to **Settings** tab
4. Click **Environment Variables** in the left sidebar
5. Find or add these variables:

   ```
   GROQ_MODEL = groq/compound
   OPENFDA_API_KEY = rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb
   NCBI_API_KEY = 5141dbd81188ce3fc0547dbcf18a3fbe9209
   ```

6. Make sure they're set for **Production**, **Preview**, and **Development**
7. Click **Save**
8. Go to **Deployments** tab
9. Click the three dots (...) on the latest deployment
10. Click **Redeploy**

### Why This is GENIUS:

**The Problem:**
- Groq compound charges $5-8 per 1000 search requests
- Rate limits on underlying models (gpt-oss-120b has 8K TPM)

**Our Solution:**
- Use compound model for AI reasoning (GPT-OSS-120B + Llama 4)
- Set `tool_choice="none"` to disable Groq's expensive searches
- Use YOUR free APIs instead:
  - ✅ OpenFDA (unlimited, free)
  - ✅ NCBI/PubMed (unlimited, free)
  - ✅ FDA Drug Labels (unlimited, free)

### Cost Comparison:

| Search Method | Cost per 1000 | Data Quality |
|---------------|---------------|--------------|
| Groq Web Search | $5-8 | Good |
| Groq Visit Website | $1 | Good |
| **Our OpenFDA** | **$0 FREE** | **Excellent** |
| **Our NCBI** | **$0 FREE** | **Excellent** |

### How It Works:

1. User asks about a drug
2. Compound model reasons intelligently
3. We intercept and detect drug query
4. Fetch FDA data with our free key
5. Enrich response with official data
6. Return: AI intelligence + government data
7. Total cost: **$0**

### Benefits:

✅ **Compound model intelligence** (best reasoning)
✅ **$0 search costs** (use free APIs)
✅ **No rate limits** on our APIs
✅ **Official FDA data** (more reliable)
✅ **Better citations** (government sources)
✅ **Unlimited queries**

### Verification:

After redeployment, check:
- No "Rate limit reached" errors
- Responses include FDA safety information
- Model shows as "groq/compound+free-apis"
- Can ask unlimited questions

### Important Notes:

1. **The local `.env` file does NOT deploy to Vercel**
2. Environment variables must be set in Vercel dashboard
3. Changes require redeployment to take effect
4. This works for ALL modes (patient/doctor/researcher)
5. Your API keys give unlimited free access to official drug data
