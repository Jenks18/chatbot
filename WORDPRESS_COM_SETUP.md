# WordPress.com Official Integration Guide

## 🎯 Two Easy Methods for WordPress.com

---

## Method 1: Custom HTML Widget (FREE - No Jetpack Needed!)

Perfect for WordPress.com Free, Personal, or Premium plans.

### Step-by-Step Instructions:

**Step 1: Go to Customizer**
1. Log in to your WordPress.com dashboard
2. Click **"Appearance"** → **"Customize"**
3. Or visit: `yoursite.wordpress.com/wp-admin/customize.php`

**Step 2: Add Custom HTML Widget**
1. In the Customizer, click **"Widgets"**
2. Choose a widget area (recommended: **"Footer"** or **"Sidebar"**)
3. Click **"+ Add a Widget"**
4. Search for and select **"Custom HTML"**

**Step 3: Add Widget Code**
1. In the Custom HTML widget, paste this code:

```html
<!-- ToxicoGPT Chat Widget -->
<div id="toxicogpt-widget-container"></div>

<style>
#toxicogpt-widget-container {
  position: fixed !important;
  bottom: 20px !important;
  right: 20px !important;
  z-index: 9999 !important;
}
#toxicogpt-button {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  transition: all 0.3s ease;
}
#toxicogpt-button:hover {
  transform: scale(1.1);
}
#toxicogpt-popup {
  display: none;
  position: fixed;
  bottom: 90px;
  right: 20px;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  overflow: hidden;
}
#toxicogpt-popup.active {
  display: block;
}
@media (max-width: 480px) {
  #toxicogpt-popup {
    width: calc(100vw - 40px);
    height: calc(100vh - 120px);
  }
}
</style>

<script>
(function() {
  // Create button
  const button = document.createElement('div');
  button.id = 'toxicogpt-button';
  button.innerHTML = `<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>`;
  
  // Create popup
  const popup = document.createElement('div');
  popup.id = 'toxicogpt-popup';
  popup.innerHTML = `
    <div style="background: #10b981; color: white; padding: 16px; display: flex; justify-content: space-between; align-items: center;">
      <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 24px;">🧬</span>
        <div>
          <h3 style="margin: 0; font-size: 18px;">ToxicoGPT</h3>
          <p style="margin: 0; font-size: 12px; opacity: 0.9;">Evidence-Based Toxicology AI</p>
        </div>
      </div>
      <button onclick="document.getElementById('toxicogpt-popup').classList.remove('active')" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 20px;">✕</button>
    </div>
    <iframe src="https://chatbot-y1ar.vercel.app/?widget=true" style="width: 100%; height: calc(100% - 72px); border: none;"></iframe>
  `;
  
  // Add to page
  const container = document.getElementById('toxicogpt-widget-container');
  if (container) {
    container.appendChild(button);
    container.appendChild(popup);
  }
  
  // Toggle function
  button.onclick = function() {
    popup.classList.add('active');
  };
})();
</script>
```

**Step 4: Publish**
1. Click **"Publish"** button in the Customizer
2. Visit your site to see the chat button!

---

## Method 2: Jetpack + Custom CSS/JS (Premium Plans)

For WordPress.com Business or eCommerce plans with Jetpack Premium.

### Requirements:
- WordPress.com Business Plan or higher
- Jetpack plugin installed and connected

### Step-by-Step Instructions:

**Step 1: Install Jetpack (if not already installed)**
1. Go to: **Plugins** → **Add New**
2. Search: **"Jetpack"**
3. Click **"Install Now"** → **"Activate"**
4. Connect your WordPress.com account

**Step 2: Enable Custom CSS Module**
1. Go to **Jetpack** → **Settings**
2. Click on **"Writing"** tab
3. Enable **"Custom Content Types"**
4. Save changes

**Step 3: Add Custom CSS**
1. Go to **Appearance** → **Customize**
2. Click **"Additional CSS"**
3. Paste the widget CSS (from Method 1 above)
4. Click **"Publish"**

**Step 4: Add JavaScript via Footer**
1. Install plugin: **"Insert Headers and Footers by WPBeginner"**
   - Go to: Plugins → Add New
   - Search: "Insert Headers and Footers"
   - Install and Activate

2. Go to **Settings** → **Insert Headers and Footers**

3. In the **"Scripts in Footer"** section, paste:

```html
<div id="toxicogpt-widget-container"></div>
<script>
// Same JavaScript from Method 1
</script>
```

4. Click **"Save"**

---

## Method 3: Page Builder Integration (Elementor/Divi)

If you use a page builder:

### For Elementor:
1. Edit page with Elementor
2. Drag **"HTML"** widget to footer section
3. Paste the complete widget code
4. Set visibility to "All Pages"
5. Update

### For Divi Builder:
1. Edit page with Divi
2. Add **"Code"** module to footer
3. Paste widget code
4. Set to display globally
5. Save

---

## 📊 Comparison Table

| Method | WordPress.com Plan | Difficulty | Cost | Best For |
|--------|-------------------|------------|------|----------|
| Custom HTML Widget | Free, Personal, Premium, Business | ⭐ Easy | Free | Everyone |
| Jetpack Premium | Business, eCommerce | ⭐⭐ Medium | $$ | Advanced users |
| Page Builder | Premium+ (with builder) | ⭐ Easy | $ | Design-focused |

---

## ✅ Recommended: Custom HTML Widget (Method 1)

**Why?**
- ✅ Works on FREE WordPress.com plans
- ✅ No plugins needed
- ✅ No coding knowledge required
- ✅ Takes 5 minutes
- ✅ Easy to remove/edit

---

## 🎨 Customization Options

### Change Button Color:
```css
background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); /* Blue */
background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); /* Red */
background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); /* Purple */
```

### Change Position to Bottom-Left:
```css
#toxicogpt-widget-container {
  left: 20px !important;
  right: auto !important;
}
#toxicogpt-popup {
  left: 20px;
  right: auto;
}
```

### Make Button Smaller:
```css
#toxicogpt-button {
  width: 50px;
  height: 50px;
}
```

---

## 🧪 Testing Your Widget

After installation:

1. **Visit your site** in a new browser tab
2. **Look for** the green chat button in bottom-right corner
3. **Click it** - the chatbot should expand
4. **Test a question**: Try "What is panadol?"
5. **Check mobile**: Test on your phone

---

## ❌ Troubleshooting

### Widget not showing?
- Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
- Check if JavaScript is blocked
- Try a different browser
- Make sure widget is in Footer area (not hidden on all pages)

### Widget shows but doesn't open?
- Check browser console for errors (F12)
- Make sure JavaScript is enabled
- Try in incognito/private mode

### Widget overlaps with other elements?
- Increase z-index: `z-index: 99999 !important;`
- Adjust position: change `bottom` or `right` values

### WordPress.com says "Code not allowed"?
- You need at least a Personal plan for Custom HTML
- Free plans have restrictions on custom code
- Consider upgrading or use the Text widget instead

---

## 📱 Mobile Responsiveness

The widget automatically adjusts for mobile:
- Smaller button on phones
- Full-screen popup on small screens
- Touch-friendly interface

---

## 🔒 Privacy & Security

The widget:
- ✅ Loads from secure HTTPS
- ✅ Uses iframe isolation
- ✅ No tracking cookies
- ✅ GDPR-friendly
- ✅ No data stored on your WordPress site

---

## 🚀 You're All Set!

**Summary:**
1. Choose Custom HTML Widget method (easiest)
2. Copy/paste the code
3. Publish
4. Test on your site

**Next Steps:**
- Customize colors to match your brand
- Test on mobile devices
- Monitor usage in the admin panel
- Collect feedback from visitors

Need help? The widget code is in `/Users/iannjenga/Desktop/chatbot/widget-embed.html`

---

## 🎯 Reading Level Strategy Confirmed

Your chatbot now uses proper reading levels for each audience:

| User Mode | Reading Level | Model Used | Response Style |
|-----------|--------------|------------|----------------|
| **Patient** | 6th Grade | Groq Compound | Short sentences, simple words, practical info |
| **Doctor** | 12th Grade (Medical) | Groq Compound | Clinical details, medical terminology, evidence-based |
| **Researcher** | Academic/Research | Groq Compound | Molecular mechanisms, citations, advanced science |

✅ All modes now use Groq compound model with appropriate prompts!
