import httpx
import logging
from typing import Dict, Optional

from app.config import settings

logger = logging.getLogger(__name__)

class AutoSpecFetcher:
    def __init__(self):
        self.api_key = settings.VIN_DECODER_API_KEY
        self.base_url = settings.VIN_DECODER_URL
    
    async def fetch_specs_by_vin(self, vin: str) -> Optional[Dict]:
        """Decode VIN using external API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/decode",
                    params={"vin": vin, "apikey": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "year": data.get("year"),
                        "make": data.get("make"),
                        "model": data.get("model"),
                        "trim": data.get("trim"),
                        "body_type": data.get("body_type")
                    }
                return None
                
        except Exception as e:
            logger.error(f"VIN decode error: {e}")
            return None
    
    def validate_vin(self, vin: str) -> bool:
        """Basic VIN validation."""
        if len(vin) != 17:
            return False
        invalid_chars = ['I', 'O', 'Q']
        return not any(c in vin.upper() for c in invalid_chars)