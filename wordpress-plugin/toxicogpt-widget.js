/**
 * ToxicoGPT WordPress Widget - Standalone JavaScript
 * Embed this in WordPress via Custom HTML widget or theme footer
 * 
 * Usage:
 * <script src="https://your-cdn.com/toxicogpt-widget.js"></script>
 * Or paste this entire file into WordPress Custom HTML widget
 */

(function() {
  'use strict';
  
  // Configuration
  var config = {
    chatUrl: 'https://chatbot-y1ar.vercel.app/',
    position: 'bottom-right', // bottom-right, bottom-left
    bubbleColor: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    bubbleIcon: '💬'
  };

  // Prevent multiple initializations
  if (window.ToxicoGPTWidget) {
    console.warn('ToxicoGPT Widget already initialized');
    return;
  }

  // Create widget HTML
  var widgetHTML = `
    <style>
      #toxicogpt-bubble {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        font-size: 28px;
        z-index: 999998;
        transition: transform 0.3s, box-shadow 0.3s;
        border: none;
      }

      #toxicogpt-bubble:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
      }

      #toxicogpt-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: none;
        align-items: center;
        justify-content: center;
        z-index: 999999;
        backdrop-filter: blur(4px);
      }

      #toxicogpt-modal.active {
        display: flex;
      }

      #toxicogpt-container {
        width: 90%;
        max-width: 450px;
        height: 80%;
        max-height: 700px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        animation: slideUp 0.3s ease-out;
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

      #toxicogpt-iframe {
        width: 100%;
        height: calc(100% - 50px);
        border: none;
      }

      #toxicogpt-header {
        height: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 15px;
        color: white;
      }

      #toxicogpt-header h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }

      #toxicogpt-actions {
        display: flex;
        gap: 10px;
      }

      .toxicogpt-btn {
        background: rgba(255, 255, 255, 0.2);
        border: none;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        color: white;
        font-weight: 600;
        transition: background 0.2s;
        font-size: 13px;
      }

      .toxicogpt-btn:hover {
        background: rgba(255, 255, 255, 0.3);
      }

      @media (max-width: 768px) {
        #toxicogpt-container {
          width: 100%;
          height: 100%;
          max-height: 100%;
          border-radius: 0;
        }
      }
    </style>

    <div id="toxicogpt-bubble" title="Chat with ToxicoGPT" aria-label="Open chat">💬</div>

    <div id="toxicogpt-modal" role="dialog" aria-modal="true" aria-labelledby="toxicogpt-title">
      <div id="toxicogpt-container">
        <div id="toxicogpt-header">
          <h3 id="toxicogpt-title">ToxicoGPT</h3>
          <div id="toxicogpt-actions">
            <button class="toxicogpt-btn" id="toxicogpt-open-new" title="Open in new window" aria-label="Open in new window">
              ⧉ Open Full
            </button>
            <button class="toxicogpt-btn" id="toxicogpt-close" title="Close" aria-label="Close chat">
              ✕
            </button>
          </div>
        </div>
        <iframe id="toxicogpt-iframe" src="${config.chatUrl}" allow="microphone; camera" title="ToxicoGPT Chat"></iframe>
      </div>
    </div>
  `;

  // Inject widget into page when DOM is ready
  function injectWidget() {
    var container = document.createElement('div');
    container.innerHTML = widgetHTML;
    document.body.appendChild(container);
    initializeWidget();
  }

  // Initialize widget functionality
  function initializeWidget() {
    var bubble = document.getElementById('toxicogpt-bubble');
    var modal = document.getElementById('toxicogpt-modal');
    var closeBtn = document.getElementById('toxicogpt-close');
    var openNewBtn = document.getElementById('toxicogpt-open-new');
    var iframe = document.getElementById('toxicogpt-iframe');
    var baseUrl = config.chatUrl;
    var iframeLoaded = false;
    var currentSessionId = null;

    // Track iframe load
    iframe.addEventListener('load', function() {
      iframeLoaded = true;
      console.log('[ToxicoGPT] Widget loaded');
    });

    // Open modal
    bubble.addEventListener('click', function() {
      modal.classList.add('active');
      document.body.style.overflow = 'hidden'; // Prevent background scroll
    });

    // Close modal
    function closeModal() {
      modal.classList.remove('active');
      document.body.style.overflow = ''; // Restore scroll
    }

    closeBtn.addEventListener('click', closeModal);

    // Close on outside click
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        closeModal();
      }
    });

    // Close on ESC key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && modal.classList.contains('active')) {
        closeModal();
      }
    });

    // Listen for messages from iframe
    window.addEventListener('message', function(event) {
      // Security: verify origin
      if (event.origin !== baseUrl.replace(/\/$/, '')) {
        return;
      }
      
      var data = event.data;
      
      // Handle session ID response
      if (data.type === 'SESSION_ID_RESPONSE') {
        currentSessionId = data.sessionId;
        console.log('[ToxicoGPT] Session received:', currentSessionId);
      }
      
      // Handle session updates
      if (data.type === 'SESSION_UPDATE') {
        currentSessionId = data.sessionId;
      }
    });

    // Open in new window
    openNewBtn.addEventListener('click', function() {
      if (!iframeLoaded) {
        alert('Please wait for chat to load...');
        return;
      }

      // Request current session from iframe
      iframe.contentWindow.postMessage({ type: 'GET_SESSION_ID' }, baseUrl);

      // Wait for response then open
      setTimeout(function() {
        var targetUrl = baseUrl;
        if (currentSessionId) {
          targetUrl = baseUrl + '?session=' + currentSessionId;
        }
        
        window.open(targetUrl, '_blank', 'noopener,noreferrer');
        closeModal();
      }, 300);
    });
  }

  // Wait for DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectWidget);
  } else {
    injectWidget();
  }

  // Export widget API
  window.ToxicoGPTWidget = {
    version: '1.0.0',
    open: function() {
      var modal = document.getElementById('toxicogpt-modal');
      if (modal) modal.classList.add('active');
    },
    close: function() {
      var modal = document.getElementById('toxicogpt-modal');
      if (modal) modal.classList.remove('active');
    },
    config: config
  };

})();
