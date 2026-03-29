import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')
django.setup()

from vols.services import agoda_service

print('--- Testing Destinations ---')
dests = agoda_service.search_destinations('دبي')
print(f'Found {len(dests)} destinations.')
if dests:
    print(dests[0])

print('\n--- Testing Hotels Search ---')
hotels = agoda_service.search_hotels(1001, '2026-04-01', '2026-04-05', 2, 1)
print(f'Found {len(hotels)} hotels with mock/real data.')
if hotels:
    print(f"Hotel 1: {hotels[0]['hotelName']} | Price: {hotels[0]['pricing']}")
