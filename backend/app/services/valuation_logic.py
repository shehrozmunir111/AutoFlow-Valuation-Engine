from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import or_
import time
import logging
from datetime import datetime

from app.models.partner import Partner
from app.models.pricing import PricingRule
from app.models.vehicle import Vehicle
from app.schemas.quote import QuoteRequest

logger = logging.getLogger(__name__)

class ValuationLogic:
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_optimal_price(self, request: QuoteRequest) -> Dict[str, Any]:
        start_time = time.time()
        
        # 1. Get eligible partners
        partners = self._get_eligible_partners(request.zip_code, request.classification_hint)
        
        if not partners:
            return self._fallback_pricing(request)
        
        # 2. Get or create vehicle
        vehicle = self._get_or_create_vehicle(request.year, request.make, request.model)
        
        # 3. Find best price
        best_offer = None
        
        for partner in partners:
            price = self._calculate_partner_price(partner, vehicle, request)
            if price and (not best_offer or price['final_offer'] > best_offer['final_offer']):
                best_offer = price
        
        elapsed_ms = (time.time() - start_time) * 1000
        
        return {
            'partner_id': best_offer['partner_id'] if best_offer else None,
            'partner_price': best_offer['base_price'] if best_offer else None,
            'spread_amount': best_offer['spread'] if best_offer else None,
            'final_offer': best_offer['final_offer'] if best_offer else Decimal('500'),
            'calculation_method': best_offer['method'] if best_offer else 'fallback',
            'query_time_ms': elapsed_ms
        }
    
    def _get_eligible_partners(self, zip_code: str, classification_hint: Optional[str]) -> List[Partner]:
        query = self.db.query(Partner).filter(Partner.is_active == True)
        
        from sqlalchemy import cast, String
        
        # Geographic filter
        query = query.filter(
            or_(
                Partner.coverage_zips.is_(None),
                cast(Partner.coverage_zips, String).ilike(f'%"{zip_code}"%'),
                cast(Partner.coverage_zips, String).ilike(f'%"{zip_code[:3]}"%')
            )
        )
        
        # Classification filter
        if classification_hint:
            query = query.filter(
                or_(
                    Partner.partner_type == classification_hint,
                    Partner.partner_type == 'hybrid'
                )
            )
        
        return query.order_by(Partner.priority_score.desc()).limit(50).all()
    
    def _get_or_create_vehicle(self, year: int, make: str, model: str) -> Vehicle:
        vehicle = self.db.query(Vehicle).filter(
            Vehicle.year == year,
            Vehicle.make.ilike(make),
            Vehicle.model.ilike(model)
        ).first()
        
        if not vehicle:
            vehicle = Vehicle(year=year, make=make, model=model, weight_kg=Decimal('1500'))
            self.db.add(vehicle)
            self.db.flush()
        
        return vehicle
    
    def _calculate_partner_price(self, partner: Partner, vehicle: Vehicle, request: QuoteRequest) -> Optional[Dict]:
        # Strategy 1: Vehicle-specific
        if partner.pricing_structure_type == 'vehicle_specific':
            rule = self.db.query(PricingRule).filter(
                PricingRule.partner_id == partner.id,
                PricingRule.vehicle_id == vehicle.id,
                PricingRule.is_active == True
            ).first()
            
            if rule and rule.specific_price:
                return self._apply_spread(rule.specific_price, rule, partner, 'vehicle_specific')
        
        # Strategy 2: Category-based
        if partner.pricing_structure_type == 'category_based':
            category = 'sedan'  # Simplified
            rule = self.db.query(PricingRule).filter(
                PricingRule.partner_id == partner.id,
                PricingRule.vehicle_category == category,
                PricingRule.is_active == True
            ).first()
            
            if rule and rule.category_price:
                return self._apply_spread(rule.category_price, rule, partner, 'category_based')
        
        # Strategy 3: Flat rate
        if partner.pricing_structure_type == 'flat_rate':
            rule = self.db.query(PricingRule).filter(
                PricingRule.partner_id == partner.id,
                PricingRule.rule_type == 'flat',
                PricingRule.is_active == True
            ).first()
            
            if rule:
                return self._apply_spread(rule.base_price, rule, partner, 'flat_rate')
        
        # Strategy 4: Weight-based
        if partner.pricing_structure_type == 'zip_based':
            rule = self.db.query(PricingRule).filter(
                PricingRule.partner_id == partner.id,
                or_(PricingRule.zip_code == request.zip_code, PricingRule.zip_prefix == request.zip_code[:3]),
                PricingRule.is_active == True
            ).first()
            
            if rule and rule.price_per_ton and vehicle.weight_kg:
                weight_tons = float(vehicle.weight_kg) / 1000
                price = Decimal(str(weight_tons)) * rule.price_per_ton
                return self._apply_spread(price, rule, partner, 'weight_based')
        
        return None
    
    def _apply_spread(self, base_price: Decimal, rule: PricingRule, partner: Partner, method: str) -> Dict:
        spread_pct = rule.buyer_spread_percent or partner.default_spread_percent or Decimal('15.0')
        spread_amount = base_price * (spread_pct / 100)
        final_offer = base_price - spread_amount
        
        return {
            'partner_id': partner.id,
            'base_price': base_price,
            'spread': spread_amount,
            'final_offer': final_offer,
            'method': method
        }
    
    def _fallback_pricing(self, request: QuoteRequest) -> Dict[str, Any]:
        age = datetime.now().year - request.year
        base_value = max(500, 5000 - (age * 300))
        
        return {
            'partner_id': None,
            'partner_price': None,
            'spread_amount': None,
            'final_offer': Decimal(str(base_value)),
            'calculation_method': 'fallback_estimate',
            'query_time_ms': 0
        }
