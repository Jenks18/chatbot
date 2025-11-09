# 🔴 Fix Supabase Database Connection

## The Problem

Your Supabase project credentials show "Tenant or user not found" error. This means:
1. The database password in your connection string is incorrect/expired
2. OR the Supabase project was paused/deleted

## Steps to Fix

### 1. Go to Supabase Dashboard

Visit: https://supabase.com/dashboard/project/zzeycmksnujfdvasxoti

If the project doesn't exist, you'll need to create a new one.

### 2. Reset Database Password

1. Click **Settings** (gear icon) in sidebar
2. Click **Database**
3. Scroll to **Database Password**
4. Click **Reset Database Password**
5. Copy the NEW password (you'll only see it once!)

### 3. Get NEW Connection String

After resetting password, get the connection string:

1. Still in **Settings → Database**
2. Find **Connection String** section
3. Select **URI** tab
4. Copy the connection string (should look like):
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.zzeycmksnujfdvasxoti.supabase.co:5432/postgres
   ```

### 4. Update Environment Variables

**Update `.env.production`:**
```bash
# Backend Configuration
DATABASE_URL=postgresql://postgres:[NEW-PASSWORD]@db.zzeycmksnujfdvasxoti.supabase.co:5432/postgres
```

**Update Vercel:**
1. Go to: https://vercel.com/jenks18/chatbot/settings/environment-variables
2. Find `DATABASE_URL`
3. Click **Edit**
4. Paste the NEW connection string
5. Click **Save**

### 5. Initialize Database Tables

```bash
cd /Users/iannjenga/Desktop/chatbot
python3 init_supabase.py
```

Should see:
```
✅ Database connection successful!
✅ All tables created successfully!
```

### 6. Deploy

```bash
git add -A
git commit -m "fix: update database credentials and consolidate API for Vercel Hobby plan"
git push origin main
```

Vercel will automatically redeploy with new credentials.

### 7. Test

Visit: https://chatbot-y1ar.vercel.app

Send a message and check:
1. Response appears
2. Go to `/admin` - should see sessions
3. Send more messages
4. Refresh page - history should persist

---

## Alternative: Use SQLite Locally (For Testing)

If you just want to test locally without fixing Supabase:

```bash
# Create .env.local
cat > .env.local << 'EOF'
DEV_SQLITE=1
DEEPSEEK_API_KEY=sk-052da17567ab438bb0ea6e80b346a85d
DEEPSEEK_MODEL=deepseek-chat
NEXT_PUBLIC_API_URL=http://localhost:8000
OPENFDA_API_KEY=rH2feOTgRtT4WRuooKmDqiHlKuDqmhhJK6GqTeAb
NCBI_API_KEY=5141dbd81188ce3fc0547dbcf18a3fbe9209
EOF

# Start backend
cd backend
uvicorn main:app --reload --port 8000 &

# Start frontend
cd ..
npm run dev
```

Then test at http://localhost:3000

---

## Summary

**You need to:**
1. ✅ Reset Supabase database password
2. ✅ Get NEW connection string  
3. ✅ Update `.env.production` and Vercel
4. ✅ Initialize database tables
5. ✅ Deploy

**The widget code is ready** - it just needs a working database to save/load messages!
