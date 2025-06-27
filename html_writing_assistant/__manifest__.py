{
    'name': 'HTML Writing Assistant',
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': 'AI-powered writing assistant for HTML fields using Google Gemini',
    'description': """
        HTML Writing Assistant Widget for Odoo 18
        =========================================
        
        This module provides an AI-powered writing assistant widget that extends 
        the standard HTML field with grammar, spelling, and style suggestions
        powered by Google Gemini AI.
        
        Features:
        - Real-time text analysis with Google Gemini AI
        - Grammar, spelling, punctuation, style, and clarity checks
        - Interactive suggestions with one-click apply
        - Categorized suggestion filtering
        - Clean and intuitive user interface
        - Configurable API settings
        - Fallback mode for offline use
        - Rate limiting and error handling
        
        Setup:
        1. Get a Google Gemini API key from Google AI Studio
        2. Configure the API key in Settings > Writing Assistant
        3. Add widget="html_writing_assistant" to any HTML field
        
        Usage:
        Add widget="html_writing_assistant" to any HTML field in your views.
    """,
    'author': 'MaiNgocDoan',
    'website': 'https://www.doandeptrai.io.vn',
    'depends': ['base', 'web', 'html_editor'],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/ir.model.access.csv',
        'views/demo_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'html_writing_assistant/static/src/fields/html_writing_assistant_field.xml',
            'html_writing_assistant/static/src/fields/html_writing_assistant_field.js',
            'html_writing_assistant/static/src/fields/html_writing_assistant_field.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
    'price': 0,
    'currency': 'EUR',
    'support': 'maidoan2002ns@gmail.com',
}
