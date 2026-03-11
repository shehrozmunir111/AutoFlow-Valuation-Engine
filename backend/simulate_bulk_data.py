import os
import sys
import random
from typing import List, Dict
import string
import decimal

# Make sure the app module can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, get_db_session
from app.models.partner import Partner
from app.models.vehicle import Vehicle
from app.models.pricing import PricingRule
from app.database import Base

# Configuration for data generation
NUM_PARTNERS = 50
NUM_VEHICLES = 1000
NUM_PRICING_RULES = 500_000  # Adjust this if it takes too long (500k should be fast with bulk insert)
CHUNK_SIZE = 10000

def generate_random_string(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_zip_code():
    return f"{random.randint(10000, 99999)}"

def main():
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    with get_db_session() as db:
        print("Checking if data already exists...")
        if db.query(Partner).count() > 0:
            print("Data already exists in DB. Truncating data to regenerate or exiting? Auto-exit to prevent data loss.")
            print("If you want fresh data, delete your SQLite DB or drop tables in PostgreSQL, then run this again.")
            return

        print(f"Generating {NUM_PARTNERS} Partners...")
        partners = []
        for i in range(NUM_PARTNERS):
            p = Partner(
                name=f"Partner_Corp_{generate_random_string(6)}",
                partner_type=random.choice(["auto", "hybrid", "manual"]),
                pricing_structure_type=random.choice(["vehicle_specific", "category_based", "flat_rate", "zip_based"]),
                is_active=True,
                priority_score=random.randint(0, 100),
                coverage_zips=[generate_zip_code() for _ in range(5)], # Sample zip codes coverage
                default_spread_percent=decimal.Decimal(str(round(random.uniform(5.0, 25.0), 2)))
            )
            partners.append(p)
            
        db.bulk_save_objects(partners)
        db.commit()
        
        # Retrieve partner IDs
        partner_ids = [p.id for p in db.query(Partner.id).all()]
        
        print(f"Generating {NUM_VEHICLES} Vehicles...")
        vehicles = []
        makes = ["Toyota", "Ford", "Honda", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz"]
        for i in range(NUM_VEHICLES):
            v = Vehicle(
                year=random.randint(1995, 2024),
                make=random.choice(makes),
                model=f"Model_{generate_random_string(4)}",
                weight_kg=decimal.Decimal(str(random.randint(1000, 3000)))
            )
            vehicles.append(v)
            
        db.bulk_save_objects(vehicles)
        db.commit()
        
        # Retrieve vehicle IDs
        vehicle_ids = [v.id for v in db.query(Vehicle.id).all()]
        
        print(f"Generating {NUM_PRICING_RULES} Pricing Rules (bulk insert)...")
        # We use dicts here because `bulk_insert_mappings` is WAY faster than object creation
        pricing_rules_chunk = []
        rule_types = ["flat", "vehicle_specific", "category_based", "zip_based"]
        
        for i in range(1, NUM_PRICING_RULES + 1):
            rule_type = random.choice(rule_types)
            base_price = decimal.Decimal(str(round(random.uniform(100, 5000), 2)))
            zip_code = generate_zip_code()
            
            rule_dict = {
                "partner_id": random.choice(partner_ids),
                "rule_type": rule_type,
                "is_active": True,
                "base_price": base_price,
            }
            
            if rule_type == "vehicle_specific":
                rule_dict["vehicle_id"] = random.choice(vehicle_ids)
                rule_dict["specific_price"] = base_price * decimal.Decimal("1.2")
            elif rule_type == "zip_based":
                rule_dict["zip_code"] = zip_code
                rule_dict["zip_prefix"] = zip_code[:3]
                rule_dict["price_per_ton"] = decimal.Decimal(str(round(random.uniform(50, 200), 2)))
            elif rule_type == "category_based":
                rule_dict["vehicle_category"] = random.choice(["sedan", "suv", "truck", "van"])
                rule_dict["category_price"] = base_price
                
            pricing_rules_chunk.append(rule_dict)
            
            if i % CHUNK_SIZE == 0:
                db.bulk_insert_mappings(PricingRule, pricing_rules_chunk)
                db.commit()
                pricing_rules_chunk.clear()
                sys.stdout.write(f"\rInserted {i} / {NUM_PRICING_RULES} rules...")
                sys.stdout.flush()
                
        # Insert remaining
        if pricing_rules_chunk:
            db.bulk_insert_mappings(PricingRule, pricing_rules_chunk)
            db.commit()
            
        print("\nFinished generating all bulk data! You can now test the pricing engine performance.")

if __name__ == "__main__":
    main()
