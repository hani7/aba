import requests

def test_lookup(query):
    url = 'http://engine.hotellook.com/api/v2/lookup.json'
    params = {
        'query': query,
        'lang': 'ar',
        'limit': 5
    }
    try:
        resp = requests.get(url, params=params)
        print(f"Status: {resp.status_code}")
        print(f"Results: {resp.json().get('results', {}).get('locations', [])}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_lookup("Paris")
    print("\n--- Algiers ---")
    test_lookup("الجزائر")
