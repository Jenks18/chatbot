# Update Vercel Environment Variables

## CRITICAL: Fix Rate Limit Errors

The rate limit errors happen because Vercel is using old environment variables.

### Quick Fix (5 minutes):

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Click on your `chatbot` project
3. Go to **Settings** tab
4. Click **Environment Variables** in the left sidebar
5. Find `GROQ_MODEL` and click Edit (or Add if it doesn't exist)
6. Change the value to: `llama-3.1-70b-versatile`
7. Make sure it's set for **Production**, **Preview**, and **Development**
8. Click **Save**
9. Go to **Deployments** tab
10. Click the three dots (...) on the latest deployment
11. Click **Redeploy**
12. Wait for deployment to finish

### Why This Works:

- `groq/compound` → routes to `gpt-oss-120b` (8,000 TPM) ❌
- `llama-3.1-70b-versatile` → direct access (30,000 TPM) ✅

### Verification:

After redeployment, test the chat. You should see:
- No more "Rate limit reached" errors
- Faster responses
- Can ask multiple questions rapidly

### Alternative: Use Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Set environment variable
vercel env add GROQ_MODEL production
# When prompted, enter: llama-3.1-70b-versatile

# Redeploy
vercel --prod
```

### Model Comparison:

| Model | TPM Limit | Quality | Status |
|-------|-----------|---------|--------|
| groq/compound | Varies (8K-30K) | High | ❌ Unreliable |
| gpt-oss-120b | 8,000 | High | ❌ Too low |
| mixtral-8x7b-32768 | 18,000 | High | ✅ Good |
| llama-3.1-70b-versatile | 30,000 | Very High | ✅✅ **Best** |

### Important Notes:

1. **The local `.env` file does NOT deploy to Vercel**
2. Environment variables must be set in Vercel dashboard
3. Changes require redeployment to take effect
4. This affects ALL three modes (patient/doctor/researcher)
