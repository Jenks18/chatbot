# Vercel Environment Variables Setup

After deploying to Vercel, you need to set these environment variables:

## Required Variables

Go to: Vercel Dashboard → Your Project → Settings → Environment Variables

Add these one by one:

| Variable Name | Value | Notes |
|--------------|-------|-------|
| `GROQ_API_KEY` | `gsk_...` | From https://console.groq.com/keys |
| `DATABASE_URL` | `postgresql://postgres.xxx:password@...pooler.supabase.com:6543/postgres?pgbouncer=true` | From Supabase (Transaction pooler) |
| `GROQ_MODEL` | `llama-3.1-8b-instant` | Or `llama-3.3-70b-versatile` if upgraded |
| `NEXT_PUBLIC_API_URL` | `/api` | Points to serverless backend |
| `CORS_ORIGINS` | `*` | Allow all (or your Vercel domain) |
| `ENABLE_RAG` | `false` | Disable RAG for now |

## Important Notes

1. Mark `GROQ_API_KEY` and `DATABASE_URL` as **Encrypted/Secret**
2. Apply to **Production, Preview, and Development** environments
3. After adding variables, redeploy the project

## Getting Supabase DATABASE_URL

1. Go to https://supabase.com → Your Project
2. Settings → Database
3. Connection string → **Transaction** mode
4. Copy the full URL (replace `[YOUR-PASSWORD]` with your actual password)
5. Should include `?pgbouncer=true` at the end

Example:
```
postgresql://postgres.abc123:mypassword@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```
