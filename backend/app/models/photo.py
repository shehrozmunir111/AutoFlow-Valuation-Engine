from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Numeric, JSON
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import TimestampMixin

class QuotePhoto(Base, TimestampMixin):
    __tablename__ = "quote_photos"
    
    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    photo_type = Column(String(50), nullable=False)
    
    s3_url = Column(String(500))
    s3_key = Column(String(500))
    
    ai_vision_analysis = Column(JSON)
    damage_detected = Column(Boolean)
    damage_description = Column(String(1000))
    confidence_score = Column(Numeric(3, 2))
    
    quote = relationship("Quote", back_populates="photos")