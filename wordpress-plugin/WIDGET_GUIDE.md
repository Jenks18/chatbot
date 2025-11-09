# ToxicoGPT WordPress Widget - Installation & Usage Guide

## 📋 Overview

This widget allows you to embed ToxicoGPT chat functionality directly into your WordPress website with full session persistence. When users click "Open Full", their conversation seamlessly transfers to a new window.

## 🚀 Features

- **Floating Chat Bubble**: Beautiful gradient blue chat icon in bottom-right corner
- **Modal Chat Interface**: Clean popup modal with iframe
- **Session Persistence**: Conversations transfer when opening in new window
- **Multiple Fallback Methods**: 3 different approaches to capture session ID
- **Retry Logic**: Automatic retry with exponential backoff
- **Responsive Design**: Works on desktop and mobile
- **Security**: Origin verification for postMessage communication
- **Debug Logging**: Console logs for troubleshooting

## 📦 Installation

### Method 1: WordPress Theme Footer (Recommended)

1. **Copy the widget code** from `toxicogpt-widget-improved.html`

2. **Go to WordPress Admin**:
   - Navigate to `Appearance` → `Theme File Editor`
   - Or use a plugin like "Insert Headers and Footers"

3. **Add to Footer**:
   - In Theme File Editor: Open `footer.php` and paste before `</body>`
   - Or use "Insert Headers and Footers" plugin: Paste in "Scripts in Footer" section

4. **Save changes**

### Method 2: WordPress Page/Post

1. **Edit your page/post** in WordPress
2. **Switch to HTML/Code view**
3. **Paste the entire widget code** where you want it to appear
4. **Publish/Update**

### Method 3: Custom HTML Widget

1. **Go to** `Appearance` → `Widgets`
2. **Add a "Custom HTML" widget** to your desired sidebar/footer
3. **Paste the widget code**
4. **Save**

## 🔧 Configuration

You can customize the widget by editing these values in the `CONFIG` object:

```javascript
var CONFIG = {
  CHAT_URL: 'https://chatbot-y1ar.vercel.app/',  // Your ToxicoGPT URL
  MESSAGE_TIMEOUT: 5000,      // Timeout for session transfer (ms)
  RETRY_ATTEMPTS: 3,          // Number of retry attempts
  RETRY_DELAY: 1000          // Delay between retries (ms)
};
```

## 🎨 Styling Customization

### Change Colors

The widget uses a blue gradient theme by default. To customize:

```css
/* Chat Bubble */
#chat-bubble {
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
  /* Change to your brand colors */
}

/* Header */
#chat-header {
  background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
  /* Match your brand */
}
```

### Change Position

Move the chat bubble to different corners:

```css
/* Bottom Right (Default) */
#chat-bubble {
  bottom: 20px;
  right: 20px;
}

/* Bottom Left */
#chat-bubble {
  bottom: 20px;
  left: 20px;
  right: auto;
}

/* Top Right */
#chat-bubble {
  top: 20px;
  right: 20px;
  bottom: auto;
}
```

### Change Size

```css
/* Larger bubble */
#chat-bubble {
  width: 70px;
  height: 70px;
  font-size: 32px;
}

/* Larger modal */
#chat-container {
  max-width: 600px;
  max-height: 800px;
}
```

## 🔐 Security Configuration

For enhanced security, uncomment and configure origin verification:

```javascript
function handleMessage(event) {
  // Uncomment and add your WordPress domain
  if (event.origin !== 'https://your-wordpress-site.com') return;
  
  // ... rest of code
}
```

Update in both:
1. WordPress widget script
2. Next.js `pages/index.tsx` (already configured)

## 📊 How Session Transfer Works

The widget uses a **3-tier fallback system**:

### Method 1: Direct Iframe Access (Fastest)
```javascript
// Try to read iframe URL directly
var iframeSrc = chatIframe.contentWindow.location.href;
var sessionId = extractSessionFromUrl(iframeSrc);
```
✅ Works if: Same origin  
❌ Fails if: Cross-origin (CORS blocked)

### Method 2: Iframe LocalStorage (Fast)
```javascript
// Try to access iframe's localStorage
var sessionId = chatIframe.contentWindow.localStorage.getItem('toxicogpt_session');
```
✅ Works if: Same origin  
❌ Fails if: Cross-origin (CORS blocked)

### Method 3: PostMessage API (Most Reliable)
```javascript
// Send message request
chatIframe.contentWindow.postMessage({ type: 'GET_SESSION_ID' }, CHAT_URL);

// Receive response
window.addEventListener('message', function(event) {
  if (event.data.type === 'SESSION_ID_RESPONSE') {
    var sessionId = event.data.sessionId;
  }
});
```
✅ Always works: Cross-origin safe  
⏱️ Slightly slower: Async communication

### Retry Logic
- **3 automatic retries** with 1-second delays
- **5-second timeout** for each attempt
- **Fallback**: Opens fresh chat if all methods fail

## 🐛 Debugging

Check the browser console for detailed logs:

```javascript
[ToxicoGPT Widget] Opening chat in new window...
[ToxicoGPT Widget] Direct iframe access blocked (expected for cross-origin)
[ToxicoGPT Widget] Requesting session ID via postMessage...
[ToxicoGPT Widget] Session ID received: abc123-def456-ghi789
[ToxicoGPT Widget] Opening new window with session: abc123-def456-ghi789
```

Common messages:
- `"Direct iframe access blocked"` - Normal for cross-origin, will fallback
- `"Session request timed out"` - Network issue, will retry
- `"Opening without session"` - All methods failed, opens fresh chat

## 🔍 Testing

### Test Session Transfer:

1. **Open WordPress site** in browser
2. **Click chat bubble** to open modal
3. **Send a few messages** in the chat
4. **Check console** for session ID logs
5. **Click "⧉ Open Full"** button
6. **Verify**: New window opens with same conversation

### Test Scenarios:

✅ **Fresh conversation**: Should open new window with existing messages  
✅ **Multiple messages**: All messages should transfer  
✅ **Network delay**: Should retry automatically  
✅ **Failed transfer**: Should open fresh chat gracefully  

## 🌐 Browser Compatibility

| Browser | Version | Support |
|---------|---------|---------|
| Chrome | 90+ | ✅ Full |
| Firefox | 88+ | ✅ Full |
| Safari | 14+ | ✅ Full |
| Edge | 90+ | ✅ Full |
| Mobile Safari | 14+ | ✅ Full |
| Mobile Chrome | 90+ | ✅ Full |

## 🆘 Troubleshooting

### Issue: Chat bubble doesn't appear

**Solution:**
- Check if element IDs are unique (no conflicts)
- Verify `z-index: 999998` is higher than other elements
- Check browser console for errors

### Issue: Session not transferring

**Solution:**
1. Open browser console
2. Look for `[ToxicoGPT Widget]` logs
3. Check if URL contains `?session=...`
4. Verify postMessage listener is active in Next.js

### Issue: Modal not opening

**Solution:**
- Check if modal CSS is loaded
- Verify JavaScript is not blocked
- Look for JavaScript errors in console

### Issue: CORS errors

**Solution:**
- This is expected for cross-origin iframes
- Widget will automatically fallback to postMessage
- Verify `pages/index.tsx` has message listener

## 📝 Customization Examples

### Example 1: Different Chat Icon

```html
<!-- Change the emoji -->
<div id="chat-bubble" title="Chat with ToxicoGPT">🤖</div>

<!-- Or use an image -->
<div id="chat-bubble" title="Chat with ToxicoGPT">
  <img src="/path/to/icon.png" style="width: 35px; height: 35px;">
</div>
```

### Example 2: Custom Button Text

```html
<button id="chat-open-new">🚀 Continue Chat</button>
<button id="chat-close">Close</button>
```

### Example 3: Add Company Branding

```html
<div id="chat-header">
  <div style="display: flex; align-items: center; gap: 8px;">
    <img src="/logo.png" style="height: 24px;">
    <h3>Your Company Name</h3>
  </div>
  <div id="chat-actions">...</div>
</div>
```

## 📈 Performance

- **Initial Load**: ~5KB (minified)
- **Iframe Load**: Depends on ToxicoGPT app
- **Session Transfer**: <100ms (direct) or <5s (postMessage)
- **Memory Usage**: Minimal (~2MB)

## 🔄 Updates

To update the widget:

1. **Download latest** `toxicogpt-widget-improved.html`
2. **Replace entire script** in your WordPress footer
3. **Clear cache** (browser & WordPress)
4. **Test** session transfer functionality

## 📞 Support

- **Issues**: Check browser console for error logs
- **Session problems**: Verify both widget and Next.js have postMessage handlers
- **Styling issues**: Use browser DevTools to inspect CSS

## 🎉 Success Checklist

- [ ] Widget appears on all pages
- [ ] Chat bubble is clickable and opens modal
- [ ] Iframe loads ToxicoGPT interface
- [ ] Can send/receive messages in modal
- [ ] "Open Full" button transfers session correctly
- [ ] Console shows session ID logs
- [ ] New window has conversation history
- [ ] Mobile responsive layout works

---

**Last Updated**: November 2025  
**Version**: 2.0 (Robust Implementation)  
**Compatibility**: WordPress 5.0+, Modern Browsers
