from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.partner import Partner
from app.models.pricing import PricingRule
from app.schemas.partner import PartnerCreate, PartnerResponse
from app.schemas.pricing import PricingRuleCreate, PricingRuleResponse

router = APIRouter()

@router.get("/", response_model=List[PartnerResponse])
async def list_partners(
    partner_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Partner)
    if partner_type:
        query = query.filter(Partner.partner_type == partner_type)
    if is_active is not None:
        query = query.filter(Partner.is_active == is_active)
    return query.all()

@router.post("/", response_model=PartnerResponse)
async def create_partner(partner: PartnerCreate, db: Session = Depends(get_db)):
    db_partner = Partner(**partner.model_dump())
    db.add(db_partner)
    db.commit()
    db.refresh(db_partner)
    return db_partner

@router.get("/{partner_id}/pricing", response_model=List[PricingRuleResponse])
async def get_partner_pricing(partner_id: int, db: Session = Depends(get_db)):
    rules = db.query(PricingRule).filter(PricingRule.partner_id == partner_id).all()
    return rules

@router.post("/{partner_id}/pricing", response_model=PricingRuleResponse)
async def add_pricing_rule(
    partner_id: int,
    rule: PricingRuleCreate,
    db: Session = Depends(get_db)
):
    partner = db.query(Partner).filter(Partner.id == partner_id).first()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    
    db_rule = PricingRule(**rule.model_dump(), partner_id=partner_id)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule