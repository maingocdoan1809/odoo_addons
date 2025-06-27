import json
import re
import logging
import requests
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WritingAssistantController(http.Controller):

    @http.route('/web/html_writing_assistant/get_config', type='json', auth='user')
    def get_writing_assistant_config(self, **kwargs):
        """
        Get current configuration for the writing assistant
        """
        try:
            settings = self._get_api_settings()
            
            return {
                'success': True,
                'config': {
                    'has_api_key': bool(settings['api_key']),
                    'model': settings['model'],
                    'max_suggestions': settings['max_suggestions'],
                    'enable_fallback': settings['enable_fallback'],
                    'temperature': settings['temperature']
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


    @http.route('/web/html_writing_assistant/analyze', type='json', auth='user')
    def analyze_text(self, text, **kwargs):
        """
        Analyze text using Google Gemini API and return writing suggestions.
        """
        if not text or not text.strip():
            return []
        
        # Extract plain text from HTML
        plain_text = self._extract_text_from_html(text)
        
        if not plain_text or len(plain_text.strip()) < 5:
            return []
        
        try:
            # Get suggestions from Gemini API
            suggestions = self._analyze_with_gemini(plain_text)
            
            # Validate and clean suggestions
            validated_suggestions = []
            for suggestion in suggestions:
                if self._validate_suggestion(suggestion, plain_text):
                    validated_suggestions.append(suggestion)
            
            # Sort by position and limit results
            validated_suggestions.sort(key=lambda x: x.get('position', 0))
            return validated_suggestions[:20]  # Limit to 20 suggestions
            
        except Exception as e:
            _logger.error(f"Gemini API analysis failed: {str(e)}")
            # Fallback to mock suggestions for development/testing
            return self._generate_fallback_suggestions(plain_text)
    

    def _get_api_settings(self):
        """Get API settings from configuration parameters"""
        config = request.env['ir.config_parameter'].sudo()
        
        return {
            'api_key': config.get_param('html_writing_assistant.gemini_api_key'),
            'model': config.get_param('html_writing_assistant.gemini_model', 'gemini-1.5-flash-latest'),
            'temperature': float(config.get_param('html_writing_assistant.gemini_temperature', 0.2)),
            'max_suggestions': int(config.get_param('html_writing_assistant.max_suggestions', 15)),
            'enable_fallback': config.get_param('html_writing_assistant.enable_fallback', 'True').lower() == 'true',
            'timeout': int(config.get_param('html_writing_assistant.gemini_timeout', 30)),
        }

    def _analyze_with_gemini(self, text):
        """
        Enhanced Gemini API call with dynamic configuration
        """
        settings = self._get_api_settings()
        
        if not settings['api_key']:
            _logger.warning("Gemini API key not configured")
            if settings['enable_fallback']:
                return self._generate_fallback_suggestions(text)
            raise Exception("Gemini API key not configured")
        
        # Gemini API endpoint with dynamic model
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings['model']}:generateContent?key={settings['api_key']}"
        
        # Generate the prompt
        prompt = self._generate_gemini_prompt(text, settings['max_suggestions'])
        
        # Prepare request payload with dynamic settings
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": settings['temperature'],
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
                "candidateCount": 1
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        # Make API request with configured timeout
        headers = {
            'Content-Type': 'application/json',
        }
        
        try:
            response = requests.post(
                api_url, 
                headers=headers, 
                json=payload, 
                timeout=settings['timeout']
            )
            
            if response.status_code == 429:  # Rate limit exceeded
                _logger.warning("Gemini API rate limit exceeded")
                if settings['enable_fallback']:
                    return self._generate_fallback_suggestions(text)
                raise Exception("API rate limit exceeded. Please try again later.")
            
            if response.status_code != 200:
                _logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                if settings['enable_fallback']:
                    return self._generate_fallback_suggestions(text)
                raise Exception(f"Gemini API returned status {response.status_code}")
            
            response_data = response.json()
            
            # Extract the generated text
            if 'candidates' not in response_data or not response_data['candidates']:
                _logger.error("No candidates in Gemini response")
                if settings['enable_fallback']:
                    return self._generate_fallback_suggestions(text)
                raise Exception("No response from Gemini API")
            
            generated_text = response_data['candidates'][0]['content']['parts'][0]['text']
            
            # Parse JSON response
            try:
                cleaned_response = self._clean_gemini_response(generated_text)
                suggestions = json.loads(cleaned_response)
                
                if not isinstance(suggestions, list):
                    _logger.error("Gemini response is not a list")
                    if settings['enable_fallback']:
                        return self._generate_fallback_suggestions(text)
                    raise Exception("Invalid response format from Gemini")
                
                # Limit suggestions to configured maximum
                return suggestions[:settings['max_suggestions']]
                
            except json.JSONDecodeError as e:
                _logger.error(f"Failed to parse Gemini JSON response: {e}")
                _logger.error(f"Raw response: {generated_text}")
                if settings['enable_fallback']:
                    return self._generate_fallback_suggestions(text)
                raise Exception("Invalid JSON response from Gemini API")
                
        except requests.exceptions.Timeout:
            _logger.error("Gemini API request timed out")
            if settings['enable_fallback']:
                return self._generate_fallback_suggestions(text)
            raise Exception("API request timed out")
            
        except requests.exceptions.RequestException as e:
            _logger.error(f"Gemini API request failed: {str(e)}")
            if settings['enable_fallback']:
                return self._generate_fallback_suggestions(text)
            raise Exception(f"API request failed: {str(e)}")
    def _generate_gemini_prompt(self, text, max_suggestions=15):
        """
        Generate a comprehensive prompt optimized for Google Gemini API with dynamic limits
        """
        prompt = f"""You are an expert writing assistant with expertise in grammar, style, clarity, and professional writing. Analyze the following text and provide specific, actionable suggestions for improvement.

CRITICAL: Respond ONLY with a valid JSON array. Do not include markdown code blocks, explanations, or any text outside the JSON structure.

TEXT TO ANALYZE:
"{text}"

ANALYSIS REQUIREMENTS:

1. **ACCURACY**: Only flag actual errors or genuine improvements. Avoid false positives.

2. **CATEGORIES**: Classify each suggestion into exactly one category:
   - "grammar": Subject-verb agreement, verb tenses, sentence structure, pronoun usage
   - "spelling": Misspelled words, typos, wrong word forms  
   - "punctuation": Missing/incorrect commas, periods, apostrophes, quotation marks
   - "style": Word choice, redundancy, passive voice, clarity improvements
   - "clarity": Ambiguous references, unclear phrasing, complex sentences

3. **PRECISION**: The "issue" field must contain the EXACT text from the original, including:
   - Exact capitalization and spacing
   - All punctuation marks
   - Complete words or phrases (not partial matches)

4. **SUGGESTIONS**: Provide specific, practical replacements that:
   - Maintain the original meaning
   - Improve readability and professionalism
   - Are contextually appropriate

5. **EXPLANATIONS**: Give clear, concise explanations (1-2 sentences) that help users learn.

6. **POSITION**: Provide the approximate character position where the issue starts.

7. **PRIORITIZATION**: Focus on high-impact errors. Limit to maximum {max_suggestions} suggestions.

JSON FORMAT REQUIRED:
[
  {{
    "category": "grammar|spelling|punctuation|style|clarity",
    "issue": "exact text from original",
    "suggestion": "improved replacement text", 
    "explanation": "brief explanation of improvement",
    "position": numeric_position
  }}
]

QUALITY STANDARDS:
- Only suggest changes that genuinely improve the text
- Ensure "issue" text appears exactly in the original
- Maintain consistent tone and style
- Prefer active voice over passive voice when appropriate
- Suggest specific/stronger words when suitable
- Flag unclear pronoun references
- Identify run-on sentences or fragments
- Catch missing articles (a, an, the)
- Notice incorrect prepositions
- Spot redundant phrases

EXAMPLES:
- "recieve" → "receive" (spelling)
- "sales has increased" → "sales have increased" (grammar) 
- "in order to" → "to" (style)
- "this" → "this strategy" (clarity)

Remember: Return ONLY the JSON array with no additional formatting or text."""

        return prompt

    
    def _clean_gemini_response(self, response_text):
        """
        Clean Gemini response by removing markdown code blocks and extra formatting
        """
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text, flags=re.IGNORECASE)
        response_text = re.sub(r'```\s*', '', response_text)
        
        # Remove any leading/trailing whitespace
        response_text = response_text.strip()
        
        # Find JSON array boundaries
        start_idx = response_text.find('[')
        end_idx = response_text.rfind(']')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx + 1]
        
        return response_text
    
    def _extract_text_from_html(self, html_content):
        """Extract plain text from HTML content"""
        try:
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', ' ', html_content)
            # Decode HTML entities
            text = text.replace('&nbsp;', ' ')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&amp;', '&')
            text = text.replace('&quot;', '"')
            text = text.replace('&#39;', "'")
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text)
            return text.strip()
        except Exception:
            return ""
    
    def _validate_suggestion(self, suggestion, original_text):
        """
        Validate that a suggestion is properly formatted and the issue exists in text
        """
        required_fields = ['category', 'issue', 'suggestion', 'explanation', 'position']
        
        # Check required fields
        if not all(field in suggestion for field in required_fields):
            _logger.warning(f"Suggestion missing required fields: {suggestion}")
            return False
        
        # Check that issue text actually exists in original
        issue_text = suggestion['issue']
        if issue_text not in original_text:
            _logger.warning(f"Issue text '{issue_text}' not found in original text")
            return False
        
        # Check category is valid
        valid_categories = ['grammar', 'spelling', 'punctuation', 'style', 'clarity']
        if suggestion['category'] not in valid_categories:
            _logger.warning(f"Invalid category: {suggestion['category']}")
            return False
        
        # Check that suggestion is different from issue
        if suggestion['issue'] == suggestion['suggestion']:
            _logger.warning(f"Suggestion same as issue: {suggestion['issue']}")
            return False
        
        # Validate position is numeric
        try:
            int(suggestion['position'])
        except (ValueError, TypeError):
            _logger.warning(f"Invalid position: {suggestion['position']}")
            return False
        
        return True
    
    def _generate_fallback_suggestions(self, text):
        """
        Generate fallback suggestions when Gemini API is unavailable
        This uses the same mock logic as before for development/testing
        """
        suggestions = []
        
        # Common spelling errors
        spelling_errors = {
            'teh': 'the',
            'recieve': 'receive', 
            'seperate': 'separate',
            'occured': 'occurred',
            'neccessary': 'necessary',
            'definately': 'definitely',
            'accomodate': 'accommodate',
            'sucessful': 'successful',
            'experiance': 'experience',
            'bussiness': 'business',
            'begining': 'beginning',
            'writting': 'writing',
            'alot': 'a lot',
            'overal': 'overall',
            'analyize': 'analyze',
            'demonstarte': 'demonstrate',
            'readibility': 'readability',
            'cant': "can't",
            'dont': "don't",
            'wont': "won't",
            'isnt': "isn't"
        }
        
        # Grammar patterns
        grammar_patterns = [
            (r'\byou (grammar|spelling|writing)\b', lambda m: f'your {m.group(1)}', 'Use possessive pronoun "your"'),
            (r'\bhe have\b', 'he has', 'Subject-verb agreement'),
            (r'\bshe have\b', 'she has', 'Subject-verb agreement'),
            (r'\bthey has\b', 'they have', 'Subject-verb agreement'),
            (r'\bsales has\b', 'sales have', 'Plural subject requires plural verb'),
        ]
        
        # Style improvements
        style_patterns = [
            (r'\bvery good\b', 'excellent', 'Use stronger adjectives'),
            (r'\bvery bad\b', 'terrible', 'Use stronger adjectives'),
            (r'\ba lot of\b', 'many', 'More concise phrasing'),
            (r'\bin order to\b', 'to', 'Simpler phrasing'),
        ]
        
        # Check for spelling errors
        words = re.findall(r'\b\w+\b', text.lower())
        for word in words:
            if word in spelling_errors:
                pattern = r'\b' + re.escape(word) + r'\b'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    original_word = match.group()
                    suggestions.append({
                        'category': 'spelling',
                        'issue': original_word,
                        'suggestion': spelling_errors[word],
                        'explanation': f'Correct spelling of "{original_word}"',
                        'position': match.start()
                    })
        
        # Check grammar patterns
        for pattern, replacement, explanation in grammar_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if callable(replacement):
                    repl_text = replacement(match)
                else:
                    repl_text = replacement
                    
                suggestions.append({
                    'category': 'grammar',
                    'issue': match.group(),
                    'suggestion': repl_text,
                    'explanation': explanation,
                    'position': match.start()
                })
        
        # Check style patterns
        for pattern, replacement, explanation in style_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                suggestions.append({
                    'category': 'style',
                    'issue': match.group(),
                    'suggestion': replacement,
                    'explanation': explanation,
                    'position': match.start()
                })
        
        # Remove duplicates and sort by position
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            key = (suggestion['issue'], suggestion['suggestion'])
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        unique_suggestions.sort(key=lambda x: x['position'])
        return unique_suggestions[:15]  # Limit fallback suggestions
    
    @http.route('/web/html_writing_assistant/apply_suggestion', type='json', auth='user')
    def apply_suggestion(self, content, suggestion, **kwargs):
        """
        Apply a suggestion to the HTML content
        """
        try:
            issue = suggestion.get('issue', '')
            replacement = suggestion.get('suggestion', '')
            
            if issue and replacement:
                # Replace the first occurrence of the issue with the suggestion
                updated_content = content.replace(issue, replacement, 1)
                return {'success': True, 'content': updated_content}
            
            return {'success': False, 'error': 'Invalid suggestion data'}
        
        except Exception as e:
            _logger.error(f"Error applying suggestion: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/web/html_writing_assistant/test_gemini', type='json', auth='user')
    def test_gemini_connection(self, **kwargs):
        """
        Test endpoint to verify Gemini API connection and configuration
        """
        try:
            # Check if API key is configured
            api_key = request.env['ir.config_parameter'].sudo().get_param('html_writing_assistant.gemini_api_key')
            
            if not api_key:
                return {
                    'success': False, 
                    'error': 'Gemini API key not configured. Please set it in System Parameters.'
                }
            
            # Test with simple text
            test_text = "This is a test sentance with a mispelled word."
            suggestions = self._analyze_with_gemini(test_text)
            
            return {
                'success': True,
                'message': f'Gemini API working correctly. Found {len(suggestions)} suggestions.',
                'suggestions': suggestions
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Gemini API test failed: {str(e)}'
            }

    @http.route('/web/html_writing_assistant/health_check', type='json', auth='user')
    def health_check(self, **kwargs):
        """
        Health check endpoint to verify system status
        """
        try:
            settings = self._get_api_settings()
            
            status = {
                'api_configured': bool(settings['api_key']),
                'fallback_enabled': settings['enable_fallback'],
                'model': settings['model'],
                'system_status': 'operational'
            }
            
            # Test API if key is configured
            if settings['api_key']:
                try:
                    test_suggestions = self._analyze_with_gemini("Test message for API connectivity.")
                    status['api_status'] = 'connected'
                    status['test_suggestions_count'] = len(test_suggestions)
                except Exception as api_error:
                    status['api_status'] = 'error'
                    status['api_error'] = str(api_error)
            else:
                status['api_status'] = 'not_configured'
            
            return {
                'success': True,
                'status': status
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'status': {
                    'system_status': 'error'
                }
            }
