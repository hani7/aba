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

MOCK_HOTELS = [
    # ── DUBAI ──
    {'hotelId': 10001, 'hotelName': 'Grand Hyatt Dubai',        'cityName': 'Dubai',    'cityId': 1, 'starRating': 5, 'reviewScore': 8.9, 'reviewCount': 4521, 'minPrice': 180.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&h=300&fit=crop', 'amenities': ['واي فاي مجاني', 'مسبح', 'مركز لياقة', 'موقف سيارات'], 'address': 'شارع الكورنيش، دبي'},
    {'hotelId': 10009, 'hotelName': 'Burj Al Arab Dubai',       'cityName': 'Dubai',    'cityId': 1, 'starRating': 7, 'reviewScore': 9.6, 'reviewCount': 6200, 'minPrice': 950.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&h=300&fit=crop', 'amenities': ['شاطئ خاص', 'هليباد', 'سبا فاخر', 'كونسيرج 24/7'], 'address': 'شارع الجميرا، دبي'},
    {'hotelId': 10010, 'hotelName': 'Atlantis The Palm Dubai',  'cityName': 'Dubai',    'cityId': 1, 'starRating': 5, 'reviewScore': 8.4, 'reviewCount': 5100, 'minPrice': 320.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600&h=300&fit=crop', 'amenities': ['حديقة مائية', 'شاطئ خاص', 'مطاعم', 'كازينو'], 'address': 'نخلة جميرا، دبي'},
    # ── PARIS ──
    {'hotelId': 10002, 'hotelName': 'Sofitel Paris Le Faubourg','cityName': 'Paris',    'cityId': 2, 'starRating': 5, 'reviewScore': 9.1, 'reviewCount': 2870, 'minPrice': 320.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600&h=300&fit=crop', 'amenities': ['واي فاي مجاني', 'مطعم', 'سبا', 'كونسيرج 24/7'], 'address': '15 Rue Boissy dAnglas, Paris'},
    {'hotelId': 10011, 'hotelName': 'Le Meurice Paris',         'cityName': 'Paris',    'cityId': 2, 'starRating': 5, 'reviewScore': 9.5, 'reviewCount': 1890, 'minPrice': 680.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=600&h=300&fit=crop', 'amenities': ['إطلالة على حديقة التويلري', 'مطعم ميشلان', 'سبا', 'مسبح'], 'address': '228 Rue de Rivoli, Paris'},
    {'hotelId': 10012, 'hotelName': 'Hôtel Plaza Athénée Paris','cityName': 'Paris',    'cityId': 2, 'starRating': 5, 'reviewScore': 9.2, 'reviewCount': 2400, 'minPrice': 500.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600&h=300&fit=crop', 'amenities': ['إطلالة على برج إيفل', 'مطعم', 'سبا', 'واي فاي مجاني'], 'address': '25 Avenue Montaigne, Paris'},
    # ── ISTANBUL ──
    {'hotelId': 10003, 'hotelName': 'Hilton Istanbul Bomonti',  'cityName': 'Istanbul', 'cityId': 3, 'starRating': 5, 'reviewScore': 8.7, 'reviewCount': 3102, 'minPrice': 95.0,  'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1596436889106-be35e843f974?w=600&h=300&fit=crop', 'amenities': ['واي فاي مجاني', 'مسبح', 'إطلالة على البوسفور', 'مطعم'], 'address': 'Silahşör Cd. 42, Bomonti, Istanbul'},
    {'hotelId': 10013, 'hotelName': 'Four Seasons Bosphorus',   'cityName': 'Istanbul', 'cityId': 3, 'starRating': 5, 'reviewScore': 9.4, 'reviewCount': 2800, 'minPrice': 350.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1508009603885-247a597a1599?w=600&h=300&fit=crop', 'amenities': ['إطلالة بوسفورية', 'سبا', 'مسبح', 'مطعم فاخر'], 'address': 'Çırağan Cd. 28, Beşiktaş, Istanbul'},
    {'hotelId': 10014, 'hotelName': 'Raffles Istanbul',         'cityName': 'Istanbul', 'cityId': 3, 'starRating': 5, 'reviewScore': 9.0, 'reviewCount': 1500, 'minPrice': 220.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1533395427226-788cee25cc7b?w=600&h=300&fit=crop', 'amenities': ['سبا', 'مسبح', 'مطعم', 'واي فاي مجاني'], 'address': 'Zorlu Center, Levent, Istanbul'},
    # ── CAIRO ──
    {'hotelId': 10004, 'hotelName': 'Marriott Cairo',           'cityName': 'Cairo',    'cityId': 4, 'starRating': 5, 'reviewScore': 8.5, 'reviewCount': 1988, 'minPrice': 120.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1553913861-c0fddf2619ee?w=600&h=300&fit=crop', 'amenities': ['واي فاي مجاني', 'مسبح', 'حديقة نيلية', 'مطعم فاخر'], 'address': 'جزيرة الزمالك، القاهرة'},
    {'hotelId': 10015, 'hotelName': 'Four Seasons Cairo Nile',  'cityName': 'Cairo',    'cityId': 4, 'starRating': 5, 'reviewScore': 9.1, 'reviewCount': 2500, 'minPrice': 200.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600&h=300&fit=crop', 'amenities': ['إطلالة على النيل', 'سبا', 'مسبح', 'مطاعم متعددة'], 'address': '35 شارع شارل ديغول، الجيزة'},
    {'hotelId': 10016, 'hotelName': 'Kempinski Nile Cairo',     'cityName': 'Cairo',    'cityId': 4, 'starRating': 5, 'reviewScore': 8.8, 'reviewCount': 1600, 'minPrice': 160.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?w=600&h=300&fit=crop', 'amenities': ['إطلالة على النيل', 'واي فاي مجاني', 'مسبح', 'منتجع صحي'], 'address': '12 أحمد رائف، الجيزة'},
    # ── LONDON ──
    {'hotelId': 10017, 'hotelName': 'The Ritz London',          'cityName': 'London',   'cityId': 5, 'starRating': 5, 'reviewScore': 9.5, 'reviewCount': 3200, 'minPrice': 850.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1535827841776-24afc1e255ac?w=600&h=300&fit=crop', 'amenities': ['واي فاي مجاني', 'مطعم ميشلان', 'بار فاخر', 'كونسيرج'], 'address': '150 Piccadilly, London'},
    {'hotelId': 10018, 'hotelName': 'Claridges London',         'cityName': 'London',   'cityId': 5, 'starRating': 5, 'reviewScore': 9.3, 'reviewCount': 2900, 'minPrice': 680.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=600&h=300&fit=crop', 'amenities': ['سبا', 'مطعم', 'واي فاي مجاني', 'صالة رجال أعمال'], 'address': 'Brook Street, Mayfair, London'},
    # ── RIYADH ──
    {'hotelId': 10005, 'hotelName': 'The Ritz-Carlton Riyadh',  'cityName': 'Riyadh',   'cityId': 6, 'starRating': 5, 'reviewScore': 9.3, 'reviewCount': 2145, 'minPrice': 250.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&h=300&fit=crop', 'amenities': ['واي فاي مجاني', 'سبا', 'صالة رجال أعمال', 'مسابح متعددة'], 'address': 'طريق الملك عبدالعزيز، الرياض'},
    {'hotelId': 10019, 'hotelName': 'Four Seasons Riyadh',      'cityName': 'Riyadh',   'cityId': 6, 'starRating': 5, 'reviewScore': 9.0, 'reviewCount': 1800, 'minPrice': 300.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600&h=300&fit=crop', 'amenities': ['سبا', 'مسبح', 'مطعم فاخر', 'واي فاي مجاني'], 'address': 'طريق الملك فهد، الرياض'},
    # ── DOHA ──
    {'hotelId': 10006, 'hotelName': 'InterContinental Doha',    'cityName': 'Doha',     'cityId': 7, 'starRating': 5, 'reviewScore': 8.8, 'reviewCount': 1776, 'minPrice': 160.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?w=600&h=300&fit=crop', 'amenities': ['شاطئ خاص', 'واي فاي مجاني', 'إطلالة على الخليج', 'مسبح'], 'address': 'شارع الكورنيش، الدوحة'},
    {'hotelId': 10020, 'hotelName': 'W Doha',                   'cityName': 'Doha',     'cityId': 7, 'starRating': 5, 'reviewScore': 9.0, 'reviewCount': 2100, 'minPrice': 220.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&h=300&fit=crop', 'amenities': ['مسبح', 'سبا', 'ملهى ليلي', 'واي فاي مجاني'], 'address': 'West Bay, Doha'},
    # ── MADRID ──
    {'hotelId': 10007, 'hotelName': 'Four Seasons Madrid',      'cityName': 'Madrid',   'cityId': 9, 'starRating': 5, 'reviewScore': 9.4, 'reviewCount': 987,  'minPrice': 420.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=600&h=300&fit=crop', 'amenities': ['سبا فاخر', 'مسبح داخلي', 'مطعم ميشلان', 'واي فاي مجاني'], 'address': 'Calle de Sevilla 3, Madrid'},
    {'hotelId': 10021, 'hotelName': 'Mandarin Oriental Madrid', 'cityName': 'Madrid',   'cityId': 9, 'starRating': 5, 'reviewScore': 9.2, 'reviewCount': 1200, 'minPrice': 550.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600&h=300&fit=crop', 'amenities': ['سبا', 'مطعم', 'بار على السطح', 'واي فاي مجاني'], 'address': 'Paseo de la Castellana 200, Madrid'},
    # ── BANGKOK ──
    {'hotelId': 10008, 'hotelName': 'Park Hyatt Bangkok',       'cityName': 'Bangkok',  'cityId': 8, 'starRating': 5, 'reviewScore': 9.0, 'reviewCount': 3321, 'minPrice': 75.0,  'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1508009603885-247a597a1599?w=600&h=300&fit=crop', 'amenities': ['واي فاي مجاني', 'مسبح على السطح', 'منتجع صحي', 'مطعم'], 'address': 'Wireless Road, Pathumwan, Bangkok'},
    {'hotelId': 10022, 'hotelName': 'Mandarin Oriental Bangkok', 'cityName': 'Bangkok', 'cityId': 8, 'starRating': 5, 'reviewScore': 9.3, 'reviewCount': 4100, 'minPrice': 180.0, 'currency': 'USD', 'imageUrl': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600&h=300&fit=crop', 'amenities': ['نادي نهري', 'سبا', 'مطاعم متعددة', 'واي فاي مجاني'], 'address': '48 Oriental Avenue, Bangkok'},
]

# Map city_id (from _mock_destinations) to cityName in MOCK_HOTELS
_CITY_ID_MAP = {
    1: 'Dubai', 2: 'Paris', 3: 'Istanbul', 4: 'Cairo',
    5: 'London', 6: 'Riyadh', 7: 'Doha', 8: 'Bangkok',
    9: 'Madrid', 10: 'Marrakech', 11: 'Algiers', 12: 'Casablanca',
    13: 'Tunis', 14: 'Abu Dhabi', 15: 'Beirut', 16: 'Kuwait City',
    17: 'New York', 18: 'Barcelona', 19: 'Rome', 20: 'Amsterdam',
    21: 'Singapore', 22: 'Muscat', 23: 'Amman', 24: 'Khartoum',
}


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
        for h in MOCK_HOTELS[:3]:
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
