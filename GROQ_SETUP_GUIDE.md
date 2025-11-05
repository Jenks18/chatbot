# Groq Setup Guide

## Get Your Free Groq API Key

1. Go to: https://console.groq.com/keys
2. Sign up or log in (free account)
3. Click "Create API Key"
4. Copy your key (starts with `gsk_`)
5. Add to `backend/.env`:
   ```
   GROQ_API_KEY=gsk_your_actual_key_here
   GROQ_MODEL=groq/compound
   ```

## Why Groq/Compound?

- **Fast**: Groq's LPU™ provides blazing-fast inference
- **Free Tier**: Generous free quota for development
- **Compound Model**: Optimized for general-purpose tasks
- **No Rate Limits**: (on free tier for reasonable use)

## Models Available

- `groq/compound` - General purpose (recommended)
- `llama-3.3-70b-versatile` - Llama 3.3 70B
- `llama-3.1-8b-instant` - Fast, smaller model
- `mixtral-8x7b-32768` - Mixtral with 32K context

## Test Your Setup

```bash
cd backend
PYTHONPATH=. DEV_SQLITE=1 python -c "
from services.groq_service import groq_service
import asyncio
result = asyncio.run(groq_service.check_health())
print(result)
"
```

Should see: `{'status': 'healthy', 'model': 'groq/compound', ...}`
