"""
Sudan Ferry Service
====================
Sea trips from Sudan (Port Sudan) to Saudi Arabia (Jeddah) and back.

Operating companies:
  - Nile Valley Transport Company (شركة وادي النيل للنقل)
  - Bawabat Al-Jazeera Shipping   (شركة بوابة الجزيرة)
  - Makkah Shipping                (شركة مكة للشحن)

Route: Port Sudan (PZU) ↔ Jeddah Islamic Port (JED)
Distance: ~800 km  |  Duration: ~36–40 hours

Cabin classes:
  economy   — shared dormitory berths
  standard  — shared 4-berth cabin
  first     — private 2-berth cabin
  vip       — private suite
"""

import uuid
from django.conf import settings

# ── Ferry companies ────────────────────────────────────────────────────────────
FERRY_COMPANIES = [
    {
        'id': 'nvc',
        'name': 'Nile Valley Transport',
        'name_ar': 'شركة وادي النيل للنقل',
        'color': '#003087',
        'logo': '⛴',
        'vessel': 'MV Nile Pioneer',
    },
    {
        'id': 'bjsh',
        'name': "Bawabat Al-Jazeera Shipping",
        'name_ar': 'شركة بوابة الجزيرة',
        'color': '#007229',
        'logo': '🚢',
        'vessel': 'MV Al-Jazeera Star',
    },
    {
        'id': 'makkah',
        'name': 'Makkah Shipping',
        'name_ar': 'شركة مكة للشحن والنقل',
        'color': '#c8102e',
        'logo': '⛵',
        'vessel': 'MV Makkah Express',
    },
]

# ── Ports ──────────────────────────────────────────────────────────────────────
PORTS = {
    'PZU': {
        'name': 'ميناء بورتسودان',
        'name_en': 'Port Sudan Seaport',
        'city': 'بورتسودان',
        'city_en': 'Port Sudan',
        'country': 'السودان',
        'code': 'PZU',
    },
    'JED': {
        'name': 'ميناء جدة الإسلامي',
        'name_en': 'Jeddah Islamic Port',
        'city': 'جدة',
        'city_en': 'Jeddah',
        'country': 'المملكة العربية السعودية',
        'code': 'JED',
    },
}

# ── Cabin classes & pricing (USD, per person, one-way) ────────────────────────
CABIN_PRICES = {
    'economy':  {'price': 80,  'name_ar': 'اقتصادي (بدون كابينة)',   'name_en': 'Economy (Open Deck)', 'capacity': '— مقعد مشترك'},
    'standard': {'price': 130, 'name_ar': 'درجة عادية (4 أشخاص)',    'name_en': 'Standard (4-berth)',  'capacity': '4 في الكابينة'},
    'first':    {'price': 200, 'name_ar': 'درجة أولى (كابينة خاصة)', 'name_en': 'First (2-berth)',     'capacity': '2 في الكابينة'},
    'vip':      {'price': 320, 'name_ar': 'VIP (جناح فاخر)',          'name_en': 'VIP Suite',           'capacity': 'كابينة خاصة'},
}

# ── Fixed schedule: Tue & Sat from each direction ─────────────────────────────
SCHEDULE_DAYS = {
    'PZU-JED': {'days': [1, 5], 'dep': '20:00', 'arr': '+1 08:00', 'duration': '36h'},  # Tue & Sat
    'JED-PZU': {'days': [3, 0], 'dep': '22:00', 'arr': '+1 10:00', 'duration': '36h'},  # Mon & Thu
}


def get_ferry_ports():
    """Return list of all ferry port dicts."""
    return list(PORTS.values())


def search_ferry(origin: str, destination: str, departure_date: str,
                 adults: int = 1, children: int = 0,
                 cabin_class: str = 'economy') -> list:
    """
    Return a list of ferry trip offers for the given route and date.
    Each offer is compatible with the same display format used by flight results.
    """
    origin      = origin.upper()
    destination = destination.upper()

    route_key = f"{origin}-{destination}"
    if route_key not in SCHEDULE_DAYS:
        # Try reverse
        rev = f"{destination}-{origin}"
        if rev in SCHEDULE_DAYS:
            origin, destination = destination, origin
            route_key = rev
        else:
            return []

    schedule = SCHEDULE_DAYS[route_key]
    cabin    = CABIN_PRICES.get(cabin_class, CABIN_PRICES['economy'])
    base     = float(cabin['price'])
    total    = round(base * adults + base * 0.75 * children, 2)
    tax      = round(total * 0.05, 2)
    adult_pp = base
    child_pp = round(base * 0.75, 2)

    ori_info = PORTS.get(origin,      list(PORTS.values())[0])
    dst_info = PORTS.get(destination, list(PORTS.values())[1])

    offers = []
    for company in FERRY_COMPANIES:
        offer_id = f"off_ferry_{company['id']}_{str(uuid.uuid4())[:8]}"
        dep_time = f"{departure_date}T{schedule['dep']}:00"
        arr_day  = _next_day(departure_date) if schedule['arr'].startswith('+1') else departure_date
        arr_time = f"{arr_day}T{schedule['arr'].replace('+1 ', '')}:00"

        pax_list = [{'id': f"pas_adult_{i}", 'type': 'adult'} for i in range(adults)]
        pax_list += [{'id': f"pas_child_{i}", 'type': 'child'} for i in range(children)]

        segment = {
            'id': f"seg_{str(uuid.uuid4())[:8]}",
            'origin': {
                'name':        ori_info['name_en'],
                'name_ar':     ori_info['name'],
                'iata_code':   origin,
                'city_name':   ori_info['city_en'],
                'city_name_ar':ori_info['city'],
            },
            'destination': {
                'name':        dst_info['name_en'],
                'name_ar':     dst_info['name'],
                'iata_code':   destination,
                'city_name':   dst_info['city_en'],
                'city_name_ar':dst_info['city'],
            },
            'departing_at': dep_time,
            'arriving_at':  arr_time,
            'duration':     f"PT{schedule['duration'].replace('h', 'H')}",
            'vessel':       company['vessel'],
            'cabin_class':  cabin_class,
            'cabin_name_ar':cabin['name_ar'],
            'marketing_carrier': {
                'name':      company['name'],
                'name_ar':   company['name_ar'],
                'iata_code': company['id'].upper(),
                'logo':      company['logo'],
            },
            'operating_carrier': {
                'name':      company['name'],
                'iata_code': company['id'].upper(),
            },
            'marketing_carrier_flight_number': '',
            'passengers': [{
                'cabin_class': cabin_class,
                'cabin_class_marketing_name': cabin['name_ar'],
                'baggages': [
                    {'type': 'checked', 'quantity': 2, 'weight': '30', 'weight_unit': 'kg'},
                ],
                'meal': 'وجبات على متن السفينة',
            }],
        }

        trip_slice = {
            'id':             f"sli_{str(uuid.uuid4())[:8]}",
            'origin':         segment['origin'],
            'destination':    segment['destination'],
            'departure_date': departure_date,
            'duration':       segment['duration'],
            'duration_fmt':   schedule['duration'],
            'segments':       [segment],
        }

        offers.append({
            'id':              offer_id,
            'total_amount':    f"{total:.2f}",
            'total_currency':  'USD',
            'tax_amount':      f"{tax:.2f}",
            'adult_per_person':f"{adult_pp:.2f}",
            'child_per_person':f"{child_pp:.2f}",
            'owner':           {'name': company['name'], 'name_ar': company['name_ar'], 'iata_code': company['id'].upper()},
            'passengers':      pax_list,
            'slices':          [trip_slice],
            'is_ferry':        True,
            'is_sudan_domestic': False,
            'ferry_company':   company,
            'cabin_info':      cabin,
            'conditions': {
                'refund_before_departure': {'allowed': True,  'penalty_amount': f"{round(total*0.2,2):.2f}", 'penalty_currency': 'USD'},
                'change_before_departure': {'allowed': True,  'penalty_amount': f"{round(total*0.1,2):.2f}", 'penalty_currency': 'USD'},
            },
        })

    return offers


def _next_day(date_str: str) -> str:
    from datetime import datetime, timedelta
    try:
        d = datetime.strptime(date_str, '%Y-%m-%d') + timedelta(days=1)
        return d.strftime('%Y-%m-%d')
    except Exception:
        return date_str
