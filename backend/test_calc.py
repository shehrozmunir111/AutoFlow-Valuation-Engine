import httpx
import json

def test_api():
    url = "http://localhost:8000/api/v1/quotes/calculate"
    payload = {
        "vin": "1A2B3D4E5F6G7H8IK", # 17 chars
        "year": 2018,
        "make": "Toyota",
        "model": "Camry",
        "mileage": 55000,
        "title_status": "clean",
        "condition_rating": "good",
        "drivable": True,
        "zip_code": "90210",
        "condition_map_ext": [
            {"zone_id": "hood", "damage_type": "Scratch", "severity": 2}
        ],
        "condition_map_int": []
    }
    
    try:
        response = httpx.post(url, json=payload, timeout=30.0)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
