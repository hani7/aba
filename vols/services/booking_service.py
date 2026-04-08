"""
Booking.com API Service (via RapidAPI)
Integrates with the unofficial Booking.com API on RapidAPI.
Requires: RAPIDAPI_KEY in settings or .env file
"""

import requests
import json
from django.conf import settings
from datetime import datetime

RAPIDAPI_KEY = getattr(settings, 'RAPIDAPI_KEY', '')
# Typically 'booking-com.p.rapidapi.com'
RAPIDAPI_HOST = getattr(settings, 'RAPIDAPI_HOST', 'booking-com.p.rapidapi.com')

def _headers():
    return {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "useQueryString": "true"
    }

def apply_markup(price: float) -> dict:
    """Apply hotel markup."""
    markup_pct = 10.0 # Adjust markup percentage here
    markup_amount = round(price * markup_pct / 100, 2)
    return {
        'original_price': price,
        'markup_amount': markup_amount,
        'customer_price': round(price + markup_amount, 2)
    }

def search_destinations(query: str) -> list:
    """Search for locations on Booking.com."""
    if not RAPIDAPI_KEY:
        return _mock_destinations(query)

    url = f"https://{RAPIDAPI_HOST}/v1/hotels/locations"
    querystring = {"name": query, "locale": "ar"}

    try:
        response = requests.get(url, headers=_headers(), params=querystring, timeout=10)
        data = response.json()
        results = []
        for loc in data:
            if loc.get('dest_type') == 'city':
                results.append({
                    'cityId': loc.get('dest_id'),
                    'cityName': loc.get('name'),
                    'countryName': loc.get('country'),
                    'nameAr': loc.get('label')
                })
        return results if results else _mock_destinations(query)
    except Exception:
        return _mock_destinations(query)


def search_hotels(city_id: str, check_in: str, check_out: str, adults: int = 2, rooms: int = 1) -> list:
    """Search for hotels in a destination ID."""
    if not RAPIDAPI_KEY:
        return _mock_hotels(city_id, check_in, check_out, adults)

    url = f"https://{RAPIDAPI_HOST}/v1/hotels/search"
    querystring = {
        "dest_id": city_id,
        "search_type": "city",
        "arrival_date": check_in,
        "departure_date": check_out,
        "adults_number": adults,
        "room_number": rooms,
        "locale": "ar",
        "currency": "USD"
    }

    try:
        response = requests.get(url, headers=_headers(), params=querystring, timeout=15)
        data = response.json()
        results = []
        
        for h in data.get('result', [])[:50]:
            price = float(h.get('min_total_price', 0))
            if price == 0: continue
            
            results.append({
                'hotelId': h.get('hotel_id'),
                'hotelName': h.get('hotel_name'),
                'cityId': city_id,
                'cityName': h.get('city'),
                'starRating': h.get('class', 3),
                'reviewScore': h.get('review_score', 8),
                'reviewCount': h.get('review_nr', 100),
                'minPrice': price,
                'pricing': apply_markup(price),
                'currency': h.get('currencycode', 'USD'),
                'imageUrl': h.get('max_photo_url', 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&h=300&fit=crop'),
                'address': h.get('address', ''),
                'amenities': ['واي فاي مجاني'] # Summarized
            })
        return results if results else _mock_hotels(city_id, check_in, check_out, adults)
    except Exception:
        return _mock_hotels(city_id, check_in, check_out, adults)


def get_hotel(hotel_id: str, check_in: str, check_out: str, adults: int = 2, rooms: int = 1) -> dict:
    """Get single hotel details."""
    if not RAPIDAPI_KEY:
        return _mock_hotel_detail(hotel_id, check_in, check_out)

    return _mock_hotel_detail(hotel_id, check_in, check_out)


# --- MOCK DATA ---
def _mock_destinations(query: str) -> list:
    destinations = [
        {'cityId': '1',  'cityName': 'Dubai',       'countryName': 'الإمارات', 'nameAr': 'دبي - الإمارات'},
        {'cityId': '2',  'cityName': 'Istanbul',    'countryName': 'تركيا',           'nameAr': 'إسطنبول - تركيا'},
        {'cityId': '3',  'cityName': 'Cairo',       'countryName': 'مصر',          'nameAr': 'القاهرة - مصر'},
    ]
    return destinations

def _mock_hotels(city_id, check_in, check_out, adults):
    try:
        ci = datetime.strptime(check_in, '%Y-%m-%d')
        co = datetime.strptime(check_out, '%Y-%m-%d')
        nights = max((co - ci).days, 1)
    except Exception:
        nights = 1

    price_per_night = 80.0
    total = price_per_night * nights
    
    return [{
        'hotelId': 10101,
        'hotelName': 'فندق وريزيدنس الفخامة (Booking.com Mock)',
        'cityName': 'المدينة',
        'cityId': city_id,
        'starRating': 4,
        'reviewScore': 8.5,
        'reviewCount': 500,
        'minPrice': total,
        'currency': 'USD',
        'imageUrl': 'https://images.unsplash.com/photo-1542314831-c6a4d1409b54?w=600&h=300&fit=crop',
        'address': 'وسط المدينة',
        'amenities': ['واي فاي مجاني', 'مسبح'],
        'pricing': apply_markup(total)
    }]

def _mock_hotel_detail(hotel_id, check_in, check_out):
    hotel = _mock_hotels(1, check_in, check_out, 2)[0]
    total = hotel['minPrice']
    
    hotel['description'] = 'فندق رائع وجميل بخدمات ممتازة.'
    hotel['rooms'] = [
        {
            'roomId': 1, 'roomName': 'غرفة قياسية مزدوجة',
            'price': total, 'capacity': 2, 'bedType': 'سرير مزدوج كبير',
            'pricing': apply_markup(total)
        }
    ]
    hotel['booking_url'] = "#"
    return hotel
