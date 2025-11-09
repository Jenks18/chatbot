# 🚀 Quick Start - WordPress Widget

## Copy & Paste into WordPress Footer

Just copy the entire `toxicogpt-widget-improved.html` file into your WordPress footer!

---

## 📍 Where to Add:

### Option 1: Theme File Editor
`Appearance` → `Theme File Editor` → `footer.php` (before `</body>`)

### Option 2: Plugin (Easiest)
Install "Insert Headers and Footers" plugin → Paste in "Scripts in Footer"

---

## ✅ What You Get:

1. **Floating Blue Chat Bubble** (bottom-right corner)
2. **Modal Chat Interface** (opens when clicked)
3. **"Open Full" Button** (transfers conversation to new window)
4. **Session Persistence** (conversation continues in new window)

---

## 🔧 How Session Transfer Works:

```
User chats in WordPress modal (iframe)
     ↓
Clicks "⧉ Open Full" button
     ↓
Widget tries 3 methods to get session ID:
  1. Direct iframe URL read
  2. Iframe localStorage access
  3. PostMessage API (most reliable)
     ↓
Opens new window with session URL
     ↓
New window loads with full conversation history! 🎉
```

---

## 🎨 Quick Customization:

### Change Colors (in CSS section):
```css
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Change Chat URL (in JavaScript CONFIG):
```javascript
CHAT_URL: 'https://your-domain.com/',
```

### Change Position:
```css
/* Move to bottom-left */
#chat-bubble {
  left: 20px;
  right: auto;
}
```

---

## 🐛 Debugging:

Open browser console (F12) and look for:
```
[ToxicoGPT Widget] Opening chat in new window...
[ToxicoGPT Widget] Session ID received: abc123...
[ToxicoGPT Widget] Opening new window with session: abc123...
```

---

## ✨ Features:

- ✅ **3 Fallback Methods** for session capture
- ✅ **Auto-Retry** (3 attempts with 1s delay)
- ✅ **5-Second Timeout** per attempt
- ✅ **Origin Security** verification
- ✅ **Debug Logging** for troubleshooting
- ✅ **Responsive** mobile design
- ✅ **Graceful Degradation** (opens fresh chat if transfer fails)

---

## 🎯 Test It:

1. Add widget to WordPress
2. Click chat bubble → Chat opens
3. Send message → "Hello!"
4. Click "⧉ Open Full" button
5. New window opens → Same conversation! ✅

---

## 📖 Full Documentation:

See `WIDGET_GUIDE.md` for:
- Detailed installation steps
- Advanced configuration
- Security settings
- Browser compatibility
- Troubleshooting guide
- Customization examples

---

**That's it! Your chat widget is ready! 🎉**
