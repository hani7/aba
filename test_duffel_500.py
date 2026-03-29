import os
import django
import sys
import json

# Setup django environment
sys.path.append('c:/Users/PC/Desktop/test')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abo.settings')
django.setup()

from vols.services import duffel_service

def test():
    print("Searching for flights...")
    slices = [{
        'origin': 'LHR',
        'destination': 'CDG',
        'departure_date': '2026-06-15'
    }]
    try:
        offers = duffel_service.search_flights(slices, passengers=1, cabin_class='economy')
        if not offers:
            print("No offers found.")
            return

        offer = offers[0]
        offer_id = offer['id']
        amount = offer['total_amount']
        currency = offer['total_currency']
        passenger_id = offer['passengers'][0]['id']

        print(f"Got offer: {offer_id} for {amount} {currency}")

        passengers_data = [{
            'id': passenger_id,
            'title': 'mr',
            'given_name': 'Test',
            'family_name': 'Testerson',
            'born_on': '1990-01-01',
            'gender': 'm',
            'email': 'test@example.com',
            'phone_number': '+442083661100'
        }]

        print("Attempting to create order...")
        order = duffel_service.create_order(offer_id, passengers_data, amount, currency)
        print("Success!", order.get('id'))
        
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == '__main__':
    test()
