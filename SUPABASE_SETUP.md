# 🚀 Supabase + Vercel Serverless Setup

## Why Supabase?

✅ **Free PostgreSQL** (500MB)  
✅ **Connection pooling** built-in (perfect for serverless)  
✅ **Auto-scaling** database  
✅ **Built-in Auth** (add user login later)  
✅ **Storage** (for RAG documents)  
✅ **Realtime** (live chat updates)  
✅ **Better than Neon** for Next.js apps!

---

## 🎯 Quick Setup (10 minutes)

### 1. Create Supabase Project

```
→ Go to https://supabase.com
→ Sign in with GitHub
→ Click "New Project"
→ Name: druginteract-db
→ Region: US East
→ Generate strong password (SAVE IT!)
→ Wait 2-3 minutes for setup
```

### 2. Get Database URL

```
→ Project Settings (gear icon)
→ Database tab
→ Connection string section
→ Copy "Transaction" pooler URL
→ Should look like:
   postgresql://postgres.xxxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true

→ Replace [PASSWORD] with your actual password!
```

### 3. Initialize Database

```
→ Supabase Dashboard
→ SQL Editor (left sidebar)
→ New Query
→ Copy entire contents of backend/db/init.sql
→ Paste and Run (Cmd+Enter)
```

### 4. Deploy to Vercel

```
→ Go to https://vercel.com
→ Import Jenks18/chatbot
→ Add Environment Variables:
   GROQ_API_KEY=gsk_...
   DATABASE_URL=postgresql://postgres.xxxxx:...
   GROQ_MODEL=llama-3.1-8b-instant
   NEXT_PUBLIC_API_URL=/api
   CORS_ORIGINS=*
   ENABLE_RAG=false
→ Deploy!
```

### 5. Test

```
→ Visit https://your-app.vercel.app
→ Ask: "Tell me about acetaminophen toxicity"
→ Verify citations work
```

---

## 🔒 Security Tips

**Environment Variables:**
- Mark `GROQ_API_KEY` and `DATABASE_URL` as **Encrypted**
- Never commit `.env` files to Git

**Database Password:**
- Use Supabase's generated password (strong!)
- If you need to reset: Project Settings → Database → Reset Database Password

**Connection Pooling:**
- Always use the **Transaction** pooler URL for serverless
- This prevents "too many connections" errors
- Format: `...pooler.supabase.com:6543/postgres?pgbouncer=true`

---

## 🎁 Supabase Bonus Features

### Add User Authentication (Later)

```typescript
// In your Next.js app
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// Login users, track their conversations, etc.
```

### Store RAG Documents

```
→ Supabase Dashboard → Storage
→ Create bucket: "documents"
→ Upload your PDF/TXT files
→ Access them in your backend for RAG
```

### Add Realtime Chat

```typescript
// Watch for new messages
supabase
  .channel('chat')
  .on('postgres_changes', { 
    event: 'INSERT', 
    schema: 'public', 
    table: 'chat_logs' 
  }, (payload) => {
    console.log('New message!', payload)
  })
  .subscribe()
```

---

## 💰 Cost Comparison

| Feature | Supabase Free | Neon Free | Winner |
|---------|---------------|-----------|--------|
| Storage | 500MB | 512MB | Tie |
| Bandwidth | 2GB/mo | 5GB/mo | Neon |
| Auth | ✅ Built-in | ❌ | **Supabase** |
| Storage | ✅ Built-in | ❌ | **Supabase** |
| Realtime | ✅ Built-in | ❌ | **Supabase** |
| Connection Pool | ✅ Built-in | ✅ Built-in | Tie |
| **Best for** | Full-stack apps | Simple databases | **Supabase** |

**Verdict**: Supabase is better for your use case! 🎉

---

## 🔧 Troubleshooting

### "Too many connections"
→ Make sure you're using the **pooler** URL (with `pgbouncer=true`)

### "Password authentication failed"
→ Check your password has no special chars, or URL-encode them
→ Or regenerate password in Supabase settings

### Cold starts slow
→ This is normal! First request ~2 seconds
→ Subsequent requests are fast (<200ms)

### Can't see tables in Supabase
→ Make sure you ran the init.sql in SQL Editor
→ Check "Table Editor" to verify tables exist

---

## 🚀 Deploy Now!

Your project is ready! Just:

1. Set up Supabase (5 mins)
2. Get connection string
3. Deploy to Vercel
4. You're live! 🎉

Total time: ~10 minutes
Total cost: $0/month

**Questions?** Check https://supabase.com/docs or ask me!
