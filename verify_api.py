import requests
import json

# Local testing
def test_local():
    print("=== Testing Local API ===")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:8080/health")
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    # Test sentiment analysis
    try:
        response = requests.get("http://localhost:8080/?q=I love this API")
        print(f"\nSentiment Analysis (Positive): {response.status_code}")
        print(f"Response: {response.json()}")
        
        response = requests.get("http://localhost:8080/?q=This is terrible")
        print(f"\nSentiment Analysis (Negative): {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Sentiment analysis failed: {e}")

# Test CORS headers
def test_cors():
    print("\n=== Testing CORS Headers ===")
    headers = {
        'Origin': 'https://api-57018476417.europe-west1.run.app'
    }
    
    try:
        response = requests.get("http://localhost:8080/health", headers=headers)
        print(f"CORS Test Status: {response.status_code}")
        print(f"Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'Not set')}")
    except Exception as e:
        print(f"CORS test failed: {e}")

if __name__ == "__main__":
    test_local()
    test_cors()