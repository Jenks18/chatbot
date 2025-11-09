# Session Persistence & Database Fix - Complete Solution

## 🔴 Root Cause Identified

**The real issue:** Your Supabase database connection is broken. The error "Tenant or user not found" means your Supabase project credentials are invalid, expired, or the project was deleted.

**This is why:**
- ✅ Chat messages are NOT being saved to database
- ✅ Admin panel shows NO data (because there IS no data)
- ✅ Session persistence doesn't work (no history to load)
- ✅ 406 errors appear (from failed database operations)

## 🎯 What I Fixed

### 1. Frontend Session Management ✅
**File: `pages/index.tsx`**

- ✅ Load session ID from URL on page load
- ✅ Load chat history when session exists in URL
- ✅ Save session to localStorage and URL
- ✅ Update URL when creating new chat
- ✅ Show loading indicator while fetching history

**Changes:**
```typescript
// Now loads history on mount
const loadChatHistory = async (sid: string) => {
  const history = await apiService.getChatHistory(sid, 100);
  // Converts DB logs to message format and displays them
};

// Checks URL for session parameter
const urlSessionId = urlParams.get('session');
if (urlSessionId) {
  loadChatHistory(urlSessionId); // Loads history!
}
```

### 2. WordPress Widget Communication ✅
**File: `wordpress-plugin/wordpress-widget-script.html`**

- ✅ Track iframe load status
- ✅ Extract session ID from iframe URL
- ✅ Better postMessage handling
- ✅ Multiple fallback mechanisms for session extraction
- ✅ Debug logging to track session flow

**Changes:**
```javascript
// Now tracks session and waits for iframe
var iframeLoaded = false;
var currentSessionId = null;

// Extracts session from iframe URL
chatIframe.addEventListener('load', function() {
  var sessionMatch = iframeSrc.match(/[?&]session=([^&]+)/);
  if (sessionMatch) currentSessionId = sessionMatch[1];
});
```

### 3. API Type Definitions ✅
**File: `services/api.ts`**

- ✅ Extended ChatLog interface to include evidence and consumer_summary
- ✅ Proper TypeScript types for database metadata

### 4. Test Infrastructure ✅

Created:
- ✅ `test-widget.html` - Comprehensive widget testing page
- ✅ `test_database.py` - Database connection tester
- ✅ `setup-sqlite.sh` - Quick local setup script
- ✅ `DATABASE_FIX_REQUIRED.md` - Complete troubleshooting guide

## ⚠️ What Still Needs Fixing

### The Database Connection

**Current Status:** BROKEN ❌
```
Supabase project credentials are invalid or expired
```

**You need to choose one option:**

### Option A: Fix Supabase (For Production)

1. **Check Supabase Dashboard:**
   ```
   https://supabase.com/dashboard
   ```
   - Verify project exists and is active
   - Get fresh connection string

2. **Update `.env.production`:**
   ```bash
   DATABASE_URL=postgresql://postgres.[NEW_PROJECT]:[NEW_PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
   ```

3. **Initialize Tables:**
   ```bash
   cd backend
   python3 -c "from db.database import Base, engine; Base.metadata.create_all(engine)"
   ```

4. **Update Vercel:**
   - Go to Vercel Dashboard → Settings → Environment Variables
   - Update `DATABASE_URL`
   - Redeploy

### Option B: Use SQLite (For Local Testing)

**Fastest way to test right now:**

```bash
# Run the setup script
./setup-sqlite.sh

# Start backend (Terminal 1)
cd backend
uvicorn main:app --reload --port 8000

# Start frontend (Terminal 2)
npm run dev

# Open browser
open http://localhost:3000
```

This will:
- ✅ Create local SQLite database
- ✅ Initialize all tables
- ✅ Allow testing without Supabase
- ✅ Everything works locally

## 📋 Testing Checklist

Once database is connected:

### 1. Test Database Connection
```bash
python3 test_database.py
```

Expected output:
```
✅ Database connection successful!
📊 Found 5 tables:
   - api_cache
   - chat_logs
   - interactions
   - references
   - sessions
```

### 2. Test Chat & Save
1. Open http://localhost:3000
2. Send a message: "What is acetaminophen?"
3. Check if response appears
4. **Verify in database:**
   ```bash
   python3 test_database.py
   ```
   Should show: "💬 Chat logs in database: 1"

### 3. Test Session Persistence
1. Send 2-3 messages in the chat
2. Note the session ID in URL (e.g., `/?session=abc-123`)
3. Click "Open Full" or open URL in new window
4. **Expected:** All messages load in new window ✅

### 4. Test Admin Panel
1. Open http://localhost:3000/admin
2. **Expected:** See sessions list with message counts
3. Click on a session
4. **Expected:** See full conversation history

### 5. Test WordPress Widget
1. Open http://localhost:8080/test-widget.html
2. Click chat bubble
3. Send messages
4. Click "⧉ Open Full"
5. **Expected:** New window opens with conversation intact

## 🚀 Quick Start (Right Now)

**To test immediately with SQLite:**

```bash
# 1. Setup (one time)
./setup-sqlite.sh

# 2. Start backend
cd backend
uvicorn main:app --reload --port 8000 &

# 3. Start frontend
cd ..
npm run dev &

# 4. Test widget server
cd wordpress-plugin
python3 -m http.server 8080 &

# 5. Open browser
open http://localhost:3000
open http://localhost:8080/test-widget.html
```

## 📊 Architecture Flow

### Before (Broken):
```
User → Chat Widget → Frontend → Backend → ❌ Database (FAILED)
                                           ↓
                                    No data saved
                                           ↓
Admin Panel: Empty, Widget: No history ❌
```

### After (Fixed):
```
User → Chat Widget → Frontend → Backend → ✅ Database (Connected)
                                           ↓
                                    Messages saved
                                           ↓
Admin Panel: Shows data ✅, Widget: Loads history ✅
```

## 🔧 Files Modified

1. **`pages/index.tsx`**
   - Added `loadChatHistory()` function
   - Load history on mount if session in URL
   - Show loading indicator

2. **`services/api.ts`**
   - Extended `ChatLog` interface
   - Added metadata types

3. **`wordpress-plugin/wordpress-widget-script.html`**
   - Session tracking variables
   - Iframe load monitoring
   - Better "Open Full" logic
   - Debug logging

4. **Created:**
   - `test_database.py` - DB connection tester
   - `setup-sqlite.sh` - Quick setup script
   - `DATABASE_FIX_REQUIRED.md` - Fix guide
   - `test-widget.html` - Widget test page
   - `SESSION_PERSISTENCE_FIX.md` - Technical docs

## ✅ What Works Now (With Working DB)

- ✅ Frontend loads history from URL
- ✅ Widget tracks and passes session ID
- ✅ "Open Full" preserves conversation
- ✅ Admin panel can display data
- ✅ TypeScript types are correct
- ✅ Loading indicators show progress

## ❌ What Doesn't Work (Until DB Fixed)

- ❌ Saving messages (no database)
- ❌ Loading history (no data to load)
- ❌ Admin panel (no data to display)
- ❌ Session persistence (no saved messages)

## 🎯 Next Steps

**Choose your path:**

### Path 1: Production (Supabase)
1. Fix Supabase credentials
2. Update Vercel environment variables
3. Initialize database tables
4. Deploy and test

### Path 2: Local Development (SQLite)
1. Run `./setup-sqlite.sh`
2. Start backend and frontend
3. Test everything locally
4. Deploy to production later with Supabase

### Path 3: Local PostgreSQL
1. Install PostgreSQL locally
2. Create database
3. Update `.env.local`
4. Initialize tables
5. Test locally

## 📞 Support

**Database connection issues?**
- Check `DATABASE_FIX_REQUIRED.md` for detailed troubleshooting

**Widget not working?**
- Open `test-widget.html` to see debug logs
- Check browser console for session tracking

**Admin panel empty?**
- First fix database connection
- Then verify messages are being saved with `test_database.py`

---

**Status:** 
- ✅ Code fixes complete
- ⏳ Waiting for database connection
- 🧪 Ready for testing with SQLite

**Last Updated:** November 9, 2025
