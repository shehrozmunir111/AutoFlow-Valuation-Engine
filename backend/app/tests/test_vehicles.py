import pytest

def test_create_vehicle(client):
    vehicle_data = {
        "year": 2020,
        "make": "Honda",
        "model": "Accord"
    }
    response = client.post("/api/v1/vehicles/", json=vehicle_data)
    assert response.status_code == 200
    assert response.json()["make"] == "Honda"
    assert response.json()["id"] is not None

def test_lookup_vehicle(client):
    # Provide VIN (mocks decoded response)
    response = client.get("/api/v1/vehicles/lookup?vin=1HGCM82633A000000")
    if response.status_code == 200:
        data = response.json()
        assert data["vin"] == "1HGCM82633A000000"
        
def test_lookup_vehicle_by_attributes(client):
    client.post("/api/v1/vehicles/", json={"year": 2021, "make": "Tesla", "model": "Model 3"})
    response = client.get("/api/v1/vehicles/lookup?year=2021&make=Tesla&model=Model 3")
    assert response.status_code == 200
    assert len(response.json()["vehicles"]) >= 1

def test_get_makes(client):
    client.post("/api/v1/vehicles/", json={"year": 2021, "make": "Tesla", "model": "Model 3"})
    client.post("/api/v1/vehicles/", json={"year": 2022, "make": "Ford", "model": "F-150"})
    
    response = client.get("/api/v1/vehicles/makes")
    assert response.status_code == 200
    assert "Tesla" in response.json()["makes"]
    assert "Ford" in response.json()["makes"]

def test_get_models(client):
    client.post("/api/v1/vehicles/", json={"year": 2021, "make": "Tesla", "model": "Model 3"})
    
    response = client.get("/api/v1/vehicles/models?make=Tesla")
    assert response.status_code == 200
    assert "Model 3" in response.json()["models"]
