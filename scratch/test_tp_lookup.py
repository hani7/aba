import requests

def test_lookup(query):
    url = 'https://suggest.travelpayouts.com/v2/places.json'
    params = {
        'term': query,
        'locale': 'ar',
        'types[]': 'city'
    }
    try:
        resp = requests.get(url, params=params)
        print(f"Status: {resp.status_code}")
        print(f"Results: {resp.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_lookup("Paris")
    print("\n--- Algiers ---")
    test_lookup("الجزائر")
