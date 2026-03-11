def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_calculate_quote(client):
    request_data = {
        "year": 2019,
        "make": "Toyota",
        "model": "Camry",
        "mileage": 50000,
        "title_status": "clean",
        "condition_rating": "good",
        "drivable": True,
        "zip_code": "12345"
    }
    
    response = client.post("/api/v1/quotes/calculate", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert "quote_id" in data
    assert "offer_amount" in data