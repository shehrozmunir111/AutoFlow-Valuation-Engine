import os
import random
import string
import sys
from decimal import Decimal
from pathlib import Path

from sqlalchemy import text


sys.path.append(str(Path(__file__).resolve().parent))

from app.database import Base, engine, get_db_session  # noqa: E402
from app.models.partner import Partner  # noqa: E402
from app.models.pricing import PricingRule  # noqa: E402
from app.models.vehicle import Vehicle  # noqa: E402


NUM_PARTNERS = int(os.getenv("SEED_PARTNERS", "300"))
NUM_VEHICLES = int(os.getenv("SEED_VEHICLES", "1500"))
NUM_PRICING_RULES = int(os.getenv("SEED_PRICING_RULES", "75000"))
CHUNK_SIZE = int(os.getenv("SEED_CHUNK_SIZE", "5000"))

VALID_PARTNER_TYPES = ["junk", "auction", "hybrid"]
VALID_PRICING_STRUCTURES = ["vehicle_specific", "category_based", "flat_rate", "zip_based"]
VEHICLE_CATEGORIES = ["sedan", "suv", "truck", "van"]
MAKES_AND_MODELS = {
    "Toyota": ["Camry", "Corolla", "RAV4", "Tacoma"],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot"],
    "Ford": ["F-150", "Escape", "Explorer", "Fusion"],
    "Chevrolet": ["Malibu", "Silverado", "Equinox", "Tahoe"],
    "Nissan": ["Altima", "Sentra", "Rogue", "Frontier"],
    "Hyundai": ["Elantra", "Sonata", "Tucson", "Santa Fe"],
    "Kia": ["Forte", "Optima", "Sportage", "Sorento"],
}


def generate_random_string(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def generate_zip_code() -> str:
    return f"{random.randint(10000, 99999)}"


def random_decimal(min_value: float, max_value: float, precision: int = 2) -> Decimal:
    return Decimal(str(round(random.uniform(min_value, max_value), precision)))


def build_partners() -> list[Partner]:
    partners: list[Partner] = []
    for _ in range(NUM_PARTNERS):
        pricing_structure_type = random.choice(VALID_PRICING_STRUCTURES)
        partner_type = random.choice(VALID_PARTNER_TYPES)

        partners.append(
            Partner(
                name=f"Partner_{partner_type.upper()}_{generate_random_string()}",
                partner_type=partner_type,
                pricing_structure_type=pricing_structure_type,
                is_active=True,
                priority_score=random.randint(10, 100),
                coverage_zips=[generate_zip_code() for _ in range(random.randint(5, 20))],
                default_spread_percent=random_decimal(5.0, 22.5),
            )
        )
    return partners


def build_vehicles() -> list[Vehicle]:
    vehicles: list[Vehicle] = []
    for _ in range(NUM_VEHICLES):
        make = random.choice(list(MAKES_AND_MODELS.keys()))
        model = random.choice(MAKES_AND_MODELS[make])
        vehicles.append(
            Vehicle(
                year=random.randint(2000, 2025),
                make=make,
                model=model,
                trim=random.choice(["Base", "SE", "Sport", "Limited", "LX", "EX"]),
                body_type=random.choice(VEHICLE_CATEGORIES),
                weight_kg=random_decimal(1100, 3200, 0),
            )
        )
    return vehicles


def build_rule_mapping(partner_id: int, vehicle_ids: list[int]) -> dict:
    structure = random.choice(VALID_PRICING_STRUCTURES)
    base_price = random_decimal(250, 6500)
    zip_code = generate_zip_code()

    rule = {
        "partner_id": partner_id,
        "is_active": True,
        "buyer_spread_percent": random_decimal(5.0, 20.0),
    }

    if structure == "vehicle_specific":
        rule.update(
            {
                "rule_type": "vehicle_specific",
                "vehicle_id": random.choice(vehicle_ids),
                "specific_price": base_price,
                "base_price": base_price,
            }
        )
    elif structure == "category_based":
        rule.update(
            {
                "rule_type": "category",
                "vehicle_category": random.choice(VEHICLE_CATEGORIES),
                "category_price": base_price,
                "base_price": base_price,
            }
        )
    elif structure == "zip_based":
        rule.update(
            {
                "rule_type": "condition_adjustment",
                "zip_code": zip_code,
                "zip_prefix": zip_code[:3],
                "price_per_ton": random_decimal(60, 220),
                "base_price": base_price,
            }
        )
    else:
        rule.update(
            {
                "rule_type": "flat",
                "base_price": base_price,
            }
        )

    return rule


def main() -> None:
    print("Preparing PostgreSQL schema...")
    Base.metadata.create_all(bind=engine)

    with get_db_session() as db:
        print("Resetting existing partner, vehicle, pricing, quote, and photo data...")
        db.execute(text("TRUNCATE TABLE quote_photos, quotes, pricing_rules, partners, vehicles RESTART IDENTITY CASCADE"))
        db.commit()

        print(f"Creating {NUM_PARTNERS} partners...")
        partners = build_partners()
        db.bulk_save_objects(partners)
        db.commit()
        partner_ids = list(db.scalars(text("SELECT id FROM partners")).all())

        print(f"Creating {NUM_VEHICLES} vehicles...")
        vehicles = build_vehicles()
        db.bulk_save_objects(vehicles)
        db.commit()
        vehicle_ids = list(db.scalars(text("SELECT id FROM vehicles")).all())

        print(f"Creating {NUM_PRICING_RULES} pricing rules in chunks...")
        chunk: list[dict] = []
        for i in range(1, NUM_PRICING_RULES + 1):
            chunk.append(build_rule_mapping(random.choice(partner_ids), vehicle_ids))

            if i % CHUNK_SIZE == 0:
                db.bulk_insert_mappings(PricingRule, chunk)
                db.commit()
                chunk.clear()
                sys.stdout.write(f"\rInserted {i} / {NUM_PRICING_RULES} pricing rules")
                sys.stdout.flush()

        if chunk:
            db.bulk_insert_mappings(PricingRule, chunk)
            db.commit()

        print("\nPostgreSQL bulk seeding complete.")
        print(f"Partners: {NUM_PARTNERS}")
        print(f"Vehicles: {NUM_VEHICLES}")
        print(f"Pricing rules: {NUM_PRICING_RULES}")


if __name__ == "__main__":
    main()
