import pytest
from decimal import Decimal
from sqlalchemy.orm import Session

from app.services.valuation_logic import ValuationLogic
from app.models.partner import Partner
from app.models.pricing import PricingRule
from app.models.vehicle import Vehicle
from app.schemas.quote import QuoteRequest

def test_valuation_logic_flat_rate(db: Session):
    partner = Partner(
        name="Test Junk Yard",
        partner_type="junk",
        pricing_structure_type="flat_rate",
        default_spread_percent=Decimal("15.0")
    )
    db.add(partner)
    db.flush()
    
    rule = PricingRule(
        partner_id=partner.id,
        rule_type="flat",
        base_price=Decimal("500.00"),
        is_active=True
    )
    db.add(rule)
    db.commit()
    
    engine = ValuationLogic(db)
    request = QuoteRequest(
        year=2010,
        make="Honda",
        model="Civic",
        mileage=150000,
        title_status="clean",
        condition_rating="fair",
        drivable=True,
        zip_code="12345"
    )
    
    result = engine.calculate_optimal_price(request)
    assert result['final_offer'] is not None
    assert result['calculation_method'] == "flat_rate"
