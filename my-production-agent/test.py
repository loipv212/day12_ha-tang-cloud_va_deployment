import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8080"
HEADERS = {"Content-Type": "application/json", "X-API-Key": "secret"}

def test_endpoint(path, method="GET", data=None, headers=HEADERS):
    try:
        req = urllib.request.Request(
            f"{BASE_URL}{path}",
            data=json.dumps(data).encode() if data else None,
            headers=headers,
            method=method
        )
        with urllib.request.urlopen(req) as resp:
            print(f"[{method}] {path} -> {resp.status}")
            print(json.loads(resp.read()))
    except urllib.error.HTTPError as e:
        print(f"[{method}] {path} -> Failed with {e.code}: {e.read().decode()}")

print("--- Testing Health ---")
test_endpoint("/health")

print("\n--- Testing Ready ---")
test_endpoint("/ready")

print("\n--- Testing Ask (No Auth) ---")
test_endpoint("/ask", "POST", {"question": "Hi", "user_id": "u1"}, headers={"Content-Type": "application/json"})

print("\n--- Testing Ask (With Auth) ---")
test_endpoint("/ask", "POST", {"question": "Hi", "user_id": "u1"})
