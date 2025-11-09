# 🔴 CRITICAL: Database Connection Issue - Root Cause Found

## Problem Summary

**The Supabase database is NOT connected**, which is why:
1. ❌ Chat messages are not being saved
2. ❌ Admin panel shows no sessions/history
3. ❌ Session persistence doesn't work in the widget
4. ❌ You're getting 406 errors (likely from failed database operations)

## Error Details

```
psycopg2.OperationalError: connection to server at "aws-0-us-west-1.pooler.supabase.com" 
(52.8.172.168), port 6543 failed: FATAL:  Tenant or user not found
```

**This error means:**
- The Supabase project no longer exists, OR
- The database credentials have expired/changed, OR
- The Supabase project has been paused/deleted

## Immediate Fixes

### Option 1: Fix Supabase Connection (Recommended)

1. **Check Supabase Project Status:**
   - Go to https://supabase.com/dashboard
   - Verify your project `zzeycmksnujfdvasxoti` exists and is active
   - If paused, restart it
   - If deleted, create a new project

2. **Get Fresh Database Credentials:**
   - In Supabase Dashboard → Settings → Database
   - Copy the **Connection Pooling** URL (Port 6543 - Transaction mode)
   - Should look like: `postgresql://postgres.[PROJECT]:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres`

3. **Update Environment Variables:**
   
   In `.env.production`:
   ```bash
   DATABASE_URL=postgresql://postgres.[YOUR_PROJECT]:[YOUR_PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
   ```

   In Vercel Dashboard (Settings → Environment Variables):
   - Update `DATABASE_URL` with the new connection string
   - Redeploy the application

4. **Initialize Database Tables:**
   ```bash
   cd backend
   python -c "from db.database import Base, engine; Base.metadata.create_all(engine)"
   ```

### Option 2: Use Local PostgreSQL (Development)

If you want to test locally without Supabase:

1. **Install PostgreSQL:**
   ```bash
   brew install postgresql@15
   brew services start postgresql@15
   ```

2. **Create Local Database:**
   ```bash
   createdb toxicology_gpt
   ```

3. **Create `.env.local`:**
   ```bash
   DATABASE_URL=postgresql://$(whoami)@localhost:5432/toxicology_gpt
   DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d
   DEEPSEEK_MODEL=deepseek-chat
   OPENFDA_API_KEY=rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb
   NCBI_API_KEY=5141dbd81188ce3fc0547dbcf18a3fbe9209
   API_CACHE_DURATION_DAYS=30
   ENABLE_API_CACHING=true
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Initialize Tables:**
   ```bash
   cd backend
   python -c "from db.database import Base, engine; Base.metadata.create_all(engine)"
   ```

### Option 3: Use SQLite (Quick Testing)

For immediate testing without any PostgreSQL setup:

1. **Create `.env.local`:**
   ```bash
   DEV_SQLITE=1
   DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d
   DEEPSEEK_MODEL=deepseek-chat
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

2. **Start Backend:**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

   The SQLite database will be automatically created at `backend/dev-data.sqlite`

## Testing the Fix

After implementing one of the options above:

1. **Test Database Connection:**
   ```bash
   python3 test_database.py
   ```
   
   Should see:
   ```
   ✅ Database connection successful!
   📊 Found 5 tables:
      - api_cache
      - chat_logs
      - interactions
      - references
      - sessions
   ```

2. **Test Chat Endpoint:**
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message":"What is acetaminophen?","session_id":"test-123"}'
   ```

3. **Check Admin Panel:**
   - Start frontend: `npm run dev`
   - Visit: http://localhost:3000/admin
   - Should see sessions and chat logs

4. **Test Widget:**
   - Visit: http://localhost:3000
   - Send messages in chat
   - Click "Open Full" - should preserve conversation

## What Was Working Wrong

### Before (Current State):
```
User sends message → Backend tries to save → Database FAILS → 
Message lost → Admin shows nothing → Widget can't load history
```

### After (With Working Database):
```
User sends message → Backend saves to database → 
Message stored → Admin shows data → Widget loads history ✅
```

## Verification Checklist

- [ ] Database connection works (no "Tenant or user not found" error)
- [ ] Tables exist in database (chat_logs, sessions, etc.)
- [ ] Chat messages are being saved
- [ ] Admin panel shows sessions and history
- [ ] Widget preserves conversation when clicking "Open Full"
- [ ] No 406 errors in browser console

## Quick Start (Fastest Method)

**For immediate testing, use SQLite:**

```bash
# 1. Create .env.local file
cat > .env.local << 'EOF'
DEV_SQLITE=1
DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d
DEEPSEEK_MODEL=deepseek-chat
NEXT_PUBLIC_API_URL=http://localhost:8000
OPENFDA_API_KEY=rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb
NCBI_API_KEY=5141dbd81188ce3fc0547dbcf18a3fbe9209
EOF

# 2. Start backend (in one terminal)
cd backend
uvicorn main:app --reload --port 8000

# 3. Start frontend (in another terminal)
cd /Users/iannjenga/Desktop/chatbot
npm run dev

# 4. Test it
open http://localhost:3000
```

## Production Deployment

Once Supabase is fixed:

```bash
# 1. Update Vercel environment variables
# Go to Vercel Dashboard → Settings → Environment Variables
# Update DATABASE_URL with new Supabase connection string

# 2. Initialize database tables
python3 -c "from backend.db.database import Base, engine; Base.metadata.create_all(engine)"

# 3. Deploy
git add -A
git commit -m "fix: restore database connection and session persistence"
git push origin main

# 4. Verify on production
curl https://chatbot-y1ar.vercel.app/api/health
```

## Need Help?

If you need to:
1. **Get new Supabase credentials** - Check Supabase dashboard
2. **Use local database** - Follow Option 2 above
3. **Quick test with SQLite** - Follow Option 3 above

The widget code and frontend are working correctly - they just need a working database connection to save and load messages!
