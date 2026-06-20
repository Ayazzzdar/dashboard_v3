"""
Settings Manager for Dashboard V2
Handles save/load/import/export of all user settings
"""

import json
import os
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = ".dashboard_settings.json"

DEFAULT_SETTINGS = {
    # Branding
    'dashboard_name': 'The Day Archive - Dashboard V2',
    'logo_file': 'logo.png',
    
    # Brand Colors
    'primary_color': '#1E3A8A',      # Navy Blue
    'accent_color': '#D1D5DB',        # Light Gray
    'background_color': '#000000',    # Black
    'text_color': '#FFFFFF',          # White
    'sidebar_color': '#1F2937',       # Dark Gray
    
    # Display Preferences
    'font_size': 'Medium',
    'compact_mode': False,
    'show_thumbnails': True,
    'dark_mode': True,
    
    # Processing Defaults
    'default_batch_size': 5,
    'auto_refresh_minutes': 0,
    'default_date_filter': 'All Orders',
    'auto_select_new': False,
    
    # Notifications
    'desktop_notifications': False,
    'sound_alert': False,
    'email_notifications': False,
    'notification_email': '',
    'slack_webhook': '',
    
    # CSV Export Options
    'filename_format': 'orders_{date}_{time}',
    'auto_save_location': '.',
    'include_notes': False,
    'decimal_precision': 2,
    
    # API Rate Limiting
    'delay_between_orders': 1,
    'max_concurrent': 1,
    'auto_retry_failed': True,
    'timeout_duration': 120,
    
    # Dashboard Layout
    'sidebar_default_open': True,
    'sort_order': 'Newest First',
    'items_per_page': 20,
    
    # Advanced
    'debug_mode': False,
    'show_api_logs': False,
}

def save_settings(settings: dict) -> bool:
    """Save settings to JSON file"""
    try:
        settings['last_saved'] = datetime.now().isoformat()
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def load_settings() -> dict:
    """Load settings from JSON file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                saved = json.load(f)
                # Merge with defaults in case new settings were added
                settings = DEFAULT_SETTINGS.copy()
                settings.update(saved)
                return settings
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS.copy()
    return DEFAULT_SETTINGS.copy()

def export_settings(settings: dict) -> str:
    """Export settings as JSON string for download"""
    export_data = settings.copy()
    export_data['exported_at'] = datetime.now().isoformat()
    export_data['dashboard_version'] = '2.0'
    return json.dumps(export_data, indent=2)

def import_settings(json_string: str) -> dict:
    """Import settings from JSON string"""
    try:
        imported = json.loads(json_string)
        # Validate and merge with defaults
        settings = DEFAULT_SETTINGS.copy()
        for key in DEFAULT_SETTINGS.keys():
            if key in imported:
                settings[key] = imported[key]
        return settings
    except Exception as e:
        print(f"Error importing settings: {e}")
        return None

def reset_settings() -> dict:
    """Reset all settings to defaults"""
    return DEFAULT_SETTINGS.copy()

def get_color_presets() -> dict:
    """Get predefined color themes"""
    return {
        'Day Archive Dark': {
            'primary_color': '#1E3A8A',
            'accent_color': '#D1D5DB',
            'background_color': '#000000',
            'text_color': '#FFFFFF',
            'sidebar_color': '#1F2937',
        },
        'Day Archive Light': {
            'primary_color': '#1E3A8A',
            'accent_color': '#3B82F6',
            'background_color': '#FFFFFF',
            'text_color': '#111827',
            'sidebar_color': '#F3F4F6',
        },
        'Sunset': {
            'primary_color': '#DC2626',
            'accent_color': '#F59E0B',
            'background_color': '#1F2937',
            'text_color': '#F9FAFB',
            'sidebar_color': '#111827',
        },
        'Ocean': {
            'primary_color': '#0EA5E9',
            'accent_color': '#06B6D4',
            'background_color': '#0F172A',
            'text_color': '#F1F5F9',
            'sidebar_color': '#1E293B',
        },
    }
