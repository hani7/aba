import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')
django.setup()

from vols.services import duffel_service
import json

def test_route(origin, destination, date):
    print(f"Testing {origin} -> {destination} on {date}...")
    slices = [{'origin': origin, 'destination': destination, 'departure_date': date}]
    try:
        offers = duffel_service.search_flights(slices, passengers=1, cabin_class='economy')
        found_airlines = set()
        for o in offers:
            for sl in o.get('slices', []):
                for seg in sl.get('segments', []):
                    carrier = seg.get('operating_carrier', {}).get('iata_code') or seg.get('marketing_carrier', {}).get('iata_code')
                    found_airlines.add(carrier)
        
        print(f"Found airlines: {found_airlines}")
        if 'J4' in found_airlines:
            print("!!! BADR AIRLINES (J4) FOUND on this route !!!")
        else:
            print("No Badr Airlines (J4) found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    # Try a few dates in the near future
    test_route('CAI', 'PZU', '2026-05-15')
    test_route('DXB', 'PZU', '2026-05-15')
    test_route('JED', 'PZU', '2026-05-15')
    test_route('CAI', 'KRT', '2026-05-15')
