from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleResponse

router = APIRouter()

from app.services.auto_spec_fetcher import AutoSpecFetcher

@router.get("/lookup")
async def lookup_vehicle(
    vin: Optional[str] = Query(None, min_length=17, max_length=17),
    year: Optional[int] = None,
    make: Optional[str] = None,
    model: Optional[str] = None,
    db: Session = Depends(get_db)
):
    if vin:
        fetcher = AutoSpecFetcher()
        data = await fetcher.fetch_specs_by_vin(vin)
        if data:
            return {
                "source": "vin_decoder",
                "vin": vin,
                **data
            }
        raise HTTPException(status_code=404, detail="VIN not found")
    
    if year and make and model:
        vehicles = db.query(Vehicle).filter(
            Vehicle.year == year,
            Vehicle.make.ilike(f"%{make}%"),
            Vehicle.model.ilike(f"%{model}%")
        ).all()
        return {"vehicles": [VehicleResponse.model_validate(v) for v in vehicles]}
    
    raise HTTPException(status_code=400, detail="Provide VIN or year/make/model")

@router.get("/makes")
async def get_makes(db: Session = Depends(get_db)):
    makes = db.query(Vehicle.make).distinct().all()
    return {"makes": sorted([m[0] for m in makes if m[0]])}

@router.get("/models")
async def get_models(make: str, year: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Vehicle.model).filter(Vehicle.make.ilike(f"%{make}%")).distinct()
    if year:
        query = query.filter(Vehicle.year == year)
    models = query.all()
    return {"models": sorted([m[0] for m in models if m[0]])}

@router.post("/", response_model=VehicleResponse)
async def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    db_vehicle = Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle