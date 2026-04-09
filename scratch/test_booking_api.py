import os
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY')
RAPIDAPI_HOST = 'booking-com15.p.rapidapi.com'

def test_search(query):
    url = f"https://{RAPIDAPI_HOST}/api/v1/hotels/searchDestination"
    querystring = {"query": query}
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if not RAPIDAPI_KEY:
        print("No RAPIDAPI_KEY found in .env")
    else:
        print(f"Testing with key: {RAPIDAPI_KEY[:5]}...")
        test_search("Paris")
