from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean, Text, DateTime, JSON, Uuid
from sqlalchemy.orm import relationship
import uuid

from app.database import Base
from app.models.base import TimestampMixin

class Quote(Base, TimestampMixin):
    __tablename__ = "quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Uuid(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    vin = Column(String(17), index=True)
    year = Column(Integer)
    make = Column(String(100))
    model = Column(String(100))
    trim = Column(String(100))
    mileage = Column(Integer)
    title_status = Column(String(50))
    
    condition_rating = Column(String(20))
    drivable = Column(Boolean)
    engine_issues = Column(Text)
    transmission_issues = Column(Text)
    condition_map_ext = Column(JSON)
    condition_map_int = Column(JSON)
    
    zip_code = Column(String(10), index=True)
    city = Column(String(100))
    state = Column(String(50))
    
    classification = Column(String(20))
    classification_confidence = Column(Numeric(3, 2))
    
    partner_id = Column(Integer, ForeignKey("partners.id"))
    partner_price = Column(Numeric(10, 2))
    spread_amount = Column(Numeric(10, 2))
    final_offer = Column(Numeric(10, 2))
    
    status = Column(String(20), default='pending')
    ai_classified = Column(Boolean, default=False)
    needs_human_review = Column(Boolean, default=False)
    
    zoho_crm_id = Column(String(100))
    zoho_sync_status = Column(String(20), default='pending')
    
    accepted_at = Column(DateTime)
    offer_valid_until = Column(DateTime)
    
    vehicle_ref = relationship("Vehicle", back_populates="quotes")
    partner_ref = relationship("Partner", back_populates="quotes")
    photos = relationship("QuotePhoto", back_populates="quote")