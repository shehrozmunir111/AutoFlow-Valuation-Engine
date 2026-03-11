import pytest

def test_create_partner(client):
    partner_data = {
        "name": "Acme Auto",
        "partner_type": "junk",
        "pricing_structure_type": "vehicle_specific"
    }
    response = client.post("/api/v1/partners/", json=partner_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Acme Auto"
    assert data["partner_type"] == "junk"

def test_list_partners(client):
    # Setup some data
    client.post("/api/v1/partners/", json={"name": "P1", "partner_type": "junk", "pricing_structure_type": "flat_rate"})
    client.post("/api/v1/partners/", json={"name": "P2", "partner_type": "hybrid", "pricing_structure_type": "zip_based"})
    
    response = client.get("/api/v1/partners/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

def test_add_pricing_rule(client):
    # First create a partner
    partner_resp = client.post("/api/v1/partners/", json={"name": "Acme Auto", "partner_type": "junk", "pricing_structure_type": "flat_rate"})
    p_id = partner_resp.json()["id"]
    
    rule_data = {
        "rule_type": "flat",
        "base_price": 500.0,
        "is_active": True,
        "partner_id": p_id
    }
    
    response = client.post(f"/api/v1/partners/{p_id}/pricing", json=rule_data)
    assert response.status_code == 200
    assert float(response.json()["base_price"]) == 500.0

def test_get_partner_pricing(client):
    # First create a partner and rule
    partner_resp = client.post("/api/v1/partners/", json={"name": "Acme Auto", "partner_type": "junk", "pricing_structure_type": "flat_rate"})
    p_id = partner_resp.json()["id"]
    
    client.post(f"/api/v1/partners/{p_id}/pricing", json={"rule_type": "flat", "base_price": 500.0, "is_active": True, "partner_id": p_id})
    
    response = client.get(f"/api/v1/partners/{p_id}/pricing")
    assert response.status_code == 200
    assert len(response.json()) >= 1
