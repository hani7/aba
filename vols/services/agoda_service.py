"""
Agoda Hotel Service
-------------------
Integrates with the Agoda Affiliate / Partner API for hotel search.
Requires:
  - AGODA_API_KEY    (your Agoda API key from partners.agoda.com)
  - AGODA_SITE_ID    (your numeric site/affiliate ID)
  - AGODA_MARKUP_PCT (optional markup percentage, default 10%)

Booking flow:
  1. search_hotels()  → list of hotel offers with real Agoda prices
  2. get_hotel()      → single hotel detail + rooms
  3. book_hotel()     → creates Agoda affiliate deep-link redirect URL
                        (full B2B direct booking requires Agoda B2B API approval)

Profit model:
  - You charge the customer (Agoda price × (1 + markup/100))
  - Agoda pays you 4–7% commission on actual bookings via affiliate
"""

import requests
from django.conf import settings

AGODA_API_URL    = getattr(settings, 'AGODA_API_URL',    'https://affiliateapi7643.agoda.com/api/v3')
AGODA_API_KEY    = getattr(settings, 'AGODA_API_KEY',    '')
AGODA_SITE_ID    = getattr(settings, 'AGODA_SITE_ID',    0)
AGODA_MARKUP_PCT = getattr(settings, 'AGODA_MARKUP_PCT', 10)   # % markup over Agoda price


def _headers():
    return {
        'Authorization': f'Bearer {AGODA_API_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


from typing import Optional

def apply_markup(price: float, markup_pct: Optional[float] = None) -> dict:
    """
    Calculate customer price and agency profit.
    Returns dict with:
      - original_price  : Agoda real price
      - markup_amount   : your profit (DZD or currency equivalent)
      - customer_price  : what the customer pays
      - markup_pct      : the markup percentage applied
    """
    if markup_pct is None:
        markup_pct = float(AGODA_MARKUP_PCT)
    markup_amount  = round(price * markup_pct / 100, 2)
    customer_price = round(price + markup_amount, 2)
    return {
        'original_price':  price,
        'markup_amount':   markup_amount,
        'customer_price':  customer_price,
        'markup_pct':      markup_pct,
    }


def search_hotels(city_id: int, check_in: str, check_out: str,
                  adults: int = 2, rooms: int = 1,
                  currency: str = 'USD', language: str = 'ar-ae') -> list:
    """
    Search available hotels for a city/destination.

    Parameters
    ----------
    city_id   : Agoda city ID (use search_destinations to get this)
    check_in  : 'YYYY-MM-DD'
    check_out : 'YYYY-MM-DD'
    adults    : number of adults
    rooms     : number of rooms

    Returns list of hotel dicts enriched with markup info.
    """
    if not AGODA_API_KEY or not AGODA_SITE_ID:
        return _mock_hotels(city_id, check_in, check_out, adults)

    payload = {
        'criteria': {
            'additional': {
                'currency':  currency,
                'language':  language,
                'siteId':    AGODA_SITE_ID,
                'userId':    'agency-user',
            },
            'checkIn':     check_in,
            'checkOut':    check_out,
            'cityId':      city_id,
            'occupancy': {
                'adults': adults,
                'rooms':  rooms,
            },
        }
    }

    try:
        resp = requests.post(
            f'{AGODA_API_URL}/hotel/search',
            json=payload,
            headers=_headers(),
            timeout=20,
        )
        if resp.status_code not in (200, 201):
            raise Exception(f'Agoda API Error {resp.status_code}: {resp.text}')

        hotels = resp.json().get('result', {}).get('hotels', [])
        return _enrich_hotels(hotels)

    except Exception as e:
        print(f'Agoda search error: {e} — returning mock data for demo')
        return _mock_hotels(city_id, check_in, check_out, adults)


def get_hotel(hotel_id: int, check_in: str, check_out: str,
              adults: int = 2, rooms: int = 1, currency: str = 'USD') -> dict:
    """Get detailed info for a single hotel including room types."""
    if not AGODA_API_KEY or not AGODA_SITE_ID:
        return _mock_hotel_detail(hotel_id, check_in, check_out)

    payload = {
        'criteria': {
            'additional': {
                'currency': currency,
                'language': 'ar-ae',
                'siteId':   AGODA_SITE_ID,
            },
            'checkIn':  check_in,
            'checkOut': check_out,
            'hotelId':  hotel_id,
            'occupancy': {
                'adults': adults,
                'rooms':  rooms,
            },
        }
    }

    try:
        resp = requests.post(
            f'{AGODA_API_URL}/hotel/detail',
            json=payload,
            headers=_headers(),
            timeout=15,
        )
        if resp.status_code != 200:
            raise Exception(f'Agoda API Error {resp.status_code}')
        hotel = resp.json().get('result', {}).get('hotel', {})
        return _enrich_hotel(hotel)
    except Exception as e:
        print(f'Agoda detail error: {e}')
        return _mock_hotel_detail(hotel_id, check_in, check_out)


def search_destinations(query: str) -> list:
    """Search Agoda destinations/cities by name."""
    if not AGODA_API_KEY or not AGODA_SITE_ID:
        return _mock_destinations(query)

    try:
        resp = requests.get(
            f'{AGODA_API_URL}/property/suggest',
            params={
                'q':       query,
                'siteId':  AGODA_SITE_ID,
                'lang':    'ar-ae',
            },
            headers=_headers(),
            timeout=10,
        )
        if resp.status_code != 200:
            return _mock_destinations(query)
        return resp.json().get('result', [])
    except Exception:
        return _mock_destinations(query)


def get_booking_url(hotel_id: int, check_in: str, check_out: str,
                    adults: int = 2, rooms: int = 1) -> str:
    """
    Generate an Agoda affiliate deep-link for booking.
    The customer is redirected to Agoda to complete the booking.
    You earn 4-7% commission automatically.
    """
    base = 'https://www.agoda.com'
    params = (
        f'?hotelId={hotel_id}'
        f'&checkIn={check_in}'
        f'&checkOut={check_out}'
        f'&adults={adults}'
        f'&rooms={rooms}'
        f'&site_id={AGODA_SITE_ID}'
        f'&tag=abumonyatravel'
        f'&lang=ar-ae'
    )
    return f'{base}/partners/partnersearch.aspx{params}'


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _enrich_hotels(hotels: list) -> list:
    enriched = []
    for h in hotels:
        price = float(h.get('minPrice', 0))
        h['pricing'] = apply_markup(price)
        h.setdefault('starRating', 3)
        h.setdefault('reviewScore', 0)
        h.setdefault('reviewCount', 0)
        h.setdefault('imageUrl', '')
        enriched.append(h)
    return enriched


def _enrich_hotel(hotel: dict) -> dict:
    price = float(hotel.get('minPrice', 0))
    hotel['pricing'] = apply_markup(price)
    return hotel


# ---------------------------------------------------------------------------
# Mock / demo data (used when API keys are not configured yet)
# ---------------------------------------------------------------------------

_CITY_ID_MAP = {
    1: 'Dubai', 2: 'Paris', 3: 'Istanbul', 4: 'Cairo',
    5: 'London', 6: 'Riyadh', 7: 'Doha', 8: 'Bangkok',
    9: 'Madrid', 10: 'Marrakech', 11: 'Algiers', 12: 'Casablanca',
    13: 'Tunis', 14: 'Abu Dhabi', 15: 'Beirut', 16: 'Kuwait City',
    17: 'New York', 18: 'Barcelona', 19: 'Rome', 20: 'Amsterdam',
    21: 'Singapore', 22: 'Muscat', 23: 'Amman', 24: 'Khartoum',
}

def _generate_bulk_hotels():
    import random
    brands = ['Hilton', 'Marriott', 'Sheraton', 'Radisson', 'Hyatt', 'InterContinental', 'Novotel', 'Sofitel', 'Ibis', 'Grand', 'Royal', 'Mercure', 'Ramada', 'Holiday Inn', 'Westin', 'Four Seasons', 'Kempinski', 'Mövenpick']
    types = ['Hotel', 'Resort', 'Palace', 'Suites', 'Plaza', 'Towers', 'Inn', 'Gardens', 'Residence']
    landmarks = ['Central', 'Downtown', 'Airport', 'Beach', 'Old City', 'Skyline', 'Riverside', 'Station', 'Park Side']
    
    amenities_pool = ['واي فاي مجاني', 'مسبح', 'مركز لياقة', 'موقف سيارات', 'سبا', 'مطعم فاخر', 'إفطار مجاني', 'خدمة غرف', 'صالة رجال أعمال']
    
    final_list = []
    base_id = 10000
    
    for city_id, city_name in _CITY_ID_MAP.items():
        # Generate 25 hotels per city
        for i in range(25):
            brand = random.choice(brands)
            type_str = random.choice(types)
            landmark = random.choice(landmarks)
            
            # Mix them up
            if i % 3 == 0:
                hotel_name = f"{brand} {city_name} {landmark}"
            elif i % 3 == 1:
                hotel_name = f"{landmark} {brand} {type_str}"
            else:
                hotel_name = f"{city_name} {brand} {type_str}"
                
            hotel_id = base_id + (city_id * 100) + i
            
            final_list.append({
                'hotelId': hotel_id,
                'hotelName': hotel_name,
                'cityName': city_name,
                'cityId': city_id,
                'starRating': random.choice([3, 4, 5, 5]),
                'reviewScore': round(random.uniform(7.5, 9.8), 1),
                'reviewCount': random.randint(100, 8000),
                'minPrice': random.randint(60, 600) + 0.0,
                'currency': 'USD',
                'imageUrl': f'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&h=300&fit=crop&sig={hotel_id}',
                'amenities': random.sample(amenities_pool, random.randint(3, 6)),
                'address': f'شارع الرئيسي، {city_name}'
            })
            
    return final_list

MOCK_HOTELS = _generate_bulk_hotels()


def _mock_hotels(city_id, check_in, check_out, adults):
    """Return realistic mock hotel data filtered by city_id."""
    from datetime import datetime
    try:
        ci = datetime.strptime(check_in, '%Y-%m-%d')
        co = datetime.strptime(check_out, '%Y-%m-%d')
        nights = max((co - ci).days, 1)
    except Exception:
        nights = 1

    # Look up the target city name from city_id
    target_city = _CITY_ID_MAP.get(int(city_id) if city_id else 0, '')

    result = []
    for h in MOCK_HOTELS:
        # Only return hotels that match the searched city
        city_name_str = str(h.get('cityName', ''))
        if target_city and city_name_str.lower() != target_city.lower():
            continue
        hotel = dict(h)
        min_price = float(str(hotel.get('minPrice', 0)))
        total = round(min_price * nights, 2)
        hotel['minPrice'] = total
        hotel['nights']   = nights
        hotel['pricing']  = apply_markup(total) # type: ignore
        result.append(hotel)

    # If no specific city found in mocks, return a generic subset to avoid empty screen
    if not result:
        for h in MOCK_HOTELS[:20]:
            hotel = dict(h)
            min_price = float(str(hotel.get('minPrice', 0)))
            total = round(min_price * nights, 2)
            hotel['minPrice'] = total
            hotel['nights']   = nights
            hotel['pricing']  = apply_markup(total) # type: ignore
            result.append(hotel)

    return result


def _mock_hotel_detail(hotel_id, check_in, check_out):
    base = next((h for h in MOCK_HOTELS if h['hotelId'] == hotel_id), MOCK_HOTELS[0])
    hotel = dict(base)
    try:
        from datetime import datetime
        nights = max((
            datetime.strptime(check_out, '%Y-%m-%d') -
            datetime.strptime(check_in,  '%Y-%m-%d')
        ).days, 1)
    except Exception:
        nights = 1

    total = round(hotel['minPrice'] * nights, 2)
    hotel['minPrice'] = total
    hotel['nights']   = nights
    hotel['pricing']  = apply_markup(total)
    hotel['description'] = (
        'فندق فاخر يوفر تجربة إقامة استثنائية مع مرافق عالمية المستوى. '
        'يضم غرفاً واسعة مع إطلالات رائعة، ومطعماً فاخراً يقدم أشهى المأكولات، '
        'ومنتجعاً صحياً متكاملاً لضمان راحة تامة طوال إقامتك.'
    )
    hotel['rooms'] = [
        {
            'roomId': 1, 'roomName': 'غرفة ديلوكس',
            'price': round(hotel['minPrice'] / nights, 2),
            'pricing': apply_markup(round(hotel['minPrice'] / nights, 2)),
            'capacity': 2, 'bedType': 'سرير كينغ',
        },
        {
            'roomId': 2, 'roomName': 'جناح ريجنت',
            'price': round(hotel['minPrice'] / nights * 1.5, 2),
            'pricing': apply_markup(round(hotel['minPrice'] / nights * 1.5, 2)),
            'capacity': 2, 'bedType': 'سريران توين',
        },
        {
            'roomId': 3, 'roomName': 'جناح رئاسي',
            'price': round(hotel['minPrice'] / nights * 2.2, 2),
            'pricing': apply_markup(round(hotel['minPrice'] / nights * 2.2, 2)),
            'capacity': 4, 'bedType': 'سرير كينغ + صالة',
        },
    ]
    hotel['booking_url'] = get_booking_url(hotel_id, check_in, check_out)
    return hotel


def _mock_destinations(query: str) -> list:
    destinations = [
        {'cityId': 1,  'cityName': 'Dubai',       'countryName': 'الإمارات العربية المتحدة', 'nameAr': 'دبي'},
        {'cityId': 2,  'cityName': 'Paris',        'countryName': 'فرنسا',                   'nameAr': 'باريس'},
        {'cityId': 3,  'cityName': 'Istanbul',     'countryName': 'تركيا',                   'nameAr': 'إسطنبول'},
        {'cityId': 4,  'cityName': 'Cairo',        'countryName': 'مصر',                     'nameAr': 'القاهرة'},
        {'cityId': 5,  'cityName': 'London',       'countryName': 'المملكة المتحدة',          'nameAr': 'لندن'},
        {'cityId': 6,  'cityName': 'Riyadh',       'countryName': 'السعودية',                'nameAr': 'الرياض'},
        {'cityId': 7,  'cityName': 'Doha',         'countryName': 'قطر',                     'nameAr': 'الدوحة'},
        {'cityId': 8,  'cityName': 'Bangkok',      'countryName': 'تايلاند',                 'nameAr': 'بانكوك'},
        {'cityId': 9,  'cityName': 'Madrid',       'countryName': 'إسبانيا',                 'nameAr': 'مدريد'},
        {'cityId': 10, 'cityName': 'Marrakech',    'countryName': 'المغرب',                  'nameAr': 'مراكش'},
        {'cityId': 11, 'cityName': 'Algiers',      'countryName': 'الجزائر',                 'nameAr': 'الجزائر'},
        {'cityId': 12, 'cityName': 'Casablanca',   'countryName': 'المغرب',                  'nameAr': 'الدار البيضاء'},
        {'cityId': 13, 'cityName': 'Tunis',        'countryName': 'تونس',                    'nameAr': 'تونس'},
        {'cityId': 14, 'cityName': 'Abu Dhabi',    'countryName': 'الإمارات العربية المتحدة', 'nameAr': 'أبوظبي'},
        {'cityId': 15, 'cityName': 'Beirut',       'countryName': 'لبنان',                   'nameAr': 'بيروت'},
        {'cityId': 16, 'cityName': 'Kuwait City',  'countryName': 'الكويت',                  'nameAr': 'مدينة الكويت'},
        {'cityId': 17, 'cityName': 'New York',     'countryName': 'الولايات المتحدة',         'nameAr': 'نيويورك'},
        {'cityId': 18, 'cityName': 'Barcelona',    'countryName': 'إسبانيا',                 'nameAr': 'برشلونة'},
        {'cityId': 19, 'cityName': 'Rome',         'countryName': 'إيطاليا',                 'nameAr': 'روما'},
        {'cityId': 20, 'cityName': 'Amsterdam',    'countryName': 'هولندا',                  'nameAr': 'أمستردام'},
        {'cityId': 21, 'cityName': 'Singapore',    'countryName': 'سنغافورة',                'nameAr': 'سنغافورة'},
        {'cityId': 22, 'cityName': 'Muscat',       'countryName': 'عُمان',                   'nameAr': 'مسقط'},
        {'cityId': 23, 'cityName': 'Amman',        'countryName': 'الأردن',                  'nameAr': 'عمان'},
        {'cityId': 24, 'cityName': 'Khartoum',     'countryName': 'السودان',                 'nameAr': 'الخرطوم'},
    ]
    q = query.strip().lower()
    # Strip Arabic definite article "ال" for better partial matching
    # e.g. typing "قاهر" should still match "القاهرة"
    q_stripped = q.lstrip('ا').lstrip('ل') if q.startswith('ال') else q
    
    results = []
    for d in destinations:
        en = str(d.get('cityName', '')).lower()
        ar = str(d.get('nameAr', ''))
        country = str(d.get('countryName', ''))
        # Match: English partial, Arabic partial, Arabic without "ال", or country name
        if (q in en or
            q in ar or
            q_stripped in ar or
            q in country.lower()):
            results.append(d)
    return results
