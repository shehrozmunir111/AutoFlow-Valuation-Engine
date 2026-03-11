import pytest
import uuid
from app.models.quote import Quote

def test_get_upload_url(client, db):
    # Need to mock a quote to find in DB
    test_uuid = uuid.uuid4()
    quote = Quote(quote_id=test_uuid, year=2015, make="Ford", model="Fiesta")
    db.add(quote)
    db.commit()
    
    req_data = {
        "quote_id": str(test_uuid),
        "photo_type": "front"
    }
    
    response = client.post("/api/v1/photos/upload-url", json=req_data)
    assert response.status_code == 200
    data = response.json()
    assert "upload_url" in data
    assert "key" in data

def test_confirm_upload(client, db):
    # Need to mock a quote to find in DB
    test_uuid = uuid.uuid4()
    quote = Quote(quote_id=test_uuid, year=2015, make="Ford", model="Fiesta")
    db.add(quote)
    db.commit()
    
    response = client.post(f"/api/v1/photos/confirm-upload?quote_id={test_uuid}&photo_type=front&s3_key=test_key")
    assert response.status_code == 200
    assert response.json()["status"] == "upload_confirmed"
