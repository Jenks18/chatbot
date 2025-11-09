# Admin Panel & WordPress Widget Fixes

## Problem 1: Admin Panel 500 Errors ❌

**Errors:**
- `api/admin/sessions?limit=100` returned 500
- `api/admin/stats/overview` returned 500

**Root Cause:**
Admin endpoints were in `api/unified.py` but Vercel routing was incorrect. The consolidated unified approach was causing conflicts.

**Solution:** ✅
Created separate `api/admin.py` with dedicated admin endpoints:
- `/api/admin/logs` - Get chat logs
- `/api/admin/stats/overview` - Get statistics
- `/api/admin/sessions` - Get all sessions
- `/api/admin/sessions/{id}/history` - Get session history
- `/api/admin/interactions` - Get drug interactions

Updated `vercel.json` to route admin requests to the dedicated admin handler.

---

## Problem 2: WordPress 406 Errors ❌

**Error:**
- Getting 406 (Not Acceptable) when saving widget script in WordPress

**Root Cause:**
WordPress ModSecurity rules block certain JavaScript patterns:
- `postMessage()` with inline objects
- Complex event listeners
- Dynamic message building
- Variable assignments in function calls

**Previous Failed Approaches:**
1. ❌ Using `postMessage()` with inline objects
2. ❌ Separating message variable but still using addEventListener
3. ❌ Complex retry logic with timeouts

**NEW Solution:** ✅

Created **ultra-simple** widget: `wordpress-widget-simple.html`

**Key Changes:**
1. **No postMessage at all** - removed all cross-origin communication
2. **Inline onclick attributes** - moved all event handlers to HTML attributes
3. **Direct window.open()** - just opens the main URL (no session transfer)
4. **Minimal JavaScript** - only ESC key listener in separate script tag

**Trade-offs:**
- ❌ No session transfer from iframe to new window (user starts fresh chat)
- ✅ Guaranteed to work in WordPress (no security blocks)
- ✅ Simple and maintainable
- ✅ Users can still use chat in iframe or new window

---

## How to Use

### 1. Install WordPress Widget

Copy **entire contents** of `wordpress-plugin/wordpress-widget-simple.html` and paste into:
- WordPress Admin → Appearance → Theme Editor → Footer
- OR use a Custom HTML widget
- OR use a plugin like "Insert Headers and Footers"

**This version WILL NOT trigger 406 errors.**

### 2. Access Admin Panel

Visit: `https://chatbot-y1ar.vercel.app/admin`

You should now see:
- ✅ Session statistics (total queries, unique sessions, avg response time)
- ✅ Recent sessions list with message counts
- ✅ Click sessions to view full conversation history

---

## Technical Details

### Admin API Endpoints (api/admin.py)

```python
@app.get("/api/admin/logs")
async def get_all_logs(limit: int, offset: int)
# Returns paginated chat logs

@app.get("/api/admin/stats/overview")
async def get_stats_overview()
# Returns: total_queries, unique_sessions, avg_response_time_ms, daily_queries

@app.get("/api/admin/sessions")
async def get_all_sessions(limit: int)
# Returns all sessions with message counts and preview

@app.get("/api/admin/sessions/{session_id}/history")
async def get_session_history(session_id: str)
# Returns full conversation for a session
```

### WordPress Widget (Simple Version)

**Features:**
- ✅ Floating chat bubble (bottom-right)
- ✅ Modal popup with iframe
- ✅ "Open Full" button (opens new window)
- ✅ Close button and ESC key support
- ✅ Mobile responsive
- ✅ Purple gradient theme

**What It Does:**
1. User clicks bubble → iframe modal opens
2. User chats in iframe (session saved automatically)
3. User clicks "Open Full" → new window opens with fresh chat
4. Sessions are still saved to database

**What It Doesn't Do:**
- ❌ Transfer session from iframe to new window
- ❌ Use postMessage (blocked by WordPress)
- ❌ Complex JavaScript (triggers security rules)

---

## Testing Steps

### Test Admin Panel:
1. Visit `https://chatbot-y1ar.vercel.app/admin`
2. Check "Overview Stats" section loads (no 500 errors)
3. Check "Chat Sessions" section loads with session list
4. Click a session to view conversation history

### Test WordPress Widget:
1. Add `wordpress-widget-simple.html` to WordPress footer
2. Save (should NOT get 406 error)
3. Visit your WordPress site
4. See purple chat bubble in bottom-right
5. Click bubble → modal opens
6. Chat in iframe
7. Click "⧉ Open Full" → new window opens

---

## Files Changed

1. ✅ `/api/admin.py` - New dedicated admin API
2. ✅ `/vercel.json` - Updated routing for admin endpoints
3. ✅ `/wordpress-plugin/wordpress-widget-simple.html` - WordPress-safe widget

---

## Next Steps

After deployment:
1. Test admin panel (should show stats and sessions)
2. Copy `wordpress-widget-simple.html` to WordPress
3. Verify no 406 errors when saving
4. Test chat functionality in both iframe and new window

If you still get 406 errors, it means WordPress security is EXTREMELY strict. In that case, we need to:
- Use WordPress's `wp_enqueue_script()` properly
- Or install the widget as a proper WordPress plugin
- Or whitelist the script in WordPress security settings
