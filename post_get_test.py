import requests
import json

# 修改為您的 API 服務 URL，例如 Cloud Run 的 URL
# BASE_URL = 'http://localhost:5000' 
BASE_URL = "https://dividend-app-148949302162.asia-east1.run.app"
BASE_URL = "https://dividend-app-148949302162.asia-east1.run.app"

def test_post_data():
    url = f"{BASE_URL}/data"
    payload = {
        "stock_symbol": "AAPL",
        "dividend": 0.82,
        "price": 150.25,
        "date": "2025-02-07"
    }
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("POST Response:", response.status_code)
        print("Response Data:", response.json())
    except requests.exceptions.RequestException as e:
        print("POST request failed:", e)

def test_get_data():
    url = f"{BASE_URL}/data"
    try:
        response = requests.get(url)
        response.raise_for_status()
        print("GET Response:", response.status_code)
        print("Response Data:", response.json())
    except requests.exceptions.RequestException as e:
        print("GET request failed:", e)

if __name__ == '__main__':
    print("Testing POST endpoint:")
    test_post_data()
    print("\nTesting GET endpoint:")
    test_get_data()
