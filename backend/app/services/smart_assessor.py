from groq import Groq
import json
import logging
from typing import Dict
from decimal import Decimal
from datetime import datetime

from app.config import settings
from app.schemas.quote import QuoteRequest

logger = logging.getLogger(__name__)

class SmartAssessor:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None
    
    async def assess_vehicle_category(self, request: QuoteRequest) -> Dict:
        rules_result = self._rules_fallback(request)

        if settings.MOCK_MODE or not self.client:
            return rules_result

        # Prefer deterministic rules when integrations are unavailable, but
        # enrich classification with Groq when the API is configured.
        prompt = f"""
        Vehicle: {request.year} {request.make} {request.model}
        Miles: {request.mileage}, Condition: {request.condition_rating}
        Drivable: {request.drivable}, Title: {request.title_status}
        
        Classify as 'junk' or 'auction'. Return ONLY a JSON object with:
        {{
            "classification": "junk" | "auction",
            "confidence": 0.0 to 1.0,
            "reasoning": "brief explanation"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'classification': result.get('classification', rules_result['classification']),
                'confidence': Decimal(str(result.get('confidence', rules_result['confidence']))),
                'reasoning': result.get('reasoning', 'Groq classification')
            }
            
        except Exception as e:
            logger.error(f"Groq assessment failed: {e}")
            return rules_result
    
    def _rules_fallback(self, request: QuoteRequest) -> Dict:
        score = 0
        age = datetime.now().year - request.year
        
        if age > 15:
            score -= 2
        if request.mileage > 200000:
            score -= 2
        if request.title_status in ['salvage', 'junk']:
            score -= 3
        if not request.drivable:
            score -= 3
        if request.condition_rating in ['poor', 'junk']:
            score -= 2
        
        classification = 'auction' if score >= 0 else 'junk'
        
        return {
            'classification': classification,
            'confidence': Decimal('0.70'),
            'reasoning': f'Rules-based fallback, score: {score}'
        }
