import httpx
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from app.config import settings
from app.models.quote import Quote

logger = logging.getLogger(__name__)

class CRMIntegration:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.token_expires: Optional[datetime] = None
        self.base_url = settings.ZOHO_BASE_URL
    
    async def _get_access_token(self) -> str:
        """Refresh OAuth token."""
        if self.access_token and self.token_expires and datetime.now() < self.token_expires:
            return self.access_token
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://accounts.zoho.com/oauth/v2/token",
                data={
                    "refresh_token": settings.ZOHO_REFRESH_TOKEN,
                    "client_id": settings.ZOHO_CLIENT_ID,
                    "client_secret": settings.ZOHO_CLIENT_SECRET,
                    "grant_type": "refresh_token"
                }
            )
            
            data = response.json()
            self.access_token = data['access_token']
            self.token_expires = datetime.now() + timedelta(seconds=data.get('expires_in', 3600) - 300)
            return self.access_token
    
    async def publish_quote_record(self, quote: Quote) -> Dict:
        """Create Cars module record in Zoho CRM."""
        if settings.MOCK_MODE or settings.ZOHO_MOCK_MODE:
            return {"success": True, "zoho_id": "mock_zoho_id"}

        try:
            token = await self._get_access_token()
            
            record_data = {
                "data": [{
                    "Vehicle_VIN": quote.vin or "",
                    "Year": quote.year,
                    "Make": quote.make,
                    "Model": quote.model,
                    "Mileage": quote.mileage,
                    "Title_Status": quote.title_status or "",
                    "Condition_Rating": quote.condition_rating or "",
                    "Classification": quote.classification or "",
                    "Final_Offer": float(quote.final_offer) if quote.final_offer else 0,
                    "Quote_ID": str(quote.quote_id)
                }]
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/{settings.ZOHO_CARS_MODULE}",
                    headers={"Authorization": f"Zoho-oauthtoken {token}"},
                    json=record_data,
                    timeout=30.0
                )
                
                if response.status_code == 201:
                    zoho_id = response.json()['data'][0]['details']['id']
                    return {"success": True, "zoho_id": zoho_id}
                else:
                    return {"success": False, "error": response.text}
                    
        except Exception as e:
            logger.error(f"Zoho CRM error: {e}")
            return {"success": False, "error": str(e)}