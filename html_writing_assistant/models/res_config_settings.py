from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gemini_api_key = fields.Char(
        string='Gemini API Key',
        config_parameter='html_writing_assistant.gemini_api_key',
        help='Google Gemini API key for writing assistance analysis'
    )
    
    gemini_model = fields.Selection([
        ('gemini-1.5-flash-latest', 'Gemini 1.5 Flash (Recommended)'),
        ('gemini-1.5-pro-latest', 'Gemini 1.5 Pro'),
        ('gemini-pro', 'Gemini Pro'),
        ('gemini-2.0-flash', 'Gemini 2.0 Flash'),
        ('gemini-2.5-flash', 'Gemini 2.5 Flash'),
        ('gemini-2.5-pro', 'Gemini 2.5 Pro'),
    ], string='Gemini Model',
        config_parameter='html_writing_assistant.gemini_model',
        default='gemini-1.5-flash-latest',
        help='Choose the Gemini model for text analysis'
    )
    
    gemini_temperature = fields.Float(
        string='Temperature',
        config_parameter='html_writing_assistant.gemini_temperature', 
        default=0.2,
        help='Controls randomness in AI responses (0.0 = deterministic, 1.0 = very random)'
    )
    
    max_suggestions = fields.Integer(
        string='Max Suggestions',
        config_parameter='html_writing_assistant.max_suggestions',
        default=15,
        help='Maximum number of suggestions to return per analysis'
    )
    
    enable_fallback = fields.Boolean(
        string='Enable Fallback Mode',
        config_parameter='html_writing_assistant.enable_fallback',
        default=True,
        help='Use built-in suggestions when Gemini API is unavailable'
    )
    
    gemini_timeout = fields.Integer(
        string='API Timeout (seconds)',
        config_parameter='html_writing_assistant.gemini_timeout',
        default=30,
        help='Timeout for Gemini API requests in seconds'
    )
    
    @api.model 
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            gemini_api_key=self.env['ir.config_parameter'].sudo().get_param('html_writing_assistant.gemini_api_key', ''),
            gemini_model=self.env['ir.config_parameter'].sudo().get_param('html_writing_assistant.gemini_model', 'gemini-1.5-flash-latest'),
            gemini_temperature=float(self.env['ir.config_parameter'].sudo().get_param('html_writing_assistant.gemini_temperature', 0.2)),
            max_suggestions=int(self.env['ir.config_parameter'].sudo().get_param('html_writing_assistant.max_suggestions', 15)),
            enable_fallback=self.env['ir.config_parameter'].sudo().get_param('html_writing_assistant.enable_fallback', 'True').lower() == 'true',
            gemini_timeout=int(self.env['ir.config_parameter'].sudo().get_param('html_writing_assistant.gemini_timeout', 30)),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('html_writing_assistant.gemini_api_key', self.gemini_api_key or '')
        self.env['ir.config_parameter'].sudo().set_param('html_writing_assistant.gemini_model', self.gemini_model)
        self.env['ir.config_parameter'].sudo().set_param('html_writing_assistant.gemini_temperature', self.gemini_temperature)
        self.env['ir.config_parameter'].sudo().set_param('html_writing_assistant.max_suggestions', self.max_suggestions)
        self.env['ir.config_parameter'].sudo().set_param('html_writing_assistant.enable_fallback', self.enable_fallback)
        self.env['ir.config_parameter'].sudo().set_param('html_writing_assistant.gemini_timeout', self.gemini_timeout)
    
    def test_gemini_connection(self):
        """Test Gemini API connection"""
        if not self.gemini_api_key:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Configuration Error',
                    'message': 'Please enter a Gemini API key first.',
                    'type': 'warning',
                }
            }
        
        try:
            # Make a test request to verify the API key
            import requests
            import json
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
            
            test_payload = {
                "contents": [{
                    "parts": [{
                        "text": "Test message. Just respond with 'OK'."
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 10
                }
            }
            
            response = requests.post(
                api_url, 
                headers={'Content-Type': 'application/json'},
                json=test_payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification', 
                    'params': {
                        'title': 'Connection Successful',
                        'message': 'Gemini API connection test passed successfully!',
                        'type': 'success',
                    }
                }
            else:
                error_msg = f"API Error: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error'].get('message', error_msg)
                except:
                    pass
                    
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Connection Failed',
                        'message': f'Gemini API test failed: {error_msg}',
                        'type': 'danger',
                    }
                }
                
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Error',
                    'message': f'Failed to connect to Gemini API: {str(e)}',
                    'type': 'danger',
                }
            }
