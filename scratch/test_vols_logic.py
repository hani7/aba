import os
import sys
import django
from django.conf import settings

# Setup Django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')
django.setup()

from vols.services import booking_service

def test():
    if sys.stdout.encoding.lower() != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("Testing search_destinations for 'Paris'...")
    results = booking_service.search_destinations("Paris")
    for r in results:
        print(f"- {r['nameAr']} (ID: {r['cityId']})")

    print("\nTesting search_destinations for 'Algiers'...")
    results = booking_service.search_destinations("Algiers")
    for r in results:
        print(f"- {r['nameAr']} (ID: {r['cityId']})")

    if results:
        city_id = results[0]['cityId']
        print(f"\nTesting search_hotels for city_id: {city_id}...")
        hotels = booking_service.search_hotels(city_id, "2026-05-01", "2026-05-05")
        for h in hotels:
            print(f"- {h['hotelName']} in {h['cityName']} - Price: {h['minPrice']}")

if __name__ == "__main__":
    test()
