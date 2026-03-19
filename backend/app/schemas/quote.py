from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from uuid import UUID

class DamageSelection(BaseModel):
    zone_id: str
    damage_type: str
    severity: int = Field(..., ge=1, le=5)

class QuoteRequest(BaseModel):
    vin: Optional[str] = None
    year: int = Field(..., ge=1900, le=2030)
    make: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    mileage: int = Field(..., ge=0)
    title_status: Optional[str] = Field(None, pattern="^(clean|salvage|rebuilt|junk|lien)$")
    condition_rating: str = Field(..., pattern="^(excellent|good|fair|poor|junk)$")
    drivable: bool
    engine_issues: Optional[str] = None
    transmission_issues: Optional[str] = None
    exterior_damage: Optional[List[DamageSelection]] = None
    interior_damage: Optional[List[DamageSelection]] = None
    glass_damage: Optional[List[DamageSelection]] = None
    wheel_damage: Optional[List[DamageSelection]] = None
    zip_code: str = Field(..., min_length=5, max_length=10)
    city: Optional[str] = None
    state: Optional[str] = None
    pickup_address: Optional[str] = None
    classification_hint: Optional[str] = None

class QuoteResponse(BaseModel):
    quote_id: UUID
    classification: str
    confidence: Decimal
    offer_amount: Optional[Decimal]
    offer_valid_until: datetime
    partner_id: Optional[int] = None
    calculation_method: str
    query_time_ms: float
    needs_human_review: bool = False