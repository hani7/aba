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
# Typically 'booking-com15.p.rapidapi.com'
RAPIDAPI_HOST = getattr(settings, 'RAPIDAPI_HOST', 'booking-com15.p.rapidapi.com')

HOTEL_MARKUP_PCT = 10.0  # Default markup for hotel bookings


def _headers():
    return {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST,
        "useQueryString": "true"
    }

def apply_markup(price: float) -> dict:
    """Apply hotel markup (using HOTEL_MARKUP_PCT)."""
    markup_pct = HOTEL_MARKUP_PCT
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

    url = f"https://{RAPIDAPI_HOST}/api/v1/hotels/searchDestination"
    querystring = {"query": query}

    try:
        response = requests.get(url, headers=_headers(), params=querystring, timeout=15)
        data = response.json()
        results = []
        # The API usually returns a list of objects under 'data'
        locations = data.get('data', [])
        for loc in locations:
            # We filter for cities or locations that have a dest_id
            dest_id = loc.get('dest_id')
            if dest_id:
                results.append({
                    'cityId': dest_id,
                    'cityName': loc.get('name'),
                    'countryName': loc.get('country'),
                    'nameAr': loc.get('label') or loc.get('name')
                })
        return results if results else _mock_destinations(query)
    except Exception as e:
        print(f"Error in search_destinations: {e}")
        return _mock_destinations(query)


def search_hotels(city_id: str, check_in: str, check_out: str, adults: int = 2, rooms: int = 1) -> list:
    """Search for hotels in a destination ID."""
    if not RAPIDAPI_KEY:
        return _mock_hotels(city_id, check_in, check_out, adults)

    url = f"https://{RAPIDAPI_HOST}/api/v1/hotels/searchHotels"
    querystring = {
        "dest_id": city_id,
        "search_type": "CITY",
        "arrival_date": check_in,
        "departure_date": check_out,
        "adults": str(adults),
        "room_qty": str(rooms),
        "page_number": "1",
        "units": "metric",
        "temperature_unit": "c",
        "language_code": "en-us",
        "currency_code": "USD"
    }

    try:
        response = requests.get(url, headers=_headers(), params=querystring, timeout=20)
        data = response.json()
        results = []
        
        # Mapping properties from RapidAPI response to our template format
        # Properties usually under data['data']['hotels'] or data['data']['result'] depending on version
        hotels = data.get('data', {}).get('hotels', [])
        if not hotels:
            hotels = data.get('data', {}).get('result', [])
            
        for h in hotels[:40]:
            # RapidAPI responses for Booking.com vary; we check multiple common price keys
            # Often it is under property['price_breakdown']['gross_price']
            price_info = h.get('price_breakdown', {})
            price = float(price_info.get('gross_amount', 0) or h.get('min_total_price', 0))
            if price == 0: continue
            
            results.append({
                'hotelId': str(h.get('hotel_id')),
                'hotelName': h.get('hotel_name'),
                'cityId': city_id,
                'cityName': h.get('city_name') or h.get('city'),
                'starRating': h.get('class', 3),
                'reviewScore': h.get('review_score', 8),
                'reviewCount': h.get('review_nr', 100),
                'minPrice': price,
                'pricing': apply_markup(price),
                'currency': h.get('currency_code') or h.get('currencycode', 'USD'),
                'imageUrl': h.get('max_photo_url') or h.get('main_photo_url'),
                'address': h.get('address', ''),
                'amenities': ['واي فاي مجاني', 'موقع متميز']
            })
        return results if results else _mock_hotels(city_id, check_in, check_out, adults)
    except Exception as e:
        print(f"Error in search_hotels: {e}")
        return _mock_hotels(city_id, check_in, check_out, adults)


def get_hotel(hotel_id: str, check_in: str, check_out: str, adults: int = 2, rooms: int = 1) -> dict:
    """Get single hotel details including rooms."""
    if not RAPIDAPI_KEY:
        return _mock_hotel_detail(hotel_id, check_in, check_out)

    url = f"https://{RAPIDAPI_HOST}/api/v1/hotels/getHotelDetails"
    querystring = {
        "hotel_id": hotel_id,
        "arrival_date": check_in,
        "departure_date": check_out,
        "adults": str(adults),
        "room_qty": str(rooms),
        "language_code": "en-us",
        "currency_code": "USD"
    }

    try:
        response = requests.get(url, headers=_headers(), params=querystring, timeout=15)
        data = response.json()
        hotel_data = data.get('data', {})
        
        if not hotel_data:
            return _mock_hotel_detail(hotel_id, check_in, check_out)

        # Build standardized hotel object
        price = float(hotel_data.get('min_total_price', 0) or 100.0)
        hotel = {
            'hotelId': hotel_id,
            'hotelName': hotel_data.get('hotel_name'),
            'cityName': hotel_data.get('city'),
            'cityId': hotel_data.get('city_id'),
            'starRating': hotel_data.get('class', 3),
            'reviewScore': hotel_data.get('review_score', 8),
            'reviewCount': hotel_data.get('review_nr', 100),
            'minPrice': price,
            'currency': 'USD',
            'imageUrl': hotel_data.get('main_photo_url'),
            'address': hotel_data.get('address', ''),
            'description': hotel_data.get('description') or "لا يوجد وصف مطول متاح حالياً.",
            'amenities': [a.get('facility_name') for a in hotel_data.get('facilities', [])[:10]],
            'pricing': apply_markup(price),
            'rooms': []
        }

        # Handle room options
        room_data = hotel_data.get('rooms', {})
        for r_id, r_info in room_data.items():
            r_price = float(r_info.get('min_price', price))
            hotel['rooms'].append({
                'roomId': r_id,
                'roomName': r_info.get('room_name', 'غرفة قياسية'),
                'price': r_price,
                'capacity': 2,
                'bedType': 'سرير مريح',
                'pricing': apply_markup(r_price)
            })
            
        hotel['booking_url'] = hotel_data.get('url') or "#"
        return hotel
    except Exception as e:
        print(f"Error in get_hotel: {e}")
        return _mock_hotel_detail(hotel_id, check_in, check_out)


def get_booking_url(hotel_id: str, check_in: str, check_out: str, adults: int = 2, rooms: int = 1) -> str:
    """
    Get the booking URL for a hotel. 
    Since the RapidAPI provides this in details, we fetch details and return the URL.
    """
    hotel = get_hotel(hotel_id, check_in, check_out, adults, rooms)
    return hotel.get('booking_url', "#")


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
        'hotelName': 'فندق الموك (تجريبي)',
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
