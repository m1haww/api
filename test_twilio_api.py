import requests
import json

# Test the Twilio-integrated API
def test_analyze_and_call():
    url = "http://localhost:8080/analyze-and-call"
    
    # Test data
    test_cases = [
        {
            "message": "I absolutely love this new feature! It's amazing!",
            "to_number": "+1234567890",  # Replace with your phone number
            "from_number": "+0987654321"  # Optional, will use TWILIO_PHONE_NUMBER if not provided
        },
        {
            "message": "This is terrible and I hate it.",
            "to_number": "+1234567890",  # Replace with your phone number
        }
    ]
    
    headers = {"Content-Type": "application/json"}
    
    for i, test_data in enumerate(test_cases):
        print(f"\n=== Test Case {i+1} ===")
        print(f"Message: {test_data['message']}")
        
        try:
            response = requests.post(url, json=test_data, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"Error: {e}")

# Test original sentiment endpoint
def test_sentiment_only():
    print("\n=== Testing Original Sentiment Endpoint ===")
    
    messages = [
        "I love this API",
        "This is terrible"
    ]
    
    for message in messages:
        try:
            response = requests.get(f"http://localhost:8080/?q={message}")
            print(f"\nMessage: {message}")
            print(f"Response: {response.json()}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing Sentiment Analysis API with Twilio Integration")
    print("Make sure the API is running on http://localhost:8080")
    print("\nNote: For the Twilio call to work, you need to set these environment variables:")
    print("- TWILIO_ACCOUNT_SID")
    print("- TWILIO_AUTH_TOKEN")
    print("- TWILIO_PHONE_NUMBER (optional if provided in request)")
    
    test_sentiment_only()
    test_analyze_and_call()