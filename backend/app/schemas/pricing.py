from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal
from datetime import date

class PricingRuleBase(BaseModel):
    rule_type: str = Field(..., pattern="^(flat|category|vehicle_specific|condition_adjustment)$")
    vehicle_category: Optional[str] = None
    zip_code: Optional[str] = None
    zip_prefix: Optional[str] = None
    base_price: Optional[Decimal] = None
    category_price: Optional[Decimal] = None
    specific_price: Optional[Decimal] = None
    price_per_ton: Optional[Decimal] = None
    condition_min: Optional[str] = None
    condition_max: Optional[str] = None
    adjustment_percent: Optional[Decimal] = None
    buyer_spread_percent: Optional[Decimal] = None
    is_active: bool = True

class PricingRuleCreate(PricingRuleBase):
    partner_id: int
    vehicle_id: Optional[int] = None

class PricingRuleResponse(PricingRuleBase):
    id: int
    partner_id: int
    vehicle_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
