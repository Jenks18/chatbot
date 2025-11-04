# Model Provider Switching Guide

## Overview
ToxicoGPT now supports **two AI model providers** that you can easily switch between using a single environment variable.

## Supported Providers

### 1. **Groq** (Default - FREE)
- **Model**: `llama-3.1-70b-versatile`
- **Context Window**: 128K tokens
- **Cost**: FREE (with rate limits: ~14,400 requests/day)
- **Speed**: Extremely fast
- **Best For**: High volume, cost-sensitive deployments

### 2. **DeepSeek** (Currently Active)
- **Model**: `deepseek-chat`
- **Context Window**: 64K tokens
- **Cost**: ~$0.14 per 1M input tokens, $0.28 per 1M output tokens
- **Speed**: Fast
- **Best For**: Consistent quality, no rate limit concerns

## How to Switch

### Environment Variable
```bash
MODEL_PROVIDER=groq     # Use Groq (FREE)
MODEL_PROVIDER=deepseek # Use DeepSeek (paid but cheap)
```

### In Vercel
1. Go to: **Settings → Environment Variables**
2. Add/Update: `MODEL_PROVIDER=deepseek` (or `groq`)
3. Redeploy

### Local Development
Update `/backend/.env`:
```bash
MODEL_PROVIDER=deepseek
```

## Current Setup

✅ **DeepSeek is currently active** (as of latest deployment)

To switch back to Groq:
- Change `MODEL_PROVIDER=groq` in Vercel
- Redeploy

## API Keys Required

Both are already configured in your environment variables:

```bash
# Groq
GROQ_API_KEY=your_groq_key_here
GROQ_MODEL=llama-3.1-70b-versatile

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key_here
DEEPSEEK_MODEL=deepseek-chat
```

## Cost Comparison

### Scenario: 1000 queries/day with API data

| Provider | Context per Query | Monthly Cost | Notes |
|----------|-------------------|--------------|-------|
| **Groq** | 50K tokens | **$0** | Free tier, may hit rate limits |
| **DeepSeek** | 50K tokens | **~$2-5** | Consistent, no limits |

With caching (30 days), actual costs are much lower!

## When to Use Each

### Use Groq When:
- ✅ You want FREE
- ✅ Traffic is moderate (< 10K queries/day)
- ✅ You can handle occasional rate limiting
- ✅ Speed is critical

### Use DeepSeek When:
- ✅ You need guaranteed availability (no rate limits)
- ✅ Budget allows $2-10/month
- ✅ You want consistent response quality
- ✅ High traffic expected

## Implementation Details

### Model Router (`services/model_router.py`)
Automatically imports the correct service based on `MODEL_PROVIDER`:

```python
MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "groq").lower()

if MODEL_PROVIDER == "deepseek":
    from services.deepseek_service import deepseek_service as model_service
else:
    from services.groq_model_service import model_service
```

### Both Services Support:
- ✅ Patient/Doctor/Researcher modes
- ✅ Inline citations [1], [2], [3]
- ✅ REFERENCES section
- ✅ Large context windows (50-128K tokens)
- ✅ Same API interface (drop-in replacement)

## Testing

After switching providers:

1. **Health Check**: Visit `/health` endpoint
2. **Test Query**: Ask "Tell me about aspirin"
3. **Check Response**: Should include citations and references
4. **Verify Logs**: Check which model is being used in logs

## Monitoring

Check which provider is active:
- Backend logs will show: `[Model Router] Using DeepSeek API` or `[Model Router] Using Groq API`
- Admin panel shows `model_used` field in chat logs

## Recommendation

**Start with DeepSeek** for consistent quality, then switch to Groq if you want to optimize costs and can handle rate limits.

Current monthly cost with DeepSeek + FREE APIs: **~$2-5** 💰
