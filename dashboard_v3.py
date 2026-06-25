#!/usr/bin/env python3
"""
The Day Archive - Dashboard V3
Complete settings system with customizable themes, notifications, and advanced features
"""

import streamlit as st
import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from pathlib import Path
from settings_manager_v2 import (
    save_settings, load_settings, export_settings, 
    import_settings, reset_settings, get_color_presets, DEFAULT_SETTINGS
)
from lookup_tables import resolve_lookup_fields

# Page configuration
st.set_page_config(
    page_title="The Day Archive - Dashboard V3",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM THEME APPLICATION
# ============================================================================

def apply_custom_theme(settings):
    """Apply thin, clean design like Plecto using The Day Archive brand colors"""
    
    primary = settings.get('primary_color', '#1E3A8A')
    accent = settings.get('accent_color', '#D1D5DB')
    bg = settings.get('background_color', '#000000')
    text = settings.get('text_color', '#FFFFFF')
    sidebar = settings.get('sidebar_color', '#1F2937')
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        /* Clean minimal background */
        .stApp {{
            background-color: {bg};
            color: {text};
            font-family: 'Inter', sans-serif;
            font-weight: 400;
        }}
        
        /* Thin sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar};
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }}
        
        [data-testid="stSidebar"] * {{ color: {text} !important; }}
        
        /* Thin clean cards - minimal padding */
        .element-container {{
            background: transparent;
            border-radius: 8px;
            padding: 0.3rem 0;
            margin-bottom: 0.2rem;
        }}
        
        /* Minimal headers */
        h1 {{ 
            color: {text} !important; 
            font-weight: 600 !important; 
            font-size: 1.5rem !important; 
            margin-bottom: 1rem !important;
            letter-spacing: -0.02em;
        }}
        
        h2 {{ 
            color: {text} !important; 
            font-weight: 500 !important; 
            font-size: 1.1rem !important;
            margin-bottom: 0.5rem !important;
        }}
        
        h3 {{ 
            color: {accent} !important; 
            font-weight: 500 !important; 
            font-size: 0.95rem !important;
        }}
        
        /* Thin clean buttons */
        .stButton>button {{
            background: {primary};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.4rem 1rem;
            font-weight: 500;
            font-size: 0.85rem;
            transition: all 0.2s ease;
            box-shadow: none;
            height: 32px;
        }}
        
        .stButton>button:hover {{
            background: #1e40af;
            box-shadow: 0 2px 8px rgba(30, 58, 138, 0.2);
        }}
        
        /* Clean minimal inputs */
        .stTextInput>div>div>input, 
        .stSelectbox>div>div>select {{
            background: rgba(255, 255, 255, 0.03) !important;
            color: {text} !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 6px !important;
            padding: 0.4rem 0.6rem !important;
            font-size: 0.85rem !important;
            height: 32px !important;
        }}
        
        .stTextInput>div>div>input:focus {{
            border-color: {primary} !important;
            box-shadow: 0 0 0 1px {primary} !important;
        }}
        
        /* Minimal tabs - thin and clean */
        .stTabs [data-baseweb="tab-list"] {{
            background: transparent;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 0;
            gap: 0;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: {accent};
            border-radius: 0;
            padding: 0.6rem 1.2rem;
            font-weight: 500;
            font-size: 0.85rem;
            border-bottom: 2px solid transparent;
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: rgba(255, 255, 255, 0.02);
            color: {text};
        }}
        
        .stTabs [aria-selected="true"] {{
            background: transparent !important;
            color: {text} !important;
            border-bottom: 2px solid {primary} !important;
            box-shadow: none;
        }}
        
        /* Clean metrics */
        [data-testid="stMetricValue"] {{
            color: {text} !important;
            font-size: 1.5rem !important;
            font-weight: 600 !important;
        }}
        
        [data-testid="stMetricLabel"] {{
            font-size: 0.75rem !important;
            font-weight: 500 !important;
            color: {accent} !important;
        }}
        
        /* Minimal checkboxes */
        .stCheckbox {{
            color: {text};
            font-size: 0.85rem;
        }}
        
        .stCheckbox > label {{ font-weight: 400; }}
        
        /* Thin progress bar */
        .stProgress > div > div > div {{
            background: {primary};
            height: 4px;
        }}
        
        /* Clean alerts - minimal */
        .stSuccess, .stError, .stWarning, .stInfo {{
            border-radius: 6px;
            padding: 0.6rem 0.8rem;
            font-size: 0.85rem;
            border-left-width: 3px;
        }}
        
        /* Minimal text */
        p {{
            margin-bottom: 0.2rem !important;
            line-height: 1.4 !important;
            font-size: 0.85rem;
            font-weight: 400;
        }}
        
        /* Ultra-compact spacing */
        .stCheckbox {{ margin: 0 !important; padding: 0 !important; }}
        .stTextInput {{ margin: 0 !important; }}
        [data-testid="column"] {{ padding: 0.2rem 0.4rem !important; }}
        
        /* Thin clean scrollbar */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ 
            background: rgba(255, 255, 255, 0.1); 
            border-radius: 3px; 
        }}
        ::-webkit-scrollbar-thumb:hover {{ background: rgba(255, 255, 255, 0.2); }}
        
        /* Clean selection */
        ::selection {{
            background: rgba(30, 58, 138, 0.3);
            color: {text};
        }}
        
        /* Remove all shadows and heavy effects */
        * {{ box-shadow: none !important; }}
        
        /* Thin borders everywhere */
        hr {{ border-top: 1px solid rgba(255, 255, 255, 0.05); }}
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

# Load settings
if 'settings' not in st.session_state:
    st.session_state.settings = load_settings()

if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'processed_orders' not in st.session_state:
    st.session_state.processed_orders = []
if 'current_order_index' not in st.session_state:
    st.session_state.current_order_index = 0
if 'processing_log' not in st.session_state:
    st.session_state.processing_log = []
if 'error_log' not in st.session_state:
    st.session_state.error_log = []
if 'total_processed_today' not in st.session_state:
    st.session_state.total_processed_today = 0
if 'selected_orders' not in st.session_state:
    st.session_state.selected_orders = []
if 'order_notes' not in st.session_state:
    # Load notes from persistent file
    notes_file = 'order_notes.json'
    if os.path.exists(notes_file):
        try:
            with open(notes_file, 'r') as f:
                st.session_state.order_notes = json.load(f)
        except:
            st.session_state.order_notes = {}
    else:
        st.session_state.order_notes = {}
if 'api_credentials' not in st.session_state:
    st.session_state.api_credentials = {
        'shopify_store': '',
        'shopify_token': '',
        'claude_api_key': ''
    }

# Apply theme
apply_custom_theme(st.session_state.settings)

# ============================================================================
# SETTINGS PAGE FUNCTION
# ============================================================================

def render_settings_page():
    """Render the complete settings page with all options"""
    st.title("⚙️ Dashboard Settings")
    st.markdown("Customize your dashboard experience")
    st.markdown("---")
    
    # Create tabs for different setting categories
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🎨 Brand Colors",
        "🖥️ Display",
        "⚡ Processing",
        "🔔 Notifications",
        "📄 CSV Export",
        "⏱️ API Limits",
        "📐 Layout",
        "💾 Backup",
        "🔧 Advanced"
    ])
    
    settings = st.session_state.settings
    
    # ========================================================================
    # TAB 1: BRAND COLORS
    # ========================================================================
    with tab1:
        st.subheader("🎨 Customize Brand & Colors")
        st.markdown("Personalize your dashboard branding and theme")
        
        # Branding Section
        st.markdown("#### 📝 Dashboard Branding")
        
        dashboard_name = st.text_input(
            "Dashboard Name",
            value=settings.get('dashboard_name', 'The Day Archive - Dashboard V3'),
            help="Custom name for your dashboard"
        )
        settings['dashboard_name'] = dashboard_name
        
        logo_file = st.text_input(
            "Logo Filename",
            value=settings.get('logo_file', 'logo.png'),
            help="Name of logo file in your GitHub repo (e.g., logo.png, my-logo.svg)"
        )
        settings['logo_file'] = logo_file
        
        st.caption("💡 Upload your logo to GitHub with this filename")
        
        st.markdown("---")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Choose Colors")
            
            # Color pickers
            primary = st.color_picker(
                "Primary Color (buttons, links)",
                value=settings['primary_color'],
                help="Main brand color for interactive elements"
            )
            
            accent = st.color_picker(
                "Accent Color (highlights)",
                value=settings['accent_color'],
                help="Secondary color for borders and highlights"
            )
            
            background = st.color_picker(
                "Background Color",
                value=settings['background_color'],
                help="Main background color"
            )
            
            text = st.color_picker(
                "Text Color",
                value=settings['text_color'],
                help="Primary text color"
            )
            
            sidebar = st.color_picker(
                "Sidebar Color",
                value=settings['sidebar_color'],
                help="Left sidebar background color"
            )
            
            # Update settings
            settings['primary_color'] = primary
            settings['accent_color'] = accent
            settings['background_color'] = background
            settings['text_color'] = text
            settings['sidebar_color'] = sidebar
        
        with col2:
            st.markdown("#### Quick Presets")
            
            presets = get_color_presets()
            
            for preset_name, preset_colors in presets.items():
                if st.button(preset_name, key=f"preset_{preset_name}"):
                    for key, value in preset_colors.items():
                        settings[key] = value
                    st.success(f"Applied {preset_name} theme!")
                    st.rerun()
        
        st.markdown("---")
        
        # Preview section
        st.markdown("#### 🔍 Live Preview")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("Sample Button", key="preview_btn")
        with col2:
            st.metric("Sample Metric", "123")
        with col3:
            st.progress(0.7)
        
        st.info("Preview of your custom theme")
    
    # ========================================================================
    # TAB 2: DISPLAY PREFERENCES
    # ========================================================================
    with tab2:
        st.subheader("🖥️ Display Preferences")
        
        font_size = st.radio(
            "Font Size",
            ["Small", "Medium", "Large"],
            index=["Small", "Medium", "Large"].index(settings.get('font_size', 'Medium')),
            horizontal=True
        )
        settings['font_size'] = font_size
        
        compact_mode = st.toggle(
            "Compact Mode",
            value=settings.get('compact_mode', False),
            help="Reduce spacing for more compact layout"
        )
        settings['compact_mode'] = compact_mode
        
        show_thumbnails = st.toggle(
            "Show Order Thumbnails",
            value=settings.get('show_thumbnails', True),
            help="Display preview images for orders"
        )
        settings['show_thumbnails'] = show_thumbnails
        
        dark_mode = st.toggle(
            "Dark Mode",
            value=settings.get('dark_mode', True),
            help="Use dark theme colors"
        )
        settings['dark_mode'] = dark_mode
    
    # ========================================================================
    # TAB 3: PROCESSING DEFAULTS
    # ========================================================================
    with tab3:
        st.subheader("⚡ Processing Defaults")
        
        batch_size = st.number_input(
            "Default Batch Size",
            min_value=1,
            max_value=100,
            value=settings.get('default_batch_size', 5),
            help="Number of orders to process at once"
        )
        settings['default_batch_size'] = batch_size
        
        auto_refresh = st.number_input(
            "Auto-Refresh Orders (minutes)",
            min_value=0,
            max_value=60,
            value=settings.get('auto_refresh_minutes', 0),
            help="Automatically refresh orders every X minutes (0 = disabled)"
        )
        settings['auto_refresh_minutes'] = auto_refresh
        
        date_filter = st.selectbox(
            "Default Date Filter",
            ["All Orders", "Today", "Yesterday", "Last 7 Days", "Last 30 Days"],
            index=["All Orders", "Today", "Yesterday", "Last 7 Days", "Last 30 Days"].index(
                settings.get('default_date_filter', 'All Orders')
            )
        )
        settings['default_date_filter'] = date_filter
        
        auto_select = st.toggle(
            "Auto-Select New Orders",
            value=settings.get('auto_select_new', False),
            help="Automatically select newly fetched orders"
        )
        settings['auto_select_new'] = auto_select
    
    # ========================================================================
    # TAB 4: NOTIFICATIONS
    # ========================================================================
    with tab4:
        st.subheader("🔔 Notification Settings")
        
        desktop_notif = st.toggle(
            "Desktop Notifications",
            value=settings.get('desktop_notifications', False),
            help="Show browser notifications when processing completes"
        )
        settings['desktop_notifications'] = desktop_notif
        
        sound_alert = st.toggle(
            "Sound Alert",
            value=settings.get('sound_alert', False),
            help="Play sound when processing completes"
        )
        settings['sound_alert'] = sound_alert
        
        email_notif = st.toggle(
            "Email Notifications",
            value=settings.get('email_notifications', False),
            help="Send email when processing completes"
        )
        settings['email_notifications'] = email_notif
        
        if email_notif:
            email = st.text_input(
                "Notification Email",
                value=settings.get('notification_email', ''),
                placeholder="your@email.com"
            )
            settings['notification_email'] = email
        
        slack_webhook = st.text_input(
            "Slack Webhook URL (optional)",
            value=settings.get('slack_webhook', ''),
            type="password",
            help="Post notifications to Slack"
        )
        settings['slack_webhook'] = slack_webhook
    
    # ========================================================================
    # TAB 5: CSV EXPORT OPTIONS
    # ========================================================================
    with tab5:
        st.subheader("📄 CSV Export Options")
        
        filename_format = st.text_input(
            "Filename Format",
            value=settings.get('filename_format', 'orders_{date}_{time}'),
            help="Use {date} and {time} placeholders"
        )
        settings['filename_format'] = filename_format
        
        st.caption("Example: orders_2026-04-06_14-30-45.csv")
        
        save_location = st.text_input(
            "Auto-Save Location",
            value=settings.get('auto_save_location', '.'),
            help="Folder path to save CSVs"
        )
        settings['auto_save_location'] = save_location
        
        include_notes = st.toggle(
            "Include Order Notes",
            value=settings.get('include_notes', False),
            help="Add order notes column to CSV"
        )
        settings['include_notes'] = include_notes
        
        decimal_precision = st.number_input(
            "Decimal Precision",
            min_value=0,
            max_value=10,
            value=settings.get('decimal_precision', 2),
            help="Number of decimal places for prices"
        )
        settings['decimal_precision'] = decimal_precision
    
    # ========================================================================
    # TAB 6: API RATE LIMITING
    # ========================================================================
    with tab6:
        st.subheader("⏱️ API Rate Limiting")
        
        delay = st.slider(
            "Delay Between Orders (seconds)",
            min_value=0,
            max_value=10,
            value=settings.get('delay_between_orders', 1),
            help="Wait time between processing each order"
        )
        settings['delay_between_orders'] = delay
        
        max_concurrent = st.number_input(
            "Max Concurrent Requests",
            min_value=1,
            max_value=10,
            value=settings.get('max_concurrent', 1),
            help="Number of simultaneous API requests"
        )
        settings['max_concurrent'] = max_concurrent
        
        auto_retry = st.toggle(
            "Auto-Retry Failed Orders",
            value=settings.get('auto_retry_failed', True),
            help="Automatically retry failed orders"
        )
        settings['auto_retry_failed'] = auto_retry
        
        timeout = st.number_input(
            "Timeout Duration (seconds)",
            min_value=30,
            max_value=300,
            value=settings.get('timeout_duration', 120),
            help="Max wait time for API responses"
        )
        settings['timeout_duration'] = timeout
    
    # ========================================================================
    # TAB 7: DASHBOARD LAYOUT
    # ========================================================================
    with tab7:
        st.subheader("📐 Dashboard Layout")
        
        sidebar_open = st.toggle(
            "Sidebar Open by Default",
            value=settings.get('sidebar_default_open', True),
            help="Show sidebar when dashboard loads"
        )
        settings['sidebar_default_open'] = sidebar_open
        
        sort_order = st.radio(
            "Order Sort Order",
            ["Newest First", "Oldest First", "Order Number"],
            index=["Newest First", "Oldest First", "Order Number"].index(
                settings.get('sort_order', 'Newest First')
            )
        )
        settings['sort_order'] = sort_order
        
        items_per_page = st.number_input(
            "Items Per Page",
            min_value=5,
            max_value=100,
            value=settings.get('items_per_page', 50),
            help="Number of orders to show per page"
        )
        settings['items_per_page'] = items_per_page
    
    # ========================================================================
    # TAB 8: BACKUP & SYNC
    # ========================================================================
    with tab8:
        st.subheader("💾 Backup & Sync")
        
        st.markdown("#### Export Settings")
        
        if st.button("📥 Export Settings File"):
            settings_json = export_settings(settings)
            st.download_button(
                label="Download Settings.json",
                data=settings_json,
                file_name=f"dashboard_settings_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            st.success("Settings ready for download!")
        
        st.markdown("#### Import Settings")
        
        uploaded_file = st.file_uploader("Upload Settings File", type=['json'])
        if uploaded_file is not None:
            try:
                json_string = uploaded_file.read().decode('utf-8')
                imported_settings = import_settings(json_string)
                if imported_settings:
                    st.session_state.settings = imported_settings
                    st.success("Settings imported successfully!")
                    st.rerun()
                else:
                    st.error("Invalid settings file")
            except Exception as e:
                st.error(f"Error importing: {e}")
    
    # ========================================================================
    # TAB 9: ADVANCED
    # ========================================================================
    with tab9:
        st.subheader("🔧 Advanced Options")
        
        debug_mode = st.toggle(
            "Debug Mode",
            value=settings.get('debug_mode', False),
            help="Show detailed error messages"
        )
        settings['debug_mode'] = debug_mode
        
        show_logs = st.toggle(
            "Show API Logs",
            value=settings.get('show_api_logs', False),
            help="Display API request/response logs"
        )
        settings['show_api_logs'] = show_logs
        
        st.markdown("---")
        st.markdown("#### Danger Zone")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset to Defaults", type="secondary"):
                if st.session_state.get('confirm_reset', False):
                    st.session_state.settings = reset_settings()
                    save_settings(st.session_state.settings)
                    st.success("Settings reset!")
                    st.session_state.confirm_reset = False
                    time.sleep(1)
                    st.rerun()
                else:
                    st.session_state.confirm_reset = True
                    st.warning("Click again to confirm reset")
        
        with col2:
            if st.button("🗑️ Clear All Data"):
                st.warning("This feature is coming soon")
    
    # ========================================================================
    # SAVE SETTINGS BUTTON
    # ========================================================================
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save Settings", type="primary", use_container_width=True):
            if save_settings(settings):
                st.success("Settings saved!")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Error saving settings")
    
    with col2:
        if st.button("↩️ Reload", use_container_width=True):
            st.session_state.settings = load_settings()
            st.rerun()
    
    # Update session state
    st.session_state.settings = settings

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def calculate_star_sign(month: int, day: int) -> str:
    """Calculate zodiac star sign"""
    if (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "CAPRICORN"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "AQUARIUS"
    elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
        return "PISCES"
    elif (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "ARIES"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "TAURUS"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "GEMINI"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "CANCER"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "LEO"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "VIRGO"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "LIBRA"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "SCORPIO"
    else:
        return "SAGITTARIUS"

def get_birthstone(month: int) -> str:
    """Get birthstone for month"""
    stones = [
        "Garnet", "Amethyst", "Aquamarine", "Diamond", "Emerald", "Pearl",
        "Ruby", "Peridot", "Sapphire", "Opal", "Topaz", "Turquoise"
    ]
    return stones[month - 1]

def get_month_name(month: int) -> str:
    """Get month name"""
    months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    return months[month - 1]

def get_day_of_week(day: int, month: int, year: int) -> str:
    """Calculate day of week"""
    date = datetime(year, month, day)
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return days[date.weekday()]

# ============================================================================
# SHOPIFY API FUNCTIONS
# ============================================================================

def fetch_shopify_orders(api_token: str, store_url: str) -> List[Dict]:
    """Fetch ALL unfulfilled orders from Shopify using pagination"""
    base_url = f"https://{store_url}/admin/api/2024-01/orders.json"
    headers = {
        "X-Shopify-Access-Token": api_token,
        "Content-Type": "application/json"
    }
    
    all_orders = []
    page_info = None
    
    # Keep fetching until we have all orders
    while True:
        params = {
            "status": "any",
            "fulfillment_status": "unfulfilled",
            "limit": 250,
            "fields": "id,name,email,line_items,fulfillment_status,created_at"
        }
        
        # Add pagination if we have page_info
        if page_info:
            params["page_info"] = page_info
        
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=30)
            
            if response.status_code != 200:
                st.error(f"Shopify API Error: {response.status_code}")
                break
            
            orders = response.json().get("orders", [])
            all_orders.extend(orders)
            
            # Check if there are more pages
            link_header = response.headers.get("Link", "")
            if "rel=\"next\"" in link_header:
                # Extract page_info from Link header
                import re
                match = re.search(r'page_info=([^&>]+)', link_header)
                if match:
                    page_info = match.group(1)
                else:
                    break
            else:
                # No more pages
                break
                
        except Exception as e:
            st.error(f"Error fetching orders: {e}")
            break
    
    return all_orders

def extract_personalization_data(order: Dict, item_index: int = 0) -> Optional[tuple]:
    """Extract Full Name and Birthday from a specific line item in an order
    
    Args:
        order: The Shopify order dict
        item_index: Which line item to extract from (0 for first, 1 for second, etc.)
    
    Returns:
        Tuple of (full_name, birthday) for that specific line item
    """
    
    # Get the specific line item
    line_items = order.get("line_items", [])
    
    if item_index >= len(line_items):
        return ("", "")
    
    item = line_items[item_index]
    
    # Extract personalization from this specific item
    full_name = ""
    birthday = ""
    
    properties = item.get("properties", [])
    for prop in properties:
        if prop.get("name") == "Full Name":
            full_name = prop.get("value") or ""
        elif prop.get("name") == "Birthday":
            birthday = prop.get("value") or ""
    
    # Check if this order+item has been edited in session - override with edits
    edit_key = f"{order['name']}_item{item_index}"
    if 'order_edits' in st.session_state and edit_key in st.session_state.order_edits:
        edits = st.session_state.order_edits[edit_key]
        # Only override if edit value is not empty
        if edits.get('full_name'):
            full_name = edits['full_name']
        if edits.get('birthday'):
            birthday = edits['birthday']
    
    # Return tuple even if values are empty strings (so we can edit them)
    return (full_name or "", birthday or "")

def get_line_item_count(order: Dict) -> int:
    """Get the number of line items in an order"""
    return len(order.get("line_items", []))

# ============================================================================
# CLAUDE API FUNCTION
# ============================================================================

def research_with_claude(month_name: str, day: int, year: int, api_key: str, progress_callback=None) -> Dict:
    """Call Claude API to research historical data"""
    
    if progress_callback:
        progress_callback("🔍 Researching with Claude API...")
    
    prompt = f"""You are a historical research expert. Research accurate historical data for {month_name} {day}, {year} in Australia.

🎯 MISSION: Provide 100% ACCURATE, VERIFIABLE data. Accuracy is MORE important than speed.

CRITICAL RULES:
1. CELEBRITIES: ONLY people ACTUALLY born on {month_name} {day} (verify the date in your knowledge)
2. HISTORICAL EVENTS: ONLY events that ACTUALLY happened on {month_name} {day} (verify the date)
3. SPORTS/ENTERTAINMENT: ONLY actual winners/champions for {year} (verify the year)
4. PRICES/DATA: Use your most reliable historical knowledge for {year}

⚠️ TRIPLE-CHECK THESE BEFORE INCLUDING:
- Celebrity birthdays: Is their birthday REALLY {month_name} {day}?
- Historical event dates: Did this REALLY happen on {month_name} {day}?
- Sports winners: Is this the ACTUAL winner for {year}?

If you are NOT CERTAIN about a date, DO NOT include that item. Better to skip than be wrong.

Return ONLY valid JSON (no markdown, no preambles, no explanations).

CRITICAL FORMATTING RULES:
- All monetary values: AUSTRALIAN DOLLARS ($) or CENTS (c) ONLY
  ⚠️ NEVER use British pounds (£), shillings (s), or pence (d)
  ⚠️ Convert all pre-1966 prices to approximate Australian dollar equivalents
- All population values: ONLY the number with units (e.g., "3.3 Billion" or "11.6 million")
- All percentage values: ONLY the number with % (e.g., "3.2%")
- Celebrity names: "Name - [2-3 word profession]" ONLY. NO DATES. NO extra description, no "known for", no film/show titles. Profession ONLY, 2-3 words, NEVER 1 word. NEVER append "born on this day". Example: "Richard Lewis - Stand-up comedian"
- News events: Must be events that happened on {month_name} {day} in ANY year (worldwide, not just Australia). MAX 15 WORDS per news event (date prefix "On Month Day, Year" can count toward limit or be excluded). Keep it to ONE short sentence — no multi-clause descriptions.
- Number1Song: If ARIA charts didn't exist in {year}, use worldwide #1 song from that time
- HISTORICAL EVENTS: Must be events that happened on {month_name} {day} across different eras (1800s, early 1900s, mid 1900s, 2000s)
  - Look for events on {month_name} {day} in 1800s, early 1900s (1900-1940), mid-late 1900s (1950-1990), and 2000s-2020s
  - If no significant events can be found for that specific DATE, then use events from {year} instead

Provide accurate Australian historical data in this exact JSON structure:

{{
  "PrimeMinister": "Name of Australian PM serving in {year}",
  "IncomingPM": "Name of the PM who came to power AFTER the current PM (regardless of what year they took office)",
  "Monarch": "Name of British monarch in {year}",
  "AverageSalary": "VALUE ONLY e.g., $2,080",
  "Celebrity1": "Name - [2-3 word profession ONLY, e.g. 'Stand-up comedian']. NO DATES, NO descriptions, NO film/show titles. MUST be a celebrity actually BORN on {month_name} {day} (any year). Example: 'Tim Roth - British actor'",
  "Celebrity2": "Name - [2-3 word profession ONLY]. NO DATES, NO descriptions. MUST be a different celebrity actually BORN on {month_name} {day} (any year).",
  "Celebrity3": "Name - [2-3 word profession ONLY]. NO DATES, NO descriptions. MUST be a third celebrity actually BORN on {month_name} {day} (any year).",
  "NewsEvent1": "Major world event that happened on {month_name} {day} in ANY year. MAX 15 WORDS TOTAL. One short sentence only, e.g. 'On July 7, 2005, terrorist bombings struck London's transport system, killing 52 people.'",
  "NewsEvent2": "Second major world event that happened on {month_name} {day} in ANY year. MAX 15 WORDS TOTAL. One short sentence only.",
  "NewsEvent3": "Third major world event that happened on {month_name} {day} in ANY year. MAX 15 WORDS TOTAL. One short sentence only.",
  "NRLWinner": "NRL premiership winner {year}",
  "AFLWinner": "AFL premiership winner {year}",
  "BestActor": "Oscar Best Actor {year} - Film name",
  "BestActress": "Oscar Best Actress {year} - Film name",
  "Bathurst1000": "Exact winning driver(s) of the {year} Bathurst 1000 ONLY - verify against that specific year, do not assume based on a driver's reputation or nearby-year wins. Include all credited drivers (2 or 3, e.g. mid-race car swaps).",
  "AusOpenWinners": "Australian Open singles winners {year}",
  "Number1Song": "Song title - Artist (use ARIA if exists for {year}, otherwise worldwide #1)",
  "AverageHouse": "VALUE ONLY e.g., $8,500",
  "MilkPrice": "VALUE ONLY e.g., $0.08 or $1.20",
  "BreadPrice": "VALUE ONLY e.g., $0.18 or $1.20",
  "EggsPrice": "VALUE ONLY e.g., $0.45 or $1.80",
  "WorldPopulation": "VALUE ONLY e.g., 3.3 Billion",
  "AustraliaPopulation": "VALUE ONLY e.g., 11.6 million",
  "HistoricalEventDate1": "Year (1800s era) when event happened on {month_name} {day}",
  "HistoricalEvent1": "ONE COMPLETE SENTENCE (20-30 words) describing a major historical event that happened on {month_name} {day} in the 1800s. Include key details like who, what, where, and significance. Example format: 'On April 10, 1849, American inventor Walter Hunt received a patent for the modern safety pin, a simple yet revolutionary device he reportedly designed in just three hours to pay off a $15 debt.'",
  "HistoricalEventDate2": "Year (early 1900s) when event happened on {month_name} {day}",
  "HistoricalEvent2": "ONE COMPLETE SENTENCE (20-30 words) describing a major historical event that happened on {month_name} {day} in early 1900s (1900-1940). Include key details about the event and its impact.",
  "HistoricalEventDate3": "Year (mid-late 1900s) when event happened on {month_name} {day}",
  "HistoricalEvent3": "ONE COMPLETE SENTENCE (20-30 words) describing a major historical event that happened on {month_name} {day} in mid-late 1900s (1950-1990). Include who was involved and why it mattered.",
  "HistoricalEventDate4": "Year (2000s-2020s) when event happened on {month_name} {day}",
  "HistoricalEvent4": "ONE COMPLETE SENTENCE (20-30 words) describing a major historical event that happened on {month_name} {day} in 2000s-2020s. Provide context and significance of the event.",
  "YearsOfWages": "VALUE ONLY e.g., 4-5 years wages",
  "CadburyBarPrice": "VALUE ONLY e.g., 8c or 90c",
  "PetrolPrice": "VALUE ONLY e.g., $0.06 or $0.68",
  "InflationRate": "VALUE ONLY e.g., 3.2%",
  "StampPrice": "VALUE ONLY e.g., 5c or 41c",
  "CinemaPrice": "VALUE ONLY e.g., $0.75 or $7.50",
  "TopBook": "Title - Author (MUST have been published in {year} or at most 1 year prior to {year}. NEVER list a book published after {year}. Verify the publication year.)",
  "TopBookDescription": "One sentence description, MAX 15-20 WORDS",
  "TVShow": "Show name (MUST have been on air before or during {year}. NEVER list a show that premiered after {year}, even if it premiered in the same calendar year but after the birth date. Verify the premiere date.)",
  "TVShowDescription": "One sentence description, MAX 15-20 WORDS",
  "FashionTrend": "Trend name",
  "FashionDescription": "One sentence description, MAX 15-20 WORDS",
  "Technology": "Technology name",
  "TechnologyDescription": "One sentence description, MAX 15-20 WORDS",
  "AustraliaBirths": "VALUE ONLY e.g., 223,000",
  "BirthsDescription": "One sentence about birth rate, MAX 15-20 WORDS",
  "BoyName1": "Most popular boys name Australia {year}",
  "BoyName2": "2nd most popular",
  "BoyName3": "3rd",
  "BoyName4": "4th",
  "BoyName5": "5th",
  "BoyName6": "6th",
  "BoyName7": "7th",
  "BoyName8": "8th",
  "BoyName9": "9th",
  "BoyName10": "10th",
  "GirlName1": "Most popular girls name Australia {year}",
  "GirlName2": "2nd",
  "GirlName3": "3rd",
  "GirlName4": "4th",
  "GirlName5": "5th",
  "GirlName6": "6th",
  "GirlName7": "7th",
  "GirlName8": "8th",
  "GirlName9": "9th",
  "GirlName10": "10th"
}}

⚠️ DETAILED ACCURACY REQUIREMENTS - READ CAREFULLY ⚠️

═══════════════════════════════════════════════════════
CELEBRITIES - BIRTH DATE MUST BE {month_name} {day}
═══════════════════════════════════════════════════════

VERIFICATION PROCESS:
1. Think: "Is this person REALLY born on {month_name} {day}?"
2. Check your knowledge carefully
3. Only include if you are CERTAIN the birth date matches

EXAMPLES OF WRONG DATES (DO NOT REPEAT THESE MISTAKES):
❌ John Travolta for August 25 → Actually born February 18
❌ Olivia Newton-John for August 25 → Actually born September 26
❌ Paul Hogan for August 25 → Actually born October 8
❌ Helen Reddy for October 24 → Actually born October 25

EXAMPLES OF CORRECT DATES:
✅ Sean Connery for August 25 → Born August 25, 1930
✅ Tim Burton for August 25 → Born August 25, 1958
✅ Blake Lively for August 25 → Born August 25, 1987

USE WORLDWIDE CELEBRITIES - not limited to Australia
EACH PERSON MUST BE DIFFERENT - no repeats
FORMAT: "Name - [2-3 word profession]" ONLY. No descriptions, no film titles, no "known for".

═══════════════════════════════════════════════════════
HISTORICAL EVENTS - MUST HAVE OCCURRED ON {month_name} {day}
═══════════════════════════════════════════════════════

⚠️ CRITICAL — "BIRTHDAY BIAS" WARNING:
Do NOT shift or adjust historical event dates to match the birth date's day number ({day}).
If an event happened on {month_name} 10 but the birth date is {month_name} {day}, do NOT move it to {month_name} {day}.
The event date must be the REAL documented date — not adjusted to fit.
This is a known and common error. Every event date must be independently verifiable as accurate.

REAL EXAMPLES OF THIS ERROR (DO NOT REPEAT):
❌ Thai cave rescue listed as July 13 — actual rescue completed July 10, 2018
❌ Last US combat brigade withdrawal listed as August 2, 2010 — actually August 18-19, 2010
❌ US invasion of Grenada listed as October 27, 1983 — actually October 25, 1983
❌ Ingmar Bergman death listed as July 31, 2007 — actually July 30, 2007

VERIFICATION PROCESS:
1. Think: "Did this event REALLY happen on {month_name} {day}?"
2. The YEAR can vary, but the MONTH and DAY must be {month_name} {day}
3. Only include if you are CERTAIN about the date — if unsure, pick a different event
4. NEVER move an event's real date to match the birth day number

EXAMPLES OF WRONG DATES (DO NOT REPEAT):
❌ Titanic left Queenstown on April 10 → Actually April 11, 1912
❌ Buchenwald liberated April 10 → Actually April 11, 1945
❌ Treaty signed April 10, 1818 → Actually February 22, 1819

EXAMPLES OF CORRECT DATES:
✅ Safety pin patented April 10, 1849 → Correct
✅ Paul McCartney announced Beatles breakup April 10, 1970 → Correct
✅ Polish plane crash April 10, 2010 → Correct

EACH EVENT MUST BE A FULL SENTENCE (25-35 words):
Example: "On April 10, 1912, the RMS Titanic departed from Southampton, England on its maiden voyage across the Atlantic, carrying over 2,200 passengers and crew toward its tragic fate."

Find 4 events from DIFFERENT eras:
- 1800s (1800-1899)
- Early 1900s (1900-1945)
- Mid-Late 1900s (1946-1999)
- 2000s-2020s (2000-present)

═══════════════════════════════════════════════════════
SPORTS WINNERS - MUST BE ACTUAL WINNERS FOR {year}
═══════════════════════════════════════════════════════

NRL Winner: Use your knowledge of {year} NRL/NSWRL premiership
- Before 1998: Use NSWRL premiership winner
- 1998+: Use NRL premiership winner
- Provide full team name (e.g., "Manly-Warringah Sea Eagles")

AFL Winner: Actual {year} VFL/AFL premiership winner
- Before 1990: VFL Grand Final winner
- 1990+: AFL Grand Final winner

Bathurst 1000: Actual winner(s) of {year} race
- Include driver names (the EXACT pairing/trio that won THAT SPECIFIC year - co-drivers change year to year, do not assume a famous driver's usual teammate)
- Double check: some years have 3 drivers credited (e.g. due to a mid-race car swap), not always 2
- Do NOT default to a well-known driver (e.g. Peter Brock, Dick Johnson) just because they are associated with that era - verify they actually won {year} specifically, not a nearby year
- If unsure, prioritise accuracy over a "plausible sounding" pairing

Australian Open: Singles champions for {year}
- Format: "Men: [Name], Women: [Name]"

═══════════════════════════════════════════════════════
ENTERTAINMENT - VERIFY YEAR {year}
═══════════════════════════════════════════════════════

Best Actor/Actress: Academy Awards for {year} films
- Format: "Actor Name - Film Title"

Number1Song: 
- If {year} ≥ 1988: Use ARIA Charts #1 song for {year}
- If {year} < 1988: Use worldwide/UK/US #1 song for {year}
- Format: "Song Title - Artist Name"

TopBook: Must have been published in {year} or at most 1 year prior
- NEVER list a book published after {year}
- NEVER list a book published more than 2 years before {year}
- Verify the exact publication year before including
- Known error to avoid: listing books from the wrong decade entirely (e.g. The Old Man and the Sea published 1952, not 1956)

TVShow: Must have been on air before or during {year}
- NEVER list a show that premiered after {year}
- Even if a show premiered in the same calendar year as {year}, verify it premiered BEFORE the birth month/day
- Known error to avoid: listing shows 1-2 years before their actual premiere (e.g. In Melbourne Tonight premiered May 1957 — do not list it for a 1956 birth date)

═══════════════════════════════════════════════════════
PRICES & ECONOMICS - HISTORICAL DATA FOR {year}
═══════════════════════════════════════════════════════

⚠️ CRITICAL: ALL PRICES MUST BE IN AUSTRALIAN DOLLARS ($) OR CENTS (c)
⚠️ DO NOT USE British pounds (£), shillings (s), or pence (d)
⚠️ Convert to Australian decimal currency

All prices must reflect {year} Australian values IN AUSTRALIAN CURRENCY:
- AverageSalary: Annual wage in AUD (e.g., "$520" or "$2,080")
- AverageHouse: House price in AUD (e.g., "$8,500" or "$1,200")
- MilkPrice: Per pint/litre in AUD (e.g., "$0.15" or "8c")
- BreadPrice: Per loaf in AUD (e.g., "$0.12" or "5c")
- EggsPrice: Per dozen in AUD (e.g., "$0.45" or "15c")
- PetrolPrice: Per gallon/litre in AUD (e.g., "$0.18" or "6c")
- CadburyBarPrice: In AUD (e.g., "5c" or "$0.05")
- StampPrice: In AUD (e.g., "3c" or "$0.03")
- CinemaPrice: In AUD (e.g., "$0.50" or "50c")

CURRENCY RULES:
- Before 1966: Australia used pounds/shillings/pence - CONVERT to approximate dollar value
  Example: £312 → "$624" (roughly £1 = $2 conversion)
  Example: 6d (sixpence) → "5c" (approximate conversion)
  Example: 2s 6d (two shillings sixpence) → "25c" (approximate)
- 1966 onwards: Use decimal Australian dollars directly
- Always use $ or c symbols, NEVER £, s, or d

Format: VALUE ONLY (just the number with $ or c, no words)
Examples: "$2,080" or "8c" or "$0.15"

═══════════════════════════════════════════════════════
GOVERNMENT - VERIFY WHO SERVED IN {year}
═══════════════════════════════════════════════════════

PrimeMinister: Who was Australian PM during {year}?
IncomingPM: Who became PM AFTER the current PM? (can be years later)
Monarch: Who was British monarch during {year}?

═══════════════════════════════════════════════════════
BABY NAMES - ACTUAL AUSTRALIAN POPULARITY FOR {year}
═══════════════════════════════════════════════════════

Top 10 boys and girls names in Australia for {year}
- Use historical records if available
- If exact {year} unavailable, use closest decade
- Do NOT use modern popular names for old years

═══════════════════════════════════════════════════════
FINAL CHECKLIST BEFORE SUBMITTING
═══════════════════════════════════════════════════════

MANDATORY SELF-VERIFICATION - DO NOT SKIP:

1. CELEBRITY BIRTHDATE VERIFICATION:
   □ Celebrity1: Born on {month_name} {day}? (Check: NOT {month_name} {day-1} or {day+1})
   □ Celebrity2: Born on {month_name} {day}? (Different person from Celebrity1?)
   □ Celebrity3: Born on {month_name} {day}? (Different from 1 and 2?)
   □ All 3 celebrities are REAL, verifiable people?
   □ Format: "Name - Description" (NO birth year included)?

2. STAR SIGN ACCURACY:
   □ Does the star sign match {month_name} {day}?
   □ Common mistakes to avoid:
     - Aries: March 21-April 19 (NOT April 20+)
     - Taurus: April 20-May 20 (NOT May 21+)
     - Gemini: May 21-June 20 (NOT June 21+)
     - Cancer: June 21-July 22
     - Leo: July 23-August 22
     - Virgo: August 23-September 22
     - Libra: September 23-October 22
     - Scorpio: October 23-November 21
     - Sagittarius: November 22-December 21
     - Capricorn: December 22-January 19
     - Aquarius: January 20-February 18
     - Pisces: February 19-March 20

3. HISTORICAL EVENTS DATE VERIFICATION:
   □ Event1: Happened on {month_name} {day} in 1800s?
   □ Event2: Happened on {month_name} {day} in early 1900s?
   □ Event3: Happened on {month_name} {day} in mid-late 1900s?
   □ Event4: Happened on {month_name} {day} in 2000s-2020s?
   □ All events are 20-30 words (full sentences)?
   □ Each event is from a DIFFERENT era?
   □ BIRTHDAY BIAS CHECK: Have I verified each event date is the REAL date, NOT shifted to match the birth day number ({day})? (e.g. if birth day is {day}, confirm each event did not actually happen on a different day that I have wrongly moved to {day})

10. BOOK AND TV SHOW VERIFICATION:
   □ TopBook was published in {year} or at most 1 year prior — NOT after {year}?
   □ TVShow was on air before or during {year} — NOT a show that premiered after {year}?

4. AUSTRALIAN CURRENCY VERIFICATION:
   □ ALL prices in Australian dollars ($) or cents (c)?
   □ NO British pounds (£), shillings (s), or pence (d)?
   □ Pre-1966 prices converted to decimal?
   □ Prices realistic for {year}?
   □ Examples checked:
     - 1940s salary: $300-500 (NOT $3,000)
     - 1960s house: $5,000-10,000 (NOT $50,000)
     - 1980s salary: $10,000-20,000 (NOT $100,000)

5. SPORTS WINNERS VERIFICATION:
   □ NRL/AFL winner is actual {year} winner? (NOT the year before or after)
   □ Australian Open winners are {year} champions?
   □ Bathurst 1000 winner is {year} race winner specifically (NOT a nearby year)? Correct driver PAIRING/trio for that exact year (co-drivers change yearly - verify, don't assume)?
   □ Best Actor/Actress won for {year} films?

6. YEAR FORMAT VERIFICATION:
   □ Year is 4 digits? (e.g., "1943" NOT "43")
   □ All HistoricalEventDate fields are 4-digit years?

7. NEWS EVENTS VERIFICATION:
   □ NewsEvent1: Actually happened on {month_name} {day}?
   □ NewsEvent2: Actually happened on {month_name} {day}?
   □ NewsEvent3: Actually happened on {month_name} {day}?
   □ All news events are from the correct DATE (even if different years)?
   □ Each NewsEvent is MAX 15 WORDS (one short sentence, not multiple clauses)?

8. DESCRIPTION LENGTH VERIFICATION:
   □ TopBookDescription is MAX 15-20 WORDS?
   □ TVShowDescription is MAX 15-20 WORDS?
   □ FashionDescription is MAX 15-20 WORDS?
   □ TechnologyDescription is MAX 15-20 WORDS?
   □ BirthsDescription is MAX 15-20 WORDS?

9. FINAL ACCURACY CHECK:
   Ask yourself for EACH field:
   - "Am I 100% CERTAIN this is correct?"
   - "Have I verified the DATE/YEAR?"
   - "Is this FACTUALLY accurate?"
   
   If ANY answer is "no" or "I'm not sure" → DO NOT include that data!
   Better to leave it blank than to be wrong!

═══════════════════════════════════════════════════════
CRITICAL REMINDERS
═══════════════════════════════════════════════════════

⚠️ WRONG CELEBRITY BIRTHDATES ARE THE #1 ERROR
⚠️ WRONG HISTORICAL EVENT DATES ARE THE #2 ERROR  
⚠️ BRITISH CURRENCY IN PRICES IS THE #3 ERROR
⚠️ 2-DIGIT YEARS INSTEAD OF 4-DIGIT IS THE #4 ERROR
⚠️ BIRTHDAY BIAS (SHIFTING EVENT DATES TO MATCH BIRTH DAY) IS THE #5 ERROR
⚠️ BOOK OR TV SHOW FROM WRONG YEAR (PUBLISHED/AIRED AFTER BIRTH DATE) IS THE #6 ERROR

TRIPLE-CHECK these four things above ALL else!

Return ONLY the JSON object. Start with {{ and end with }}."""

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    timeout = st.session_state.settings.get('timeout_duration', 180)
    
    data = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 8192,  # Maximum allowed for comprehensive, detailed responses
        "temperature": 0.3,  # Lower temperature for more accurate, factual responses
        "messages": [{
            "role": "user",
            "content": prompt
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=timeout)
        
        if response.status_code != 200:
            if progress_callback:
                progress_callback(f"❌ Claude API error: {response.status_code}")
            return {}
        
        result = response.json()
        text_content = result["content"][0]["text"]
        
        # Clean up markdown
        text_content = text_content.replace("```json", "").replace("```", "").strip()
        
        # Find JSON object
        start_idx = text_content.find("{")
        end_idx = text_content.rfind("}")
        
        if start_idx != -1 and end_idx != -1:
            text_content = text_content[start_idx:end_idx+1]
        
        # Parse JSON
        research_data = json.loads(text_content)
        
        if progress_callback:
            progress_callback("✅ Research completed")
        
        return research_data
        
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Error: {str(e)}")
        return {}

# ============================================================================
# ORDER PROCESSING
# ============================================================================

def process_order(order: Dict, claude_api_key: str, item_index: int = 0, progress_callback=None) -> Optional[Dict]:
    """Process a single order line item and return complete data
    
    Args:
        order: The Shopify order dict
        claude_api_key: API key for Claude
        item_index: Which line item to process (0 for first, 1 for second, etc.)
        progress_callback: Optional callback function for progress updates
    
    Returns:
        Dictionary with complete processed data for this line item
    """
    order_number = order["name"]
    
    # Add item suffix if multiple items
    line_item_count = get_line_item_count(order)
    if line_item_count > 1:
        display_order = f"{order_number} (Item {item_index + 1}/{line_item_count})"
    else:
        display_order = order_number
    
    if progress_callback:
        progress_callback(f"📋 Processing {display_order}...")
    
    # Extract personalization for this specific item
    personalization = extract_personalization_data(order, item_index)
    if not personalization:
        if progress_callback:
            progress_callback(f"⚠️ No personalization data found")
        return None
    
    full_name, birthday = personalization
    
    if progress_callback:
        progress_callback(f"👤 Customer: {full_name}")
        progress_callback(f"🎂 Birthday: {birthday}")
    
    # Parse birthday
    try:
        day, month, year = map(int, birthday.split('/'))
    except:
        if progress_callback:
            progress_callback("❌ Invalid birthday format")
        return None
    
    # Calculate fields
    day_of_week = get_day_of_week(day, month, year)
    month_name = get_month_name(month)
    star_sign = calculate_star_sign(month, day)
    birthstone = get_birthstone(month)
    
    # Delay if configured
    delay = st.session_state.settings.get('delay_between_orders', 1)
    if delay > 0:
        time.sleep(delay)
    
    # Research with Claude
    research_data = research_with_claude(month_name, day, year, claude_api_key, progress_callback)
    
    if not research_data:
        if st.session_state.settings.get('auto_retry_failed', True):
            if progress_callback:
                progress_callback("🔄 Retrying...")
            time.sleep(2)
            research_data = research_with_claude(month_name, day, year, claude_api_key, progress_callback)
            
        if not research_data:
            return None
    
    # Combine data
    complete_data = {
        "OrderID": display_order,  # Include item suffix if multiple items
        "Name": full_name.upper(),
        "DayOfWeek": day_of_week,
        "MonthName": month_name,
        "Day": day,
        "Year": year,
        "StarSign": star_sign,
        "Birthstone": birthstone,
    }
    
    complete_data.update(research_data)
    
    # ------------------------------------------------------------------
    # LOOKUP TABLE OVERRIDE
    # Replace the LLM's generated values for NRL, AFL, Bathurst 1000,
    # Australian Open, Oscar Best Actor/Actress, Prime Minister,
    # IncomingPM, and Monarch with verified static lookup data wherever
    # a match exists. These are finite, unchanging historical facts -
    # not generative content - so a hardcoded table removes this error
    # category entirely rather than relying on prompt accuracy.
    #
    # If the lookup table has no entry for this year (e.g. very old or
    # very recent dates not yet added), the LLM-generated value from
    # research_data above is left untouched as a fallback.
    # ------------------------------------------------------------------
    lookup_results = resolve_lookup_fields(day, month, year)
    fields_overridden = []
    for field_name, verified_value in lookup_results.items():
        if verified_value is not None:
            complete_data[field_name] = verified_value
            fields_overridden.append(field_name)
    
    if progress_callback and fields_overridden:
        progress_callback(f"✅ Verified from lookup tables: {', '.join(fields_overridden)}")
    
    if progress_callback:
        progress_callback(f"✅ {display_order} processed successfully")
    
    return complete_data

def generate_csv_filename(settings: dict) -> str:
    """Generate CSV filename based on settings"""
    template = settings.get('filename_format', 'orders_{date}_{time}')
    now = datetime.now()
    
    filename = template.replace('{date}', now.strftime('%Y-%m-%d'))
    filename = filename.replace('{time}', now.strftime('%H-%M-%S'))
    
    if not filename.endswith('.csv'):
        filename += '.csv'
    
    return filename

def save_csv(data: List[Dict], settings: dict) -> str:
    """Save processed data to CSV"""
    df = pd.DataFrame(data)
    filename = generate_csv_filename(settings)
    
    save_location = settings.get('auto_save_location', '.')
    filepath = os.path.join(save_location, filename)
    
    df.to_csv(filepath, index=False)
    
    return filepath

# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def main():
    """Main dashboard application"""
    
    # Get branding settings
    dashboard_name = st.session_state.settings.get('dashboard_name', 'The Day Archive - Dashboard V3')
    logo_file = st.session_state.settings.get('logo_file', 'logo.png')
    
    # Header with logo
    col1, col2 = st.columns([1, 4])
    with col1:
        try:
            st.image(logo_file, width=150)
        except:
            st.write("📅")
    with col2:
        st.title(dashboard_name)
        st.caption("Complete order processing with advanced settings")
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # API Credentials
        st.subheader("🔐 API Credentials")
        
        shopify_store = st.text_input(
            "Shopify Store URL",
            value=st.session_state.api_credentials.get('shopify_store', ''),
            placeholder="your-store.myshopify.com",
            help="Your Shopify store URL"
        )
        st.session_state.api_credentials['shopify_store'] = shopify_store
        
        shopify_token = st.text_input(
            "Shopify Access Token",
            value=st.session_state.api_credentials.get('shopify_token', ''),
            type="password",
            placeholder="shpat_...",
            help="Your Shopify Admin API access token"
        )
        st.session_state.api_credentials['shopify_token'] = shopify_token
        
        claude_api_key = st.text_input(
            "Claude API Key",
            value=st.session_state.api_credentials.get('claude_api_key', ''),
            type="password",
            placeholder="sk-ant-api03-...",
            help="Your Claude API key"
        )
        st.session_state.api_credentials['claude_api_key'] = claude_api_key
        
        # Test connections
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Test Shopify", use_container_width=True):
                with st.spinner("Testing..."):
                    if shopify_store and shopify_token:
                        orders = fetch_shopify_orders(shopify_token, shopify_store)
                        if orders:
                            st.success(f"✓ ({len(orders)})")
                        else:
                            st.error("✗ Failed")
                    else:
                        st.warning("Enter credentials")
        
        with col2:
            if st.button("Test Claude", use_container_width=True):
                if claude_api_key and claude_api_key.startswith('sk-ant-'):
                    st.success("✓ Valid")
                else:
                    st.error("✗ Invalid")
        
        st.markdown("---")
        
        # Quick Settings Access
        st.subheader("⚡ Quick Settings")
        
        test_mode = st.toggle(
            "🧪 Test Mode",
            value=st.session_state.get('test_mode', False),
            help="Process only selected orders (no auto-processing)"
        )
        st.session_state.test_mode = test_mode
        
        if test_mode:
            st.warning("⚠️ Test Mode Active - Only selected orders will process")
        
        batch_size = st.number_input(
            "Batch Size",
            min_value=1,
            max_value=100,
            value=st.session_state.settings.get('default_batch_size', 5),
            help="Orders to process at once"
        )
        st.session_state.settings['default_batch_size'] = batch_size
        
        if st.button("🎨 Open Full Settings", use_container_width=True):
            st.session_state.show_settings = True
        
        st.markdown("---")
        
        # Cost Tracker
        st.subheader("💰 Cost Tracker")
        st.metric("Processed Today", st.session_state.total_processed_today)
        cost = st.session_state.total_processed_today * 0.015
        st.metric("Estimated Cost", f"${cost:.2f}")
    
    # Show settings page if requested
    if st.session_state.get('show_settings', False):
        if st.button("← Back to Dashboard"):
            st.session_state.show_settings = False
            st.rerun()
        render_settings_page()
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Orders", "⚙️ Processing", "📊 History", "❌ Errors"])
    
    # ========================================================================
    # TAB 1: ORDERS
    # ========================================================================
    with tab1:
        st.header("Unfulfilled Orders")
        
        # Fetch orders
        if st.button("🔄 Refresh Orders", type="primary"):
            if shopify_store and shopify_token:
                with st.spinner("Fetching from Shopify..."):
                    orders = fetch_shopify_orders(shopify_token, shopify_store)
                    
                    # Filter unfulfilled
                    unfulfilled = [o for o in orders if o.get("fulfillment_status") != "fulfilled"]
                    
                    # Store
                    st.session_state.unfulfilled_orders = unfulfilled
                    st.success(f"Found {len(unfulfilled)} unfulfilled orders")
            else:
                st.error("Please enter API credentials in sidebar")
        
        # Display orders
        if 'unfulfilled_orders' in st.session_state and st.session_state.unfulfilled_orders:
            orders = st.session_state.unfulfilled_orders
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search = st.text_input("🔍 Search", placeholder="Order # or customer")
            
            with col2:
                date_filter = st.selectbox(
                    "📅 Filter by Date",
                    ["All Orders", "Today", "Yesterday", "Last 7 Days", "Last 30 Days"],
                    index=["All Orders", "Today", "Yesterday", "Last 7 Days", "Last 30 Days"].index(
                        st.session_state.settings.get('default_date_filter', 'All Orders')
                    )
                )
            
            with col3:
                sort_by = st.selectbox(
                    "Sort By",
                    ["Newest First", "Oldest First", "Order Number"],
                    index=["Newest First", "Oldest First", "Order Number"].index(
                        st.session_state.settings.get('sort_order', 'Newest First')
                    )
                )
            
            # Apply filters
            filtered = orders
            
            if search:
                filtered = [
                    o for o in filtered
                    if search.lower() in o['name'].lower() or 
                       search.lower() in o.get('email', '').lower()
                ]
            
            if date_filter == "Today":
                today = datetime.now().date()
                filtered = [
                    o for o in filtered
                    if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).date() == today
                ]
            elif date_filter == "Yesterday":
                yesterday = (datetime.now() - timedelta(days=1)).date()
                filtered = [
                    o for o in filtered
                    if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).date() == yesterday
                ]
            elif date_filter == "Last 7 Days":
                week_ago = (datetime.now() - timedelta(days=7)).date()
                filtered = [
                    o for o in filtered
                    if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).date() >= week_ago
                ]
            elif date_filter == "Last 30 Days":
                month_ago = (datetime.now() - timedelta(days=30)).date()
                filtered = [
                    o for o in filtered
                    if datetime.fromisoformat(o['created_at'].replace('Z', '+00:00')).date() >= month_ago
                ]
            
            # Sort
            if sort_by == "Newest First":
                filtered.sort(key=lambda x: x['created_at'], reverse=True)
            elif sort_by == "Oldest First":
                filtered.sort(key=lambda x: x['created_at'])
            else:
                filtered.sort(key=lambda x: int(x['name'].replace('#', '')))
            
            st.markdown(f"**Showing {len(filtered)} orders**")
            
            # Store filtered orders for callbacks
            if 'current_filtered_orders' not in st.session_state:
                st.session_state.current_filtered_orders = []
            st.session_state.current_filtered_orders = [o['name'] for o in filtered]
            
            # Selection controls with callbacks
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("✓ Select All", key="select_all_btn", use_container_width=True):
                    st.session_state.selected_orders = [o['name'] for o in filtered]
            with col2:
                if st.button("✗ Deselect All", key="deselect_all_btn", use_container_width=True):
                    st.session_state.selected_orders = []
            
            st.markdown(f"**Selected: {len(st.session_state.selected_orders)} orders**")
            st.markdown("---")
            
            # Order list - show each line item as a separate row
            for idx, order in enumerate(filtered):
                # Get number of line items in this order
                line_item_count = get_line_item_count(order)
                
                # Display each line item separately
                for item_idx in range(line_item_count):
                    personalization = extract_personalization_data(order, item_idx)
                    
                    # Extract values
                    full_name = personalization[0] if personalization else ""
                    birthday = personalization[1] if personalization else ""
                    
                    # Create unique keys for this order+item combination
                    item_key = f"{order['name']}_item{item_idx}"
                    edit_key = f"edit_{item_key}"
                    is_editing = st.session_state.get(edit_key, False)
                    
                    # Check if this order has notes (only check on first item)
                    has_notes = False
                    if item_idx == 0:
                        has_notes = bool(st.session_state.order_notes.get(order['name'], "").strip())
                    
                    # Apply background color if notes exist
                    if has_notes and item_idx == 0:
                        st.markdown(
                            f"<div style='background-color: #1F2937; padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0;'>",
                            unsafe_allow_html=True
                        )
                    
                    col1, col2, col3, col4, col5, col6 = st.columns([0.8, 2, 1.5, 1.5, 0.7, 2])
                    
                    with col1:
                        # Show order number (add suffix if multiple items)
                        display_name = order['name']
                        if line_item_count > 1:
                            display_name = f"{order['name']} ({item_idx + 1}/{line_item_count})"
                        
                        # Checkbox - only the first item of each order can be selected
                        if item_idx == 0:
                            is_checked = order['name'] in st.session_state.selected_orders
                            
                            if st.checkbox(
                                display_name,
                                value=is_checked,
                                key=f"cb_{item_key}_{is_checked}"
                            ):
                                if order['name'] not in st.session_state.selected_orders:
                                    st.session_state.selected_orders.append(order['name'])
                            else:
                                if order['name'] in st.session_state.selected_orders:
                                    st.session_state.selected_orders.remove(order['name'])
                        else:
                            # For subsequent items, just show the label
                            st.write(display_name)
                    
                    with col2:
                        if is_editing:
                            # Edit mode - show input field with current value
                            new_name = st.text_input(
                                "Full Name",
                                value=full_name,
                                key=f"edit_name_{item_key}",
                                placeholder="Enter full name",
                                label_visibility="collapsed"
                            )
                        else:
                            # Display mode - show value or "No data"
                            if full_name:
                                st.write(f"**{full_name}**")
                            else:
                                st.write("_No data_")
                    
                    with col3:
                        if is_editing:
                            # Edit mode - show input field with current value
                            new_birthday = st.text_input(
                                "Birthday",
                                value=birthday,
                                placeholder="DD/MM/YYYY",
                                key=f"edit_birthday_{item_key}",
                                label_visibility="collapsed"
                            )
                        else:
                            # Display mode - show value or dash
                            if birthday:
                                st.write(f"🎂 {birthday}")
                            else:
                                st.write("—")
                    
                    with col4:
                        # Only show date for first item of each order
                        if item_idx == 0:
                            order_date = datetime.fromisoformat(order['created_at'].replace('Z', '+00:00'))
                            st.write(f"📅 {order_date.strftime('%b %d, %Y')}")
                        else:
                            st.write("")  # Empty for subsequent items
                    
                    with col5:
                        # Show edit/save button for each line item
                        if not is_editing:
                            if st.button("✏️", key=f"btn_edit_{item_key}", use_container_width=True, help="Edit this item"):
                                st.session_state[edit_key] = True
                                st.rerun()
                        else:
                            # Show save/cancel buttons when editing
                            if st.button("💾", key=f"btn_save_{item_key}", use_container_width=True, help="Save changes"):
                                # Get the new values
                                name_input_key = f"edit_name_{item_key}"
                                birthday_input_key = f"edit_birthday_{item_key}"
                                
                                # Initialize order_edits if needed
                                if 'order_edits' not in st.session_state:
                                    st.session_state.order_edits = {}
                                
                                # Save the edits with item-specific key
                                st.session_state.order_edits[item_key] = {
                                    'full_name': st.session_state.get(name_input_key, ""),
                                    'birthday': st.session_state.get(birthday_input_key, "")
                                }
                                
                                # Exit edit mode
                                st.session_state[edit_key] = False
                                st.rerun()
                    
                    with col6:
                        # Internal notes - only for first item of each order
                        if item_idx == 0:
                            note_value = st.session_state.order_notes.get(order['name'], "")
                            note = st.text_input(
                                "Internal Notes",
                                value=note_value,
                                key=f"note_{order['name']}",
                                placeholder="Notes (won't be processed)",
                                label_visibility="collapsed",
                                help="Internal notes - only visible in dashboard, never sent to CSV or processing"
                            )
                            # Save note to session state AND to file
                            if note != note_value:
                                st.session_state.order_notes[order['name']] = note
                                # Save to persistent file
                                try:
                                    with open('order_notes.json', 'w') as f:
                                        json.dump(st.session_state.order_notes, f)
                                except:
                                    pass  # Silently fail if can't write
                    
                    # Close the background div if it was opened
                    if has_notes and item_idx == 0:
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Add a subtle separator between line items from the same order
                    if item_idx < line_item_count - 1:
                        st.markdown("<div style='border-bottom: 1px dashed #333; margin: 0.3rem 0;'></div>", unsafe_allow_html=True)
                
                # Add a stronger separator between different orders
                if idx < len(filtered) - 1:
                    st.markdown("<div style='border-bottom: 1px solid #555; margin: 0.8rem 0;'></div>", unsafe_allow_html=True)
        
        else:
            st.info("Click 'Refresh Orders' to load unfulfilled orders")
    
    # ========================================================================
    # TAB 2: PROCESSING
    # ========================================================================
    with tab2:
        st.header("Process Orders")
        
        if st.session_state.get('test_mode', False):
            st.info("🧪 **Test Mode Active** - Processing only selected orders")
        
        if st.session_state.selected_orders:
            st.success(f"Ready to process {len(st.session_state.selected_orders)} selected orders")
            
            if st.button("🚀 Process Selected Orders", type="primary", disabled=st.session_state.processing):
                if not claude_api_key:
                    st.error("Please enter Claude API key in sidebar")
                else:
                    st.session_state.processing = True
                    st.session_state.processed_orders = []
                    
                    # Progress containers
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    log_container = st.container()
                    
                    # Get selected orders
                    selected_objs = [
                        o for o in st.session_state.unfulfilled_orders
                        if o['name'] in st.session_state.selected_orders
                    ]
                    
                    # Calculate total items to process (not just orders)
                    total_items = sum(get_line_item_count(o) for o in selected_objs)
                    
                    # Process each order's line items
                    processed_count = 0
                    for order in selected_objs:
                        line_item_count = get_line_item_count(order)
                        
                        # Process each line item separately
                        for item_idx in range(line_item_count):
                            processed_count += 1
                            progress = processed_count / total_items
                            progress_bar.progress(progress)
                            
                            # Create display name
                            if line_item_count > 1:
                                display_name = f"{order['name']} (Item {item_idx + 1}/{line_item_count})"
                            else:
                                display_name = order['name']
                            
                            status_text.markdown(f"**Processing {processed_count} of {total_items}** ({display_name})")
                            
                            def log(msg):
                                with log_container:
                                    st.write(msg)
                                st.session_state.processing_log.append({
                                    "timestamp": datetime.now(),
                                    "order": display_name,
                                    "message": msg
                                })
                            
                            try:
                                order_data = process_order(order, claude_api_key, item_idx, log)
                                
                                if order_data:
                                    st.session_state.processed_orders.append(order_data)
                                    st.session_state.total_processed_today += 1
                                else:
                                    st.session_state.error_log.append({
                                        "timestamp": datetime.now(),
                                        "order": display_name,
                                        "error": "Processing failed"
                                    })
                            
                            except Exception as e:
                                st.session_state.error_log.append({
                                    "timestamp": datetime.now(),
                                    "order": display_name,
                                    "error": str(e)
                                })
                                log(f"❌ Error: {str(e)}")
                    
                    # Complete
                    st.session_state.processing = False
                    progress_bar.progress(1.0)
                    status_text.markdown("**✅ Processing Complete!**")
                    
                    # Generate CSV
                    if st.session_state.processed_orders:
                        try:
                            filepath = save_csv(
                                st.session_state.processed_orders,
                                st.session_state.settings
                            )
                            
                            st.success(f"✅ Generated {os.path.basename(filepath)}")
                            
                            # Download button
                            df = pd.DataFrame(st.session_state.processed_orders)
                            csv_data = df.to_csv(index=False).encode('utf-8')
                            
                            st.download_button(
                                label="📥 Download CSV",
                                data=csv_data,
                                file_name=os.path.basename(filepath),
                                mime="text/csv"
                            )
                            
                            # Preview
                            with st.expander("👁️ Preview Data"):
                                st.dataframe(df.head(10))
                        
                        except Exception as e:
                            st.error(f"Error saving CSV: {e}")
        
        else:
            st.info("Select orders from the Orders tab to process")
    
    # ========================================================================
    # TAB 3: HISTORY
    # ========================================================================
    with tab3:
        st.header("Processing History")
        
        if st.session_state.processing_log:
            st.markdown(f"**Total logs: {len(st.session_state.processing_log)}**")
            
            # Group by order
            by_order = {}
            for log in st.session_state.processing_log:
                order = log['order']
                if order not in by_order:
                    by_order[order] = []
                by_order[order].append(log)
            
            # Display
            for order, logs in by_order.items():
                with st.expander(f"📋 {order} ({len(logs)} events)"):
                    for log in logs:
                        st.caption(f"{log['timestamp'].strftime('%H:%M:%S')} - {log['message']}")
        
        else:
            st.info("No processing history yet")
        
        # Show processed orders
        if st.session_state.processed_orders:
            st.markdown("---")
            st.subheader("✅ Successfully Processed")
            
            for order_data in st.session_state.processed_orders:
                st.success(f"{order_data['OrderID']} - {order_data['Name']}")
    
    # ========================================================================
    # TAB 4: ERRORS
    # ========================================================================
    with tab4:
        st.header("Error Log")
        
        if st.session_state.error_log:
            st.error(f"**{len(st.session_state.error_log)} errors logged**")
            
            for error in st.session_state.error_log:
                with st.expander(f"❌ {error['order']} - {error['timestamp'].strftime('%H:%M:%S')}"):
                    st.code(error['error'])
                    
                    if st.button(f"🔄 Retry {error['order']}", key=f"retry_{error['order']}"):
                        st.info("Retry functionality coming soon")
        
        else:
            st.success("No errors! 🎉")

# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
