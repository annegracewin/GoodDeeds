import logging
import json
import re
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)

def log(msg):
    print(f"🔍 {msg}")


class GeminiVerifier:
    """
    AI verification using Groq with explicit sarcasm detection.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.AGNES_API_KEY,
            base_url=settings.AGNES_BASE_URL,
        )
        self.model = settings.AGNES_MODEL

    def verify_post(self, post):
        log(f"Processing post: {post.caption[:50]}...")

        try:
            # ---- 1. Image analysis ----
            image_analysis = self._keyword_image_analysis(post)
            log(f"Image score: {image_analysis['score']}")

            # ---- 2. Context analysis (AI) ----
            context_analysis = self._analyze_context(post)
            log(f"AI context score: {context_analysis['score']}")
            log(f"AI is_authentic: {context_analysis.get('is_authentic')}")
            log(f"AI red_flags: {context_analysis.get('red_flags', [])}")

            # ---- 3. Override context score if AI flagged as not authentic ----
            if not context_analysis.get('is_authentic', True):
                log("⚠️ AI flagged as inauthentic – overriding context score to 0.2")
                context_analysis['score'] = 0.2
                if not context_analysis.get('red_flags'):
                    context_analysis['red_flags'] = ['AI flagged as inauthentic']

            # ---- 4. Combine scores ----
            final_score = (image_analysis['score'] * 0.6) + (context_analysis['score'] * 0.4)
            log(f"Initial final score: {final_score:.2f}")

            # ---- 5. Extra sarcasm check (if AI didn't flag) ----
            if context_analysis.get('is_authentic', True):
                sarcasm_indicators = ['just kidding', 'lol', 'im broke', 'not really',
                                      'lmao', 'rofl', 'jk', 'haha', 'funny', 'joke',
                                      'sarcasm', 'wouldn\'t that be cool', 'imagine if']
                caption_lower = post.caption.lower()
                if any(phrase in caption_lower for phrase in sarcasm_indicators):
                    log("🚨 Sarcasm indicator found in caption!")
                    context_analysis['is_authentic'] = False
                    context_analysis['score'] = 0.2
                    context_analysis['red_flags'].append('Sarcasm or joke detected')
                    final_score = (image_analysis['score'] * 0.6) + (0.2 * 0.4)
                    log(f"After sarcasm penalty: {final_score:.2f}")

            # ---- 6. Ensure score in [0,1] ----
            final_score = max(0, min(1, final_score))

            is_authentic = final_score >= 0.6
            status = 'verified' if is_authentic else 'flagged'

            log(f"Final decision: {status} (score: {final_score:.2f})")

            return {
                'is_authentic': is_authentic,
                'score': final_score,
                'image_analysis': image_analysis,
                'context_analysis': context_analysis,
                'status': status
            }

        except Exception as e:
            log(f"❌ AI verification failed with error: {e}")
            return self._fallback_verification(post)

    def _keyword_image_analysis(self, post):
        keywords = ['clean', 'plant', 'donate', 'help', 'volunteer',
                   'blood', 'tree', 'food', 'education', 'health', 'recycle']
        caption_lower = post.caption.lower()
        found = [kw for kw in keywords if kw in caption_lower]
        if len(found) >= 2:
            return {'score': 0.8, 'is_real': True, 'reason': 'Multiple good keywords'}
        elif len(found) >= 1:
            return {'score': 0.6, 'is_real': True, 'reason': 'Good keyword'}
        else:
            return {'score': 0.5, 'is_real': True, 'reason': 'No relevant keywords'}

    def _analyze_context(self, post):
        prompt = f"""
        Analyse this post for authenticity. Be strict.

        Caption: {post.caption}
        Location: {post.location or 'Not specified'}
        Hashtags: {post.hashtags or 'None'}

        INSTRUCTIONS:
        - If the post contains sarcasm, jokes, contradictions, or unrealistic claims, it MUST be flagged as suspicious.
        - Examples of red flags: "just kidding", "lol", "I'm broke", "not really", "imagine if", unrealistic amounts, etc.
        - A genuine good deed post should be sincere and not make fun of charity.

        Reply ONLY in valid JSON:
        {{
            "is_authentic": true/false,
            "confidence": 0-100,
            "reason": "brief explanation",
            "red_flags": ["list of concerns"]
        }}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            result_text = response.choices[0].message.content
            log(f"Raw AI response: {result_text[:200]}...")

            # Extract JSON
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(result_text)

            return {
                'score': result.get('confidence', 50) / 100,
                'is_authentic': result.get('is_authentic', False),
                'reason': result.get('reason', 'No reason provided'),
                'red_flags': result.get('red_flags', [])
            }

        except Exception as e:
            log(f"⚠️ Groq API error: {e}. Using keyword fallback.")
            return self._fallback_context_analysis(post)

    def _fallback_context_analysis(self, post):
        keywords = ['clean', 'plant', 'donate', 'help', 'volunteer',
                   'blood', 'tree', 'food', 'education', 'health', 'recycle']
        caption_lower = post.caption.lower()
        found = [kw for kw in keywords if kw in caption_lower]
        # Also check for sarcasm indicators in fallback
        sarcasm_phrases = ['just kidding', 'lol', 'im broke', 'not really', 'joke', 'imagine if']
        if any(p in caption_lower for p in sarcasm_phrases):
            log("⚠️ Fallback: sarcasm detected via keyword check.")
            return {'score': 0.2, 'is_authentic': False, 'reason': 'Sarcasm/joke detected', 'red_flags': ['Sarcasm']}
        if len(found) >= 2:
            return {'score': 0.8, 'is_authentic': True, 'reason': 'Multiple good keywords', 'red_flags': []}
        elif len(found) >= 1:
            return {'score': 0.6, 'is_authentic': True, 'reason': 'Good keyword found', 'red_flags': []}
        else:
            return {'score': 0.2, 'is_authentic': False, 'reason': 'No relevant keywords', 'red_flags': ['No evidence']}

    def _fallback_verification(self, post):
        log("⚠️ Using full fallback (keyword-only).")
        sarcasm_phrases = ['just kidding', 'lol', 'im broke', 'not really', 'joke', 'imagine if']
        if any(p in post.caption.lower() for p in sarcasm_phrases):
            return {
                'is_authentic': False,
                'score': 0.2,
                'details': {'fallback': True, 'reason': 'Sarcasm detected'},
                'status': 'flagged'
            }
        keywords = ['clean', 'plant', 'donate', 'help', 'volunteer',
                   'blood', 'tree', 'food', 'education', 'health', 'recycle']
        found = [kw for kw in keywords if kw in post.caption.lower()]
        if len(found) >= 2:
            return {'is_authentic': True, 'score': 0.8, 'details': {'fallback': True, 'keywords': found}, 'status': 'verified'}
        elif len(found) >= 1:
            return {'is_authentic': True, 'score': 0.6, 'details': {'fallback': True, 'keywords': found}, 'status': 'verified'}
        else:
            return {'is_authentic': False, 'score': 0.2, 'details': {'fallback': True, 'keywords': []}, 'status': 'flagged'}