from groq import Groq
import base64
import logging
import json
from typing import Optional
from decimal import Decimal

from app.config import settings

logger = logging.getLogger(__name__)

class VisionAudit:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
    
    async def perform_photo_audit(self, photo_id: int, image_data: bytes) -> dict:
        """Analyze vehicle photo using Groq Vision."""
        try:
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Using Groq's vision model
            response = self.client.chat.completions.create(
                model=settings.GROQ_VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this vehicle photo. Identify damage: dents, scratches, rust, cracks. Return ONLY a JSON object with: { \"damage_detected\": boolean, \"damage_description\": string, \"severity_rating\": 1-5, \"estimated_repair_cost\": number }"},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return {
                "damage_detected": result.get("damage_detected", False),
                "damage_description": result.get("damage_description", ""),
                "confidence_score": Decimal("0.85"),
                "severity_rating": result.get("severity_rating"),
                "estimated_repair_cost": Decimal(str(result.get("estimated_repair_cost", 0)))
            }
            
        except Exception as e:
            logger.error(f"Groq Vision audit failed: {e}")
            return {
                "damage_detected": False,
                "damage_description": "Analysis failed",
                "confidence_score": Decimal("0.0"),
                "severity_rating": None,
                "estimated_repair_cost": None
            }