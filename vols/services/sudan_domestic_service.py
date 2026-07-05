"""
Sudan Domestic Flights Service
================================
Provides internal flight search for Sudan using:
  1. AeroDataBox API via RapidAPI (real live/schedule data)
  2. Rich mock fallback — used when the API has no data or key is missing.

Sudan domestic airlines covered:
  - Sudan Airways  (SD)  — historic national carrier
  - Badr Airlines  (J4)  — hub: Port Sudan (PZU)
  - Tarco Aviation (TJ)  — hub: Khartoum / Port Sudan

All prices are in USD.  Markup is applied by the caller (views.py).

Key airports:
  KRT  Khartoum International (limited / currently contested)
  PZU  Port Sudan New International (main active hub)
  KSL  Kassala Airport
  DOG  Dongola Airport
  ELF  El Fasher Airport
  UYL  Nyala Airport
  EBD  El Obeid Airport
  ATB  Atbara Airport
  MWE  Merowe Airport
  RSS  Damazin Airport
  KDX  Kadugli Airport
  EGN  Geneina Airport
  WHF  Wadi Halfa Airport
"""

import uuid
import requests
from django.conf import settings

# ── Configuration ─────────────────────────────────────────────────────────────
RAPIDAPI_KEY = getattr(settings, 'RAPIDAPI_KEY', '')
AERODATABOX_HOST = 'aerodatabox.p.rapidapi.com'
AERODATABOX_BASE = f'https://{AERODATABOX_HOST}'

# ── Sudan airport registry ─────────────────────────────────────────────────────
SUDAN_AIRPORTS = {
    'KRT': {'name': 'مطار الخرطوم الدولي',        'name_en': 'Khartoum International',        'city': 'الخرطوم',    'city_en': 'Khartoum'},
    'PZU': {'name': 'مطار بورتسودان الدولي الجديد','name_en': 'Port Sudan New International',  'city': 'بورتسودان', 'city_en': 'Port Sudan'},
    'KSL': {'name': 'مطار كسلا',                   'name_en': 'Kassala Airport',               'city': 'كسلا',       'city_en': 'Kassala'},
    'DOG': {'name': 'مطار دنقلا',                  'name_en': 'Dongola Airport',               'city': 'دنقلا',      'city_en': 'Dongola'},
    'ELF': {'name': 'مطار الفاشر',                 'name_en': 'El Fasher Airport',             'city': 'الفاشر',     'city_en': 'El Fasher'},
    'UYL': {'name': 'مطار نيالا',                  'name_en': 'Nyala Airport',                 'city': 'نيالا',      'city_en': 'Nyala'},
    'EBD': {'name': 'مطار الأبيض',                 'name_en': 'El Obeid Airport',              'city': 'الأبيض',     'city_en': 'El Obeid'},
    'ATB': {'name': 'مطار عطبرة',                  'name_en': 'Atbara Airport',                'city': 'عطبرة',      'city_en': 'Atbara'},
    'MWE': {'name': 'مطار مروي',                   'name_en': 'Merowe Airport',                'city': 'مروي',       'city_en': 'Merowe'},
    'RSS': {'name': 'مطار الدمازين',               'name_en': 'Damazin Airport',               'city': 'الدمازين',   'city_en': 'Damazin'},
    'KDX': {'name': 'مطار كادقلي',                 'name_en': 'Kadugli Airport',               'city': 'كادقلي',     'city_en': 'Kadugli'},
    'EGN': {'name': 'مطار الجنينة',                'name_en': 'Geneina Airport',               'city': 'الجنينة',    'city_en': 'Geneina'},
    'WHF': {'name': 'مطار وادي حلفا',              'name_en': 'Wadi Halfa Airport',            'city': 'وادي حلفا',  'city_en': 'Wadi Halfa'},
    'GSU': {'name': 'مطار القضارف',                'name_en': 'Gedaref Airport',               'city': 'القضارف',    'city_en': 'Gedaref'},
    'KST': {'name': 'مطار كوستي',                  'name_en': 'Kosti Airport',                 'city': 'كوستي',      'city_en': 'Kosti'},
    'NUD': {'name': 'مطار النهود',                  'name_en': 'En Nahud Airport',              'city': 'النهود',     'city_en': 'En Nahud'},
}

# ── Route schedule / price table (realistic 2025 estimates, USD) ───────────────
# Each route key is "ORIG-DEST".  Both directions use the same price.
ROUTE_TABLE = {
    # Port Sudan hub routes
    'PZU-KRT': {'price': 85,  'duration': 'PT1H10M', 'airlines': ['SD', 'J4'], 'dep': '08:00', 'arr': '09:10', 'flight_nums': {'SD': 'SD101', 'J4': 'J4110'}},
    'PZU-KSL': {'price': 55,  'duration': 'PT0H45M', 'airlines': ['J4'],       'dep': '07:00', 'arr': '07:45', 'flight_nums': {'J4': 'J4120'}},
    'PZU-DOG': {'price': 65,  'duration': 'PT1H00M', 'airlines': ['J4'],       'dep': '07:30', 'arr': '08:30', 'flight_nums': {'J4': 'J4130'}},
    'PZU-ELF': {'price': 95,  'duration': 'PT1H20M', 'airlines': ['SD'],       'dep': '09:00', 'arr': '10:20', 'flight_nums': {'SD': 'SD201'}},
    'PZU-UYL': {'price': 110, 'duration': 'PT1H35M', 'airlines': ['SD', 'TJ'], 'dep': '10:00', 'arr': '11:35', 'flight_nums': {'SD': 'SD211', 'TJ': 'TJ301'}},
    'PZU-MWE': {'price': 70,  'duration': 'PT1H05M', 'airlines': ['SD'],       'dep': '08:30', 'arr': '09:35', 'flight_nums': {'SD': 'SD221'}},
    'PZU-ATB': {'price': 60,  'duration': 'PT0H50M', 'airlines': ['SD'],       'dep': '07:45', 'arr': '08:35', 'flight_nums': {'SD': 'SD231'}},
    'PZU-WHF': {'price': 75,  'duration': 'PT1H10M', 'airlines': ['SD'],       'dep': '09:15', 'arr': '10:25', 'flight_nums': {'SD': 'SD241'}},
    'PZU-GSU': {'price': 58,  'duration': 'PT0H48M', 'airlines': ['J4'],       'dep': '08:00', 'arr': '08:48', 'flight_nums': {'J4': 'J4140'}},
    # Khartoum hub routes
    'KRT-KSL': {'price': 60,  'duration': 'PT0H55M', 'airlines': ['SD'],       'dep': '06:30', 'arr': '07:25', 'flight_nums': {'SD': 'SD103'}},
    'KRT-DOG': {'price': 70,  'duration': 'PT1H05M', 'airlines': ['SD'],       'dep': '07:00', 'arr': '08:05', 'flight_nums': {'SD': 'SD113'}},
    'KRT-ELF': {'price': 90,  'duration': 'PT1H15M', 'airlines': ['SD', 'TJ'], 'dep': '09:00', 'arr': '10:15', 'flight_nums': {'SD': 'SD203', 'TJ': 'TJ303'}},
    'KRT-UYL': {'price': 100, 'duration': 'PT1H30M', 'airlines': ['SD', 'TJ'], 'dep': '10:00', 'arr': '11:30', 'flight_nums': {'SD': 'SD213', 'TJ': 'TJ313'}},
    'KRT-EBD': {'price': 55,  'duration': 'PT0H50M', 'airlines': ['SD'],       'dep': '08:00', 'arr': '08:50', 'flight_nums': {'SD': 'SD223'}},
    'KRT-MWE': {'price': 65,  'duration': 'PT1H00M', 'airlines': ['SD'],       'dep': '08:30', 'arr': '09:30', 'flight_nums': {'SD': 'SD233'}},
    'KRT-ATB': {'price': 50,  'duration': 'PT0H45M', 'airlines': ['SD'],       'dep': '07:30', 'arr': '08:15', 'flight_nums': {'SD': 'SD243'}},
    'KRT-RSS': {'price': 80,  'duration': 'PT1H10M', 'airlines': ['SD'],       'dep': '11:00', 'arr': '12:10', 'flight_nums': {'SD': 'SD253'}},
    'KRT-KDX': {'price': 85,  'duration': 'PT1H15M', 'airlines': ['SD'],       'dep': '09:30', 'arr': '10:45', 'flight_nums': {'SD': 'SD263'}},
    'KRT-EGN': {'price': 110, 'duration': 'PT1H40M', 'airlines': ['SD'],       'dep': '10:00', 'arr': '11:40', 'flight_nums': {'SD': 'SD273'}},
    'KRT-WHF': {'price': 80,  'duration': 'PT1H10M', 'airlines': ['SD'],       'dep': '08:00', 'arr': '09:10', 'flight_nums': {'SD': 'SD283'}},
    'KRT-NUD': {'price': 65,  'duration': 'PT1H00M', 'airlines': ['SD'],       'dep': '09:00', 'arr': '10:00', 'flight_nums': {'SD': 'SD293'}},
    'KRT-GSU': {'price': 55,  'duration': 'PT0H50M', 'airlines': ['SD'],       'dep': '07:00', 'arr': '07:50', 'flight_nums': {'SD': 'SD153'}},
    'KRT-KST': {'price': 50,  'duration': 'PT0H45M', 'airlines': ['SD'],       'dep': '07:30', 'arr': '08:15', 'flight_nums': {'SD': 'SD163'}},
    'KRT-PZU': {'price': 85,  'duration': 'PT1H10M', 'airlines': ['SD', 'J4'], 'dep': '09:00', 'arr': '10:10', 'flight_nums': {'SD': 'SD102', 'J4': 'J4111'}},
}

AIRLINE_INFO = {
    'SD': {'name': 'Sudan Airways',  'name_ar': 'الخطوط الجوية السودانية', 'iata': 'SD', 'color': '#007229'},
    'J4': {'name': 'Badr Airlines',  'name_ar': 'خطوط بدر الجوية',         'iata': 'J4', 'color': '#003087'},
    'TJ': {'name': 'Tarco Aviation', 'name_ar': 'تركو للطيران',             'iata': 'TJ', 'color': '#c8102e'},
}


# ══════════════════════════════════════════════════════════════════════════════
# Public API
# ══════════════════════════════════════════════════════════════════════════════

def is_sudan_domestic(origin: str, destination: str) -> bool:
    """Return True if both airports are Sudan domestic airports."""
    return origin.upper() in SUDAN_AIRPORTS and destination.upper() in SUDAN_AIRPORTS


def get_sudan_airports() -> list:
    """Return list of all Sudan airport dicts for autocomplete / dropdowns."""
    result = []
    for iata, info in SUDAN_AIRPORTS.items():
        result.append({
            'iata_code': iata,
            'name': info['name'],
            'name_en': info['name_en'],
            'city': info['city'],
            'city_en': info['city_en'],
        })
    return result


def search_sudan_domestic(origin: str, destination: str, departure_date: str,
                           adults: int = 1, children: int = 0,
                           cabin_class: str = 'economy') -> list:
    """
    Main entry point.  Returns a list of flight offer dicts compatible
    with the existing Duffel/mock offer format used in views.py.

    Strategy:
      1. Try AeroDataBox (RapidAPI) for live departure board data.
      2. Fallback to mock offers built from ROUTE_TABLE.
    """
    origin = origin.upper()
    destination = destination.upper()

    offers = []

    # ── 1. Try live data via AeroDataBox ──────────────────────────────────────
    if RAPIDAPI_KEY:
        try:
            live_offers = _fetch_aerodatabox(origin, destination, departure_date,
                                              adults, children, cabin_class)
            if live_offers:
                offers = live_offers
        except Exception as e:
            print(f"[SudanDomestic] AeroDataBox error: {e}")

    # ── 2. Fallback to mock ───────────────────────────────────────────────────
    if not offers:
        offers = _build_mock_offers(origin, destination, departure_date,
                                    adults, children, cabin_class)

    return offers


# ══════════════════════════════════════════════════════════════════════════════
# AeroDataBox (RapidAPI) integration
# ══════════════════════════════════════════════════════════════════════════════

def _fetch_aerodatabox(origin, destination, departure_date, adults, children, cabin_class):
    """
    Query AeroDataBox airport departures board for `origin` and filter flights
    that arrive at `destination`.
    Returns a list of offer dicts, or [] if nothing found.
    """
    headers = {
        'X-RapidAPI-Key': RAPIDAPI_KEY,
        'X-RapidAPI-Host': AERODATABOX_HOST,
    }

    # Build a 24-hour window for the departure date
    from_time = f"{departure_date}T00:00"
    to_time   = f"{departure_date}T23:59"

    url = f"{AERODATABOX_BASE}/flights/airports/iata/{origin}/{from_time}/{to_time}"
    params = {
        'withLeg': 'true',
        'direction': 'Departure',
        'withCancelled': 'false',
        'withCodeshared': 'true',
        'withCargo': 'false',
        'withPrivate': 'false',
    }

    resp = requests.get(url, headers=headers, params=params, timeout=12)
    if resp.status_code != 200:
        print(f"[SudanDomestic] AeroDataBox HTTP {resp.status_code}: {resp.text[:200]}")
        return []

    data = resp.json()
    departures = data.get('departures', [])

    offers = []
    for flight in departures:
        arr_iata = (flight.get('arrival', {}).get('airport', {}).get('iata') or '').upper()
        if arr_iata != destination:
            continue

        airline_name = flight.get('airline', {}).get('name', 'Sudan Airways')
        airline_iata = flight.get('airline', {}).get('iata', 'SD')
        flight_num   = flight.get('number', f'{airline_iata}001')
        dep_time     = flight.get('departure', {}).get('scheduledTime', {}).get('local', f'{departure_date}T08:00')
        arr_time     = flight.get('arrival',   {}).get('scheduledTime', {}).get('local', f'{departure_date}T09:30')

        # Build a price estimate from ROUTE_TABLE or default
        route_info = _get_route_info(origin, destination)
        base_price = float(route_info['price']) if route_info else 100.0
        total = _calc_total(base_price, adults, children)
        tax   = round(total * 0.12, 2)

        offers.append(_build_offer(
            origin=origin, destination=destination,
            dep_time=dep_time, arr_time=arr_time,
            airline_iata=airline_iata, airline_name=airline_name,
            flight_num=flight_num, duration=route_info.get('duration', 'PT1H00M') if route_info else 'PT1H00M',
            total=total, tax=tax, adults=adults, children=children, cabin_class=cabin_class,
            source='live',
        ))

    return offers


# ══════════════════════════════════════════════════════════════════════════════
# Mock offer builder
# ══════════════════════════════════════════════════════════════════════════════

def _build_mock_offers(origin, destination, departure_date, adults, children, cabin_class):
    """Build realistic mock offers from ROUTE_TABLE for the given route."""
    route_info = _get_route_info(origin, destination)
    if not route_info:
        return []

    offers = []
    for airline_iata in route_info['airlines']:
        airline = AIRLINE_INFO.get(airline_iata, AIRLINE_INFO['SD'])
        flight_num = route_info['flight_nums'].get(airline_iata, f'{airline_iata}100')

        # Adjust departure time per airline (stagger by 2 hours if multiple airlines)
        dep_h, dep_m = route_info['dep'].split(':')
        offset = route_info['airlines'].index(airline_iata) * 2
        dep_hour = (int(dep_h) + offset) % 24
        dep_time = f"{departure_date}T{dep_hour:02d}:{dep_m}:00"

        # Calculate arrival from duration
        arr_time = _add_duration(dep_time, route_info['duration'])

        base_price = float(route_info['price'])
        # Cabin class price multiplier
        cabin_mult = {'economy': 1.0, 'premium_economy': 1.6, 'business': 2.5, 'first': 3.5}
        base_price = round(base_price * cabin_mult.get(cabin_class, 1.0), 2)

        total = _calc_total(base_price, adults, children)
        tax   = round(total * 0.12, 2)

        offers.append(_build_offer(
            origin=origin, destination=destination,
            dep_time=dep_time, arr_time=arr_time,
            airline_iata=airline_iata, airline_name=airline['name'],
            flight_num=flight_num, duration=route_info['duration'],
            total=total, tax=tax, adults=adults, children=children, cabin_class=cabin_class,
            source='mock',
        ))

    return offers


# ══════════════════════════════════════════════════════════════════════════════
# Shared offer builder
# ══════════════════════════════════════════════════════════════════════════════

def _build_offer(origin, destination, dep_time, arr_time,
                 airline_iata, airline_name, flight_num, duration,
                 total, tax, adults, children, cabin_class, source='mock'):
    """Build one offer dict in the Duffel-compatible format used by views.py."""
    ori_info = SUDAN_AIRPORTS.get(origin,      {'name': origin,      'city': origin,      'name_en': origin,      'city_en': origin})
    dst_info = SUDAN_AIRPORTS.get(destination, {'name': destination, 'city': destination, 'name_en': destination, 'city_en': destination})

    adult_pp  = round(total / max(adults + children * 0.75, 1), 2)
    child_pp  = round(adult_pp * 0.75, 2)

    pax_list = [{'id': f"pas_adult_{i}",  'type': 'adult'} for i in range(adults)]
    pax_list += [{'id': f"pas_child_{i}", 'type': 'child'} for i in range(children)]

    segment = {
        'id': f"seg_{str(uuid.uuid4())[:8]}",
        'origin': {
            'name': ori_info['name_en'],
            'iata_code': origin,
            'city_name': ori_info['city_en'],
            'name_ar': ori_info['name'],
            'city_name_ar': ori_info['city'],
        },
        'destination': {
            'name': dst_info['name_en'],
            'iata_code': destination,
            'city_name': dst_info['city_en'],
            'name_ar': dst_info['name'],
            'city_name_ar': dst_info['city'],
        },
        'departing_at': dep_time,
        'arriving_at':  arr_time,
        'duration':     duration,
        'marketing_carrier': {'name': airline_name, 'iata_code': airline_iata},
        'operating_carrier': {'name': airline_name, 'iata_code': airline_iata},
        'marketing_carrier_flight_number': flight_num,
        'passengers': [{
            'cabin_class': cabin_class,
            'cabin_class_marketing_name': cabin_class,
            'baggages': [
                {'type': 'checked', 'quantity': 1, 'weight': '20', 'weight_unit': 'kg'},
                {'type': 'carry_on','quantity': 1, 'weight': '7',  'weight_unit': 'kg'},
            ],
        }],
    }

    flight_slice = {
        'id': f"sli_{str(uuid.uuid4())[:8]}",
        'origin': segment['origin'],
        'destination': segment['destination'],
        'departure_date': dep_time[:10],
        'duration': duration,
        'duration_fmt': _fmt_duration(duration),
        'segments': [segment],
    }

    refund_penalty  = round(total * 0.15, 2)
    change_penalty  = round(total * 0.10, 2)

    return {
        'id': f"off_sudan_{str(uuid.uuid4())[:8]}",
        'total_amount': f"{total:.2f}",
        'total_currency': 'USD',
        'tax_amount': f"{tax:.2f}",
        'adult_per_person': f"{adult_pp:.2f}",
        'child_per_person': f"{child_pp:.2f}",
        'owner': {'name': airline_name, 'iata_code': airline_iata},
        'passengers': pax_list,
        'slices': [flight_slice],
        'source': source,            # 'live' or 'mock'
        'is_sudan_domestic': True,   # flag for template
        'conditions': {
            'refund_before_departure': {
                'allowed': True,
                'penalty_amount': f"{refund_penalty:.2f}",
                'penalty_currency': 'USD',
            },
            'change_before_departure': {
                'allowed': True,
                'penalty_amount': f"{change_penalty:.2f}",
                'penalty_currency': 'USD',
            },
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _get_route_info(origin, destination):
    """Look up route in ROUTE_TABLE in both directions."""
    key_fwd = f"{origin}-{destination}"
    key_rev = f"{destination}-{origin}"
    return ROUTE_TABLE.get(key_fwd) or ROUTE_TABLE.get(key_rev)


def _calc_total(base_price, adults, children):
    return round(base_price * adults + base_price * 0.75 * children, 2)


def _fmt_duration(iso_duration):
    """Convert PT1H30M → '1h 30min'."""
    import re
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', iso_duration or '')
    if not m:
        return iso_duration
    h, mins = int(m.group(1) or 0), int(m.group(2) or 0)
    parts = []
    if h:
        parts.append(f"{h}h")
    if mins:
        parts.append(f"{mins}min")
    return ' '.join(parts) or '-'


def _add_duration(dep_time_str, iso_duration):
    """Add ISO 8601 duration to a datetime string and return the result."""
    import re
    from datetime import datetime, timedelta
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?', iso_duration or '')
    hours   = int(m.group(1) or 0) if m else 0
    minutes = int(m.group(2) or 0) if m else 0
    try:
        fmt = '%Y-%m-%dT%H:%M:%S' if len(dep_time_str) > 16 else '%Y-%m-%dT%H:%M'
        dt = datetime.strptime(dep_time_str, fmt)
        dt += timedelta(hours=hours, minutes=minutes)
        return dt.strftime('%Y-%m-%dT%H:%M:%S')
    except Exception:
        return dep_time_str
