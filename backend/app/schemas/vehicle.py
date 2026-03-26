from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

class VehicleBase(BaseModel):
    year: int = Field(..., ge=1900, le=2030)
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    trim: Optional[str] = None
    body_type: Optional[str] = None
    weight_kg: Optional[Decimal] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleResponse(VehicleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
