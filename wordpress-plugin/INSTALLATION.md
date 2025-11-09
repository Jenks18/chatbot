# WordPress Plugin Installation Guide - No Coding Required! 🎉

## ✅ EASIEST METHOD: Use Existing WordPress Plugins

You DON'T need to code anything from scratch. Here are 3 super easy ways:

---

## Method 1: WPCode Plugin (Recommended - 5 minutes)

**Step 1:** Install WPCode
- WordPress Admin → Plugins → Add New
- Search: "WPCode - Insert Headers and Footers"
- Click "Install Now" → "Activate"

**Step 2:** Add Widget Code
- Go to: Code Snippets → Add Snippet
- Click: "Add Your Custom Code (New Snippet)"
- Name: "ToxicoGPT Widget"
- Code Type: Select "HTML Snippet"
- Paste this code:

```html
<!-- Copy from widget-embed.html file -->
<div id="toxicogpt-widget-container">
  <!-- All the widget HTML here -->
</div>
<style>/* All CSS here */</style>
<script>/* All JavaScript here */</script>
```

- Location: Select "Site Wide Footer"
- Click "Save Snippet" → Toggle "Active"

**Done!** Visit your site and see the chat button! ✅

---

## Method 2: Simple Custom CSS and JS (Also Easy)

**Step 1:** Install Plugin
- Plugins → Add New
- Search: "Simple Custom CSS and JS"
- Install and Activate

**Step 2:** Add Code
- Custom CSS & JS → Add Custom JS
- Paste the widget code from `widget-embed.html`
- Check "In Footer"
- Publish

**Done!** ✅

---

## Method 3: Elementor/WPBakery (If You Use Page Builders)

**For Elementor:**
- Edit any page with Elementor
- Add "HTML" widget
- Paste widget code
- Set to display site-wide

**For WPBakery:**
- Add "Raw HTML" element
- Paste code
- Save

---

## Method 4: Install Custom Plugin (Your Own Plugin!)

If you want it as a proper plugin with settings page:

**Step 1:** Create Plugin ZIP
```bash
cd /Users/iannjenga/Desktop/chatbot/wordpress-plugin
zip -r toxicogpt-widget.zip toxicogpt-widget.php readme.txt
```

**Step 2:** Upload to WordPress
- WordPress Admin → Plugins → Add New → Upload Plugin
- Choose `toxicogpt-widget.zip`
- Click "Install Now" → "Activate"

**Step 3:** Configure
- Settings → ToxicoGPT Widget
- Choose position, color, auto-open
- Save

**Features you get:**
- ✅ Settings page in WordPress admin
- ✅ Enable/disable toggle
- ✅ Color picker
- ✅ Position selector (left/right)
- ✅ Auto-open option
- ✅ Clean interface

---

## 🎯 Quick Comparison

| Method | Difficulty | Time | Settings Page | Best For |
|--------|-----------|------|--------------|----------|
| WPCode Plugin | ⭐ Easy | 5 min | No | Quick setup |
| Simple CSS/JS | ⭐ Easy | 5 min | No | Developers |
| Custom Plugin | ⭐⭐ Medium | 10 min | Yes | Full control |
| Elementor | ⭐ Easy | 3 min | No | Page builder users |

---

## 🚀 My Recommendation

**For non-developers:** Use **WPCode** (Method 1)
- Easiest to install
- No coding knowledge needed
- Can edit/disable easily
- Free forever

**For developers:** Use **Custom Plugin** (Method 4)
- Professional settings page
- Easy to customize
- Can distribute to clients
- Looks official

---

## 📦 What's Included in Custom Plugin

The `/wordpress-plugin/` folder contains:

1. **`toxicogpt-widget.php`** - Main plugin file
   - Admin settings page
   - Color picker
   - Position selector
   - Enable/disable toggle

2. **`readme.txt`** - WordPress plugin documentation
   - Installation instructions
   - FAQ
   - Changelog
   - Screenshots descriptions

---

## 🎨 After Installation

Test it works:
1. Visit your website
2. See green chat bubble in corner? ✅
3. Click it - chatbot opens!
4. Try asking: "What is panadol?"

Customize:
- Settings → ToxicoGPT Widget
- Change color, position, behavior
- Save and refresh your site

---

## ❓ Troubleshooting

**Widget not showing?**
- Clear WordPress cache (if using caching plugin)
- Check if JavaScript is enabled
- Try different browser

**Widget blocked by theme?**
- Increase z-index in CSS: `z-index: 99999;`
- Check theme's footer.php loads properly

**Iframe not loading?**
- Check your site allows iframes
- Verify chatbot URL is accessible
- Check browser console for errors

---

## 🎉 You're Done!

No coding from scratch needed! Just:
1. Pick a method (I recommend WPCode)
2. Copy/paste the widget code
3. Activate
4. Enjoy your chatbot!

Need help? Check the WORDPRESS_WIDGET_GUIDE.md for full details.
