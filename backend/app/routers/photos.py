from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.schemas.photo import PhotoUploadRequest
from app.models.quote import Quote
from app.models.photo import QuotePhoto

router = APIRouter()

@router.post("/upload-url")
async def get_upload_url(
    request: PhotoUploadRequest,
    db: Session = Depends(get_db)
):
    try:
        quote_uuid = uuid.UUID(request.quote_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quote_id format")
        
    quote = db.query(Quote).filter(Quote.quote_id == quote_uuid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    # Mock presigned URL
    key = f"quotes/{request.quote_id}/{request.photo_type}_{uuid.uuid4()}.jpg"
    
    return {
        "upload_url": f"https://autoflow-photos.s3.amazonaws.com/{key}?X-Amz-Algorithm=...",
        "key": key,
        "expires_in": 3600
    }

@router.post("/confirm-upload")
async def confirm_upload(
    quote_id: str,
    photo_type: str,
    s3_key: str,
    db: Session = Depends(get_db)
):
    try:
        quote_uuid = uuid.UUID(quote_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid quote_id format")
        
    quote = db.query(Quote).filter(Quote.quote_id == quote_uuid).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found")
    
    photo = QuotePhoto(
        quote_id=quote.id,
        photo_type=photo_type,
        s3_key=s3_key,
        s3_url=f"https://autoflow-photos.s3.amazonaws.com/{s3_key}"
    )
    db.add(photo)
    db.commit()
    
    return {"status": "upload_confirmed", "photo_id": photo.id}