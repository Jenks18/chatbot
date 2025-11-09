<?php
/**
 * Plugin Name: ToxicoGPT Chat Widget
 * Plugin URI: https://chatbot-y1ar.vercel.app
 * Description: Evidence-based toxicology AI chatbot widget for your WordPress site. Answers questions about drug safety, chemical hazards, and poison information.
 * Version: 1.0.0
 * Author: Your Name
 * Author URI: https://yourwebsite.com
 * License: GPL-2.0+
 * License URI: http://www.gnu.org/licenses/gpl-2.0.txt
 * Text Domain: toxicogpt-widget
 */

// If this file is called directly, abort.
if (!defined('WPINC')) {
    die;
}

// Plugin version
define('TOXICOGPT_VERSION', '1.0.0');

/**
 * Add settings link on plugin page
 */
function toxicogpt_settings_link($links) {
    $settings_link = '<a href="options-general.php?page=toxicogpt-settings">Settings</a>';
    array_unshift($links, $settings_link);
    return $links;
}
add_filter('plugin_action_links_' . plugin_basename(__FILE__), 'toxicogpt_settings_link');

/**
 * Register settings
 */
function toxicogpt_register_settings() {
    register_setting('toxicogpt_options', 'toxicogpt_position', array('default' => 'bottom-right'));
    register_setting('toxicogpt_options', 'toxicogpt_autoopen', array('default' => 0));
    register_setting('toxicogpt_options', 'toxicogpt_color', array('default' => '#10b981'));
    register_setting('toxicogpt_options', 'toxicogpt_enabled', array('default' => 1));
}
add_action('admin_init', 'toxicogpt_register_settings');

/**
 * Add settings page to WordPress admin
 */
function toxicogpt_add_admin_menu() {
    add_options_page(
        'ToxicoGPT Widget Settings',
        'ToxicoGPT Widget',
        'manage_options',
        'toxicogpt-settings',
        'toxicogpt_settings_page'
    );
}
add_action('admin_menu', 'toxicogpt_add_admin_menu');

/**
 * Settings page HTML
 */
function toxicogpt_settings_page() {
    ?>
    <div class="wrap">
        <h1>🧬 ToxicoGPT Widget Settings</h1>
        <p>Configure your ToxicoGPT chatbot widget appearance and behavior.</p>
        
        <form method="post" action="options.php">
            <?php settings_fields('toxicogpt_options'); ?>
            <table class="form-table">
                <tr>
                    <th scope="row">
                        <label for="toxicogpt_enabled">Enable Widget</label>
                    </th>
                    <td>
                        <input type="checkbox" 
                               id="toxicogpt_enabled" 
                               name="toxicogpt_enabled" 
                               value="1" 
                               <?php checked(get_option('toxicogpt_enabled', 1), 1); ?> />
                        <p class="description">Show the chat widget on your website</p>
                    </td>
                </tr>
                
                <tr>
                    <th scope="row">
                        <label for="toxicogpt_position">Widget Position</label>
                    </th>
                    <td>
                        <select id="toxicogpt_position" name="toxicogpt_position">
                            <option value="bottom-right" <?php selected(get_option('toxicogpt_position', 'bottom-right'), 'bottom-right'); ?>>
                                Bottom Right
                            </option>
                            <option value="bottom-left" <?php selected(get_option('toxicogpt_position', 'bottom-right'), 'bottom-left'); ?>>
                                Bottom Left
                            </option>
                        </select>
                        <p class="description">Where to display the chat button</p>
                    </td>
                </tr>
                
                <tr>
                    <th scope="row">
                        <label for="toxicogpt_color">Widget Color</label>
                    </th>
                    <td>
                        <input type="color" 
                               id="toxicogpt_color" 
                               name="toxicogpt_color" 
                               value="<?php echo esc_attr(get_option('toxicogpt_color', '#10b981')); ?>" />
                        <p class="description">Choose the widget button color</p>
                    </td>
                </tr>
                
                <tr>
                    <th scope="row">
                        <label for="toxicogpt_autoopen">Auto-Open Widget</label>
                    </th>
                    <td>
                        <input type="checkbox" 
                               id="toxicogpt_autoopen" 
                               name="toxicogpt_autoopen" 
                               value="1" 
                               <?php checked(get_option('toxicogpt_autoopen', 0), 1); ?> />
                        <p class="description">Automatically open the widget for first-time visitors (after 3 seconds)</p>
                    </td>
                </tr>
            </table>
            
            <?php submit_button(); ?>
        </form>
        
        <hr>
        
        <h2>📊 Widget Preview</h2>
        <div style="padding: 20px; background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px;">
            <p><strong>Current Settings:</strong></p>
            <ul>
                <li>Position: <?php echo esc_html(get_option('toxicogpt_position', 'bottom-right')); ?></li>
                <li>Color: <span style="display:inline-block; width:20px; height:20px; background:<?php echo esc_attr(get_option('toxicogpt_color', '#10b981')); ?>; border-radius:3px; vertical-align:middle;"></span> <?php echo esc_html(get_option('toxicogpt_color', '#10b981')); ?></li>
                <li>Auto-open: <?php echo get_option('toxicogpt_autoopen', 0) ? 'Yes' : 'No'; ?></li>
            </ul>
        </div>
        
        <hr>
        
        <h2>❓ Need Help?</h2>
        <p>Visit <a href="https://chatbot-y1ar.vercel.app" target="_blank">ToxicoGPT</a> for more information.</p>
    </div>
    <?php
}

/**
 * Add widget to footer
 */
function toxicogpt_add_widget() {
    // Check if widget is enabled
    if (!get_option('toxicogpt_enabled', 1)) {
        return;
    }
    
    $position = get_option('toxicogpt_position', 'bottom-right');
    $color = get_option('toxicogpt_color', '#10b981');
    $autoopen = get_option('toxicogpt_autoopen', 0);
    
    // Determine position CSS
    $position_css = ($position === 'bottom-left') ? 'left: 20px; right: auto;' : 'right: 20px;';
    
    ?>
    <!-- ToxicoGPT Widget -->
    <div id="toxicogpt-widget-container" style="position: fixed; bottom: 20px; <?php echo $position_css; ?> z-index: 9999;">
        <div id="toxicogpt-widget-button" onclick="toggleToxicoWidget()" style="width: 60px; height: 60px; border-radius: 50%; background: <?php echo esc_attr($color); ?>; color: white; display: flex; align-items: center; justify-content: center; cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: all 0.3s ease;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
        </div>
        
        <div id="toxicogpt-widget-popup" style="display: none; position: absolute; bottom: 80px; <?php echo ($position === 'bottom-left') ? 'left: 0;' : 'right: 0;'; ?> width: 380px; height: 600px; background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); overflow: hidden;">
            <div style="background: <?php echo esc_attr($color); ?>; color: white; padding: 16px; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 24px;">🧬</span>
                    <div>
                        <h3 style="margin: 0; font-size: 18px;">ToxicoGPT</h3>
                        <p style="margin: 0; font-size: 12px; opacity: 0.9;">Evidence-Based Toxicology AI</p>
                    </div>
                </div>
                <button onclick="toggleToxicoWidget()" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; font-size: 20px;">✕</button>
            </div>
            
            <iframe src="https://chatbot-y1ar.vercel.app/?widget=true" style="width: 100%; height: calc(100% - 120px); border: none;"></iframe>
            
            <div style="padding: 12px 16px; background: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center;">
                <a href="https://chatbot-y1ar.vercel.app" target="_blank" style="color: <?php echo esc_attr($color); ?>; text-decoration: none; font-size: 13px;">Open in full page →</a>
            </div>
        </div>
    </div>
    
    <script>
    function toggleToxicoWidget() {
        var popup = document.getElementById('toxicogpt-widget-popup');
        var button = document.getElementById('toxicogpt-widget-button');
        
        if (popup.style.display === 'none') {
            popup.style.display = 'block';
            button.style.display = 'none';
        } else {
            popup.style.display = 'none';
            button.style.display = 'flex';
        }
    }
    
    <?php if ($autoopen): ?>
    // Auto-open on first visit
    document.addEventListener('DOMContentLoaded', function() {
        var hasVisited = sessionStorage.getItem('toxicogpt-visited');
        if (!hasVisited) {
            setTimeout(function() {
                toggleToxicoWidget();
                sessionStorage.setItem('toxicogpt-visited', 'true');
            }, 3000);
        }
    });
    <?php endif; ?>
    </script>
    <?php
}
add_action('wp_footer', 'toxicogpt_add_widget');

/**
 * Add admin notice after activation
 */
function toxicogpt_activation_notice() {
    ?>
    <div class="notice notice-success is-dismissible">
        <p><strong>🧬 ToxicoGPT Widget activated!</strong> Go to <a href="<?php echo admin_url('options-general.php?page=toxicogpt-settings'); ?>">Settings → ToxicoGPT Widget</a> to configure.</p>
    </div>
    <?php
}

function toxicogpt_activation_hook() {
    add_option('toxicogpt_show_activation_notice', true);
}
register_activation_hook(__FILE__, 'toxicogpt_activation_hook');

function toxicogpt_check_activation_notice() {
    if (get_option('toxicogpt_show_activation_notice')) {
        add_action('admin_notices', 'toxicogpt_activation_notice');
        delete_option('toxicogpt_show_activation_notice');
    }
}
add_action('admin_init', 'toxicogpt_check_activation_notice');
