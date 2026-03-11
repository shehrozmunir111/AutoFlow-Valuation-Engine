from locust import HttpUser, task, between
import random

class APIUser(HttpUser):
    wait_time = between(0.1, 1) # Wait 0.1s to 1s between requests

    @task
    def test_pricing_endpoint(self):
        # Simulate the payload for best price match
        payload = {
            "year": random.randint(1995, 2024),
            "make": random.choice(["Toyota", "Ford", "Honda", "Chevrolet", "Nissan"]),
            "model": "Camry", # simplified
            "zip_code": str(random.randint(10000, 99999)),
            "classification_hint": random.choice(["auto", "hybrid", "manual", None])
        }
        self.client.post("/api/v1/quotes/calculate", json=payload)

# If running Locust locally without a host defined beforehand
if __name__ == "__main__":
    from locust.main import main
    main()
