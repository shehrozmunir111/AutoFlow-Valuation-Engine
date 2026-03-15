from groq import Groq
import json
import logging
from typing import Dict
from decimal import Decimal

from app.config import settings
from app.schemas.quote import QuoteRequest

logger = logging.getLogger(__name__)

class SmartAssessor:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    async def assess_vehicle_category(self, request: QuoteRequest) -> Dict:
        # AI for all cases as per user request
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
            # Note: Groq's python client for chat completion is synchronous by default in common versions 
            # or uses different async pattern. For this demo, we'll use the sync client or wrap if needed.
            # Assuming standard Groq client usage:
            response = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'classification': result['classification'],
                'confidence': Decimal(str(result['confidence'])),
                'reasoning': result['reasoning']
            }
            
        except Exception as e:
            logger.error(f"Groq assessment failed: {e}")
            return self._rules_fallback(request)
    
    def _rules_fallback(self, request: QuoteRequest) -> Dict:
        score = 0
        age = 2024 - request.year
        
        if age > 15: score -= 2
        if request.mileage > 200000: score -= 2
        if request.title_status in ['salvage', 'junk']: score -= 3
        if not request.drivable: score -= 3
        
        classification = 'auction' if score >= 0 else 'junk'
        
        return {
            'classification': classification,
            'confidence': Decimal('0.70'),
            'reasoning': f'Rules-based fallback, score: {score}'
        }