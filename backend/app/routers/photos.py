from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.schemas.photo import PhotoUploadRequest
from app.models.quote import Quote
from app.models.photo import QuotePhoto

router = APIRouter()

from app.services.s3_service import S3Service

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
    
    s3 = S3Service()
    key = f"quotes/{request.quote_id}/{request.photo_type}_{uuid.uuid4()}.jpg"
    upload_url = s3.generate_presigned_url(key)
    
    return {
        "upload_url": upload_url,
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
    
    s3 = S3Service()
    photo = QuotePhoto(
        quote_id=quote.id,
        photo_type=photo_type,
        s3_key=s3_key,
        s3_url=s3.get_object_url(s3_key)
    )
    db.add(photo)
    db.commit()
    
    return {"status": "upload_confirmed", "photo_id": photo.id}