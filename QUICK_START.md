# Quick Start: Database Clean + WordPress Widget

## ✅ Task 1: Clear Database (Fresh Start)

### Run this SQL in Supabase Dashboard:
1. Go to: https://zzeycmksnujfdvasxoti.supabase.co
2. Click "SQL Editor" → "New Query"
3. Paste and run:

```sql
DELETE FROM chat_logs;
ALTER SEQUENCE chat_logs_id_seq RESTART WITH 1;
```

✅ **Done!** All old conversation data deleted, starting fresh.

---

## ✅ Task 2: Add WordPress Chat Widget

### What You'll Get:
- 🟢 Floating green chat bubble (bottom-right corner)
- 💬 Click to expand full chatbot
- 📱 Mobile responsive
- ✨ Auto-opens on first visit

### Installation (3 Easy Steps):

**Step 1:** Copy the widget code
- Open: `/Users/iannjenga/Desktop/chatbot/widget-embed.html`
- Copy EVERYTHING from `<div id="toxicogpt-widget-container">` to `</script>`

**Step 2:** Add to WordPress
- Go to WordPress Admin
- Install plugin: "Insert Headers and Footers"
- Settings → Insert Headers and Footers
- Paste code in **"Scripts in Footer"** section
- Click "Save"

**Step 3:** Test
- Visit your WordPress site
- See green chat bubble in bottom-right? ✅
- Click it - chatbot opens!

---

## Widget Preview:

```
     Your WordPress Page
┌────────────────────────────────┐
│                                │
│  Page Content Here             │
│                                │
│                          ┌─────┤
│                          │ 🧬  │ ← Click this
│                          └─────┘
└────────────────────────────────┘

Opens to:
┌──────────────────────────┐
│ 🧬 ToxicoGPT        ✕   │
├──────────────────────────┤
│                          │
│  Chat Interface          │
│  (Full chatbot here)     │
│                          │
├──────────────────────────┤
│ Open in full page →      │
└──────────────────────────┘
```

---

## Customization:

### Change Colors (in the CSS):
```css
background: linear-gradient(135deg, #10b981 0%, #059669 100%);
/* Change to blue: */
background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
```

### Move to Bottom-Left:
```css
#toxicogpt-widget-container {
  left: 20px;   /* Change this */
  right: auto;  /* Add this */
}
```

### Disable Auto-Open:
Remove or comment out this section:
```javascript
// Auto-open widget on first visit
document.addEventListener('DOMContentLoaded', function() {
  // ... comment all this out
});
```

---

## Files Created:

1. **`clear_database.sql`** - SQL to wipe database
2. **`widget-embed.html`** - Ready-to-use widget code
3. **`WORDPRESS_WIDGET_GUIDE.md`** - Full documentation

---

## Need Help?

**Widget not showing?**
- Clear WordPress cache
- Check browser console for errors
- Make sure JavaScript is enabled

**Want different size?**
- Edit width/height in CSS:
  ```css
  #toxicogpt-widget-popup {
    width: 400px;  /* Change this */
    height: 650px; /* Change this */
  }
  ```

**Need it on specific pages only?**
- Use WordPress conditional tags:
  ```php
  <?php if (is_page('contact')) { ?>
    <!-- Widget code here -->
  <?php } ?>
  ```

---

🚀 **You're all set!** Database is ready to start fresh, and you have everything needed for the WordPress widget.
