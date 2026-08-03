import google.generativeai as genai
from django.conf import settings
from PIL import Image
import requests
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class GeminiVerifier:
    """
    Real AI verification using Google's Gemini API
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.vision_model = genai.GenerativeModel('gemini-1.5-pro')
    
    def verify_post(self, post):
        """
        Full verification pipeline
        """
        try:
            # Step 1: Analyze image
            image_analysis = self._analyze_image(post.image_url)
            
            # Step 2: Analyze context
            context_analysis = self._analyze_context(post)
            
            # Step 3: Combine results
            final_score = (image_analysis['score'] * 0.6) + (context_analysis['score'] * 0.4)
            
            return {
                'is_authentic': final_score > 0.6,
                'score': final_score,
                'image_analysis': image_analysis,
                'context_analysis': context_analysis,
                'status': 'verified'
            }
        except Exception as e:
            logger.error(f"Gemini verification failed: {str(e)}")
            return self._fallback_verification(post)
    
    def _analyze_image(self, image_url):
        """
        Analyze image for authenticity using Gemini Vision
        """
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            img = Image.open(BytesIO(response.content))
            
            prompt = """
            Analyze this image and determine:
            1. Is this a real photo or AI-generated?
            2. Does it show genuine human activity?
            3. Is there evidence of photo manipulation?
            
            Reply in JSON format:
            {
                "is_real": true/false,
                "confidence": 0-100,
                "reason": "brief explanation"
            }
            """
            
            # Use Gemini Vision
            response = self.vision_model.generate_content([prompt, img])
            
            # Parse response
            import json
            try:
                result = json.loads(response.text)
                return {
                    'score': result.get('confidence', 50) / 100,
                    'is_real': result.get('is_real', False),
                    'reason': result.get('reason', 'No reason provided')
                }
            except:
                # Fallback parse
                text = response.text.lower()
                if 'real' in text and 'true' in text:
                    return {'score': 0.7, 'is_real': True, 'reason': 'Looks authentic'}
                else:
                    return {'score': 0.3, 'is_real': False, 'reason': 'Suspicious image'}
        
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            return {'score': 0.5, 'is_real': True, 'reason': 'Image analysis error'}
    
    def _analyze_context(self, post):
        """
        Analyze caption and context for authenticity
        """
        try:
            prompt = f"""
            Analyze this post for authenticity:
            
            Caption: {post.caption}
            Location: {post.location or 'Not specified'}
            Hashtags: {post.hashtags or 'None'}
            
            Determine:
            1. Is this a genuine good deed or suspicious?
            2. Does the description match a real-world activity?
            3. Are there any red flags?
            
            Reply in JSON format:
            {{
                "is_authentic": true/false,
                "confidence": 0-100,
                "reason": "brief explanation",
                "red_flags": ["list of concerns"]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            import json
            try:
                result = json.loads(response.text)
                return {
                    'score': result.get('confidence', 50) / 100,
                    'is_authentic': result.get('is_authentic', False),
                    'reason': result.get('reason', 'No reason provided'),
                    'red_flags': result.get('red_flags', [])
                }
            except:
                return {'score': 0.5, 'is_authentic': True, 'reason': 'Context analysis error'}
        
        except Exception as e:
            logger.error(f"Context analysis failed: {str(e)}")
            return {'score': 0.5, 'is_authentic': True, 'reason': 'Context analysis error'}
    
    def _fallback_verification(self, post):
        """
        Fallback if Gemini fails
        """
        # Simple keyword check
        keywords = ['clean', 'plant', 'donate', 'help', 'volunteer', 
                   'blood', 'tree', 'food', 'education', 'health', 'recycle']
        caption_lower = post.caption.lower()
        found = [kw for kw in keywords if kw in caption_lower]
        
        if len(found) >= 2:
            return {
                'is_authentic': True,
                'score': 0.8,
                'details': {'fallback': True, 'keywords': found},
                'status': 'verified'
            }
        elif len(found) >= 1:
            return {
                'is_authentic': True,
                'score': 0.6,
                'details': {'fallback': True, 'keywords': found},
                'status': 'verified'
            }
        else:
            return {
                'is_authentic': False,
                'score': 0.2,
                'details': {'fallback': True, 'keywords': []},
                'status': 'flagged'
            }