# ToxicoGPT WordPress Widget Integration Guide

## Overview
Convert your ToxicoGPT chatbot into a floating chat widget that appears in the bottom-right corner of WordPress pages (like Intercom, Drift, or Zendesk Chat).

---

## Option 1: Simple Embed Code (Recommended)

### Step 1: Create the Widget HTML
Add this code to your WordPress site (via Custom HTML widget, footer.php, or a plugin like "Insert Headers and Footers"):

```html
<!-- ToxicoGPT Chat Widget -->
<div id="toxicogpt-widget-container">
  <!-- Minimized Widget Button -->
  <div id="toxicogpt-widget-button" onclick="toggleToxicoWidget()">
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
    </svg>
    <span id="widget-badge" class="notification-badge">1</span>
  </div>

  <!-- Expanded Widget (Chat Interface) -->
  <div id="toxicogpt-widget-popup" style="display: none;">
    <div class="widget-header">
      <div class="widget-title">
        <span class="widget-icon">🧬</span>
        <div>
          <h3>ToxicoGPT</h3>
          <p class="widget-subtitle">Evidence-Based Toxicology AI</p>
        </div>
      </div>
      <button onclick="toggleToxicoWidget()" class="widget-close">✕</button>
    </div>
    
    <!-- Embed your chatbot in an iframe -->
    <iframe 
      id="toxicogpt-iframe"
      src="https://chatbot-y1ar.vercel.app/?widget=true" 
      frameborder="0"
      allow="clipboard-write"
    ></iframe>
    
    <div class="widget-footer">
      <a href="https://chatbot-y1ar.vercel.app" target="_blank">Open in full page →</a>
    </div>
  </div>
</div>

<style>
/* Widget Container */
#toxicogpt-widget-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* Minimized Button */
#toxicogpt-widget-button {
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
  position: relative;
}

#toxicogpt-widget-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
}

/* Notification Badge */
.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: #ef4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: bold;
  border: 2px solid white;
}

/* Expanded Popup */
#toxicogpt-widget-popup {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 380px;
  height: 600px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Widget Header */
.widget-header {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.widget-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.widget-icon {
  font-size: 24px;
}

.widget-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.widget-subtitle {
  margin: 0;
  font-size: 12px;
  opacity: 0.9;
}

.widget-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.widget-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* Iframe Container */
#toxicogpt-iframe {
  flex: 1;
  width: 100%;
  border: none;
}

/* Widget Footer */
.widget-footer {
  padding: 12px 16px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  text-align: center;
}

.widget-footer a {
  color: #10b981;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
}

.widget-footer a:hover {
  text-decoration: underline;
}

/* Mobile Responsive */
@media (max-width: 480px) {
  #toxicogpt-widget-popup {
    width: calc(100vw - 40px);
    height: calc(100vh - 100px);
    max-height: 600px;
  }
}
</style>

<script>
function toggleToxicoWidget() {
  const popup = document.getElementById('toxicogpt-widget-popup');
  const button = document.getElementById('toxicogpt-widget-button');
  const badge = document.getElementById('widget-badge');
  
  if (popup.style.display === 'none') {
    popup.style.display = 'flex';
    button.style.display = 'none';
    // Hide notification badge when opened
    if (badge) badge.style.display = 'none';
  } else {
    popup.style.display = 'none';
    button.style.display = 'flex';
  }
}

// Auto-open widget on first visit (optional)
document.addEventListener('DOMContentLoaded', function() {
  const hasVisited = localStorage.getItem('toxicogpt-visited');
  if (!hasVisited) {
    setTimeout(() => {
      toggleToxicoWidget();
      localStorage.setItem('toxicogpt-visited', 'true');
    }, 3000); // Open after 3 seconds
  }
});
</script>
```

---

## Option 2: WordPress Plugin Method

### Create a Custom Plugin

1. Create a new folder: `/wp-content/plugins/toxicogpt-widget/`

2. Create `toxicogpt-widget.php`:

```php
<?php
/**
 * Plugin Name: ToxicoGPT Chat Widget
 * Description: Adds a floating ToxicoGPT chatbot widget to your WordPress site
 * Version: 1.0.0
 * Author: Your Name
 */

// Prevent direct access
if (!defined('ABSPATH')) exit;

// Add widget to footer
function toxicogpt_widget() {
    ?>
    <!-- ToxicoGPT Widget -->
    <div id="toxicogpt-widget-container">
        <!-- Widget code from Option 1 above -->
    </div>
    <?php
}
add_action('wp_footer', 'toxicogpt_widget');

// Enqueue styles and scripts
function toxicogpt_enqueue_assets() {
    wp_enqueue_style('toxicogpt-widget', plugins_url('widget.css', __FILE__));
    wp_enqueue_script('toxicogpt-widget', plugins_url('widget.js', __FILE__), array(), '1.0.0', true);
}
add_action('wp_enqueue_scripts', 'toxicogpt_enqueue_assets');

// Add settings page
function toxicogpt_settings_page() {
    add_options_page(
        'ToxicoGPT Settings',
        'ToxicoGPT Widget',
        'manage_options',
        'toxicogpt-settings',
        'toxicogpt_settings_page_html'
    );
}
add_action('admin_menu', 'toxicogpt_settings_page');

function toxicogpt_settings_page_html() {
    ?>
    <div class="wrap">
        <h1>ToxicoGPT Widget Settings</h1>
        <form method="post" action="options.php">
            <table class="form-table">
                <tr>
                    <th>Widget Position</th>
                    <td>
                        <select name="toxicogpt_position">
                            <option value="bottom-right">Bottom Right</option>
                            <option value="bottom-left">Bottom Left</option>
                        </select>
                    </td>
                </tr>
                <tr>
                    <th>Auto-open on first visit</th>
                    <td>
                        <input type="checkbox" name="toxicogpt_autoopen" value="1" />
                    </td>
                </tr>
            </table>
            <?php submit_button(); ?>
        </form>
    </div>
    <?php
}
?>
```

---

## Option 3: Modify Your Chatbot for Widget Mode

Update your chatbot to detect widget mode and adjust the UI:

### Add to `/pages/index.tsx`:

```typescript
// Detect widget mode from URL parameter
const isWidget = router.query.widget === 'true';

// Add CSS class based on mode
<div className={`chat-container ${isWidget ? 'widget-mode' : 'full-page'}`}>
```

### Add to `/styles/globals.css`:

```css
/* Widget Mode Adjustments */
.widget-mode {
  height: 100vh;
  overflow: hidden;
}

.widget-mode header {
  display: none; /* Hide full header in widget */
}

.widget-mode .chat-interface {
  max-width: 100%;
  padding: 16px;
  height: 100vh;
}

.widget-mode .disclaimer {
  font-size: 10px;
  padding: 8px;
}
```

---

## Installation Steps for WordPress

### Method 1: Custom HTML Widget
1. Go to WordPress Admin → Appearance → Widgets
2. Add "Custom HTML" widget to your footer
3. Paste the HTML code from Option 1
4. Save

### Method 2: Theme Footer
1. Go to Appearance → Theme File Editor
2. Open `footer.php`
3. Paste the code before `</body>` tag
4. Save

### Method 3: Plugin (Easiest)
1. Install "Insert Headers and Footers" plugin
2. Go to Settings → Insert Headers and Footers
3. Paste code in "Scripts in Footer" section
4. Save

---

## Testing

1. Visit any page on your WordPress site
2. You should see the green chat bubble in bottom-right corner
3. Click it to open the chatbot widget
4. Test the chat functionality

---

## Customization Options

### Change Colors
```css
background: linear-gradient(135deg, #10b981 0%, #059669 100%);
/* Change to your brand colors */
background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
```

### Change Position (Bottom-Left)
```css
#toxicogpt-widget-container {
  left: 20px;  /* Instead of right: 20px */
  right: auto;
}
```

### Change Size
```css
#toxicogpt-widget-popup {
  width: 400px;    /* Adjust width */
  height: 650px;   /* Adjust height */
}
```

### Disable Auto-Open
Remove the auto-open JavaScript section

---

## Advanced Features

### Add Welcome Message
Add a speech bubble that appears before opening:

```html
<div class="welcome-bubble" id="welcome-bubble">
  👋 Hi! Ask me about drug safety and toxicology!
</div>
```

### Track Widget Analytics
```javascript
// Google Analytics event tracking
function toggleToxicoWidget() {
  // ... existing code ...
  if (typeof gtag !== 'undefined') {
    gtag('event', 'widget_opened', {
      'event_category': 'ToxicoGPT',
      'event_label': 'Chat Widget'
    });
  }
}
```

---

## Troubleshooting

**Widget not appearing?**
- Check if JavaScript is enabled
- Clear WordPress cache
- Check browser console for errors

**Widget blocked by CORS?**
- Add your WordPress domain to Vercel's allowed origins
- Update CORS settings in your API

**Widget looks weird on mobile?**
- Check the responsive CSS is included
- Test on different screen sizes

---

## Next Steps

1. ✅ Copy the SQL to Supabase to clear database
2. ✅ Add widget code to WordPress
3. ✅ Test the widget on your site
4. 🎨 Customize colors to match your brand
5. 📊 Set up analytics tracking

Need help with any step? Let me know!
