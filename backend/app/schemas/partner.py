from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from decimal import Decimal

class PartnerBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    partner_type: str = Field(..., pattern="^(junk|auction|hybrid)$")
    pricing_structure_type: str = Field(..., pattern="^(flat_rate|category_based|vehicle_specific|zip_based)$")
    api_endpoint: Optional[str] = None
    priority_score: int = Field(default=0, ge=0, le=100)
    is_active: bool = True

class PartnerCreate(PartnerBase):
    api_credentials: Optional[Dict] = None
    coverage_zips: Optional[List[str]] = None
    default_spread_percent: Decimal = Field(default=Decimal("15.0"))

class PartnerResponse(PartnerBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
