import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .services import duffel_service
from .services import agoda_service
from .models import Booking, Passenger, HotelBooking


# ---------------------------------------------------------------------------
# Home – Search form
# ---------------------------------------------------------------------------
AIRLINES_LIST = [
    {'name': 'EgyptAir',         'iata': 'MS', 'flag': '🇪🇬', 'color': '#c8102e', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/MS.png'},
    {'name': 'Air Algérie',      'iata': 'AH', 'flag': '🇩🇿', 'color': '#006233', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/AH.png'},
    {'name': 'Turkish Airlines', 'iata': 'TK', 'flag': '🇹🇷', 'color': '#c8102e', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/TK.png'},
    {'name': 'Emirates',         'iata': 'EK', 'flag': '🇦🇪', 'color': '#c8102e', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/EK.png'},
    {'name': 'Qatar Airways',    'iata': 'QR', 'flag': '🇶🇦', 'color': '#5c0632', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/QR.png'},
    {'name': 'Air France',       'iata': 'AF', 'flag': '🇫🇷', 'color': '#002395', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/AF.png'},
    {'name': 'Lufthansa',        'iata': 'LH', 'flag': '🇩🇪', 'color': '#05164d', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/LH.png'},
    {'name': 'British Airways',  'iata': 'BA', 'flag': '🇬🇧', 'color': '#075aaa', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/BA.png'},
    {'name': 'Royal Air Maroc',  'iata': 'AT', 'flag': '🇲🇦', 'color': '#c1272d', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/AT.png'},
    {'name': 'Tunisair',         'iata': 'TU', 'flag': '🇹🇳', 'color': '#e70013', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/TU.png'},
    {'name': 'flynas',           'iata': 'XY', 'flag': '🇸🇦', 'color': '#ff6600', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/XY.png'},
    {'name': 'Sudan Airways',    'iata': 'SD', 'flag': '🇸🇩', 'color': '#007229', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/SD.png'},
    {'name': 'Etihad Airways',   'iata': 'EY', 'flag': '🇦🇪', 'color': '#b5975a', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/EY.png'},
    {'name': 'Saudi Airlines',   'iata': 'SV', 'flag': '🇸🇦', 'color': '#006747', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/SV.png'},
    {'name': 'Ethiopian',        'iata': 'ET', 'flag': '🇪🇹', 'color': '#009a44', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/ET.png'},
    {'name': 'Kenya Airways',    'iata': 'KQ', 'flag': '🇰🇪', 'color': '#c8102e', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/KQ.png'},
    {'name': 'KLM',              'iata': 'KL', 'flag': '🇳🇱', 'color': '#00a1de', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/KL.png'},
    {'name': 'Swiss',            'iata': 'LX', 'flag': '🇨🇭', 'color': '#e4002b', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/LX.png'},
    {'name': 'Iberia',           'iata': 'IB', 'flag': '🇪🇸', 'color': '#c60b1e', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/IB.png'},
    {'name': 'ITA Airways',      'iata': 'AZ', 'flag': '🇮🇹', 'color': '#009246', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/AZ.png'},
    {'name': 'Oman Air',         'iata': 'WY', 'flag': '🇴🇲', 'color': '#db0011', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/WY.png'},
    {'name': 'Gulf Air',         'iata': 'GF', 'flag': '🇧🇭', 'color': '#b5002e', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/GF.png'},
    {'name': 'flydubai',         'iata': 'FZ', 'flag': '🇦🇪', 'color': '#e40521', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/FZ.png'},
    {'name': 'Air Arabia',       'iata': 'G9', 'flag': '🇦🇪', 'color': '#e40521', 'logo': 'https://www.gstatic.com/flights/airline_logos/70px/G9.png'},
]

DESTINATIONS_LIST = [
    {'iata': 'CAI', 'name_ar': _('القاهرة'),  'badge': _('🇪🇬 مصر'),             'desc': _('CAI · أهرامات الجيزة'),    'image': 'https://images.unsplash.com/photo-1553913861-c0fddf2619ee?w=600&h=300&fit=crop&q=80'},
    {'iata': 'CDG', 'name_ar': _('باريس'),    'badge': _('🇫🇷 فرنسا'),           'desc': _('CDG · برج إيفل'),          'image': 'https://images.unsplash.com/photo-1499856871958-5b9627545d1a?w=600&h=300&fit=crop&q=80'},
    {'iata': 'DXB', 'name_ar': _('دبي'),      'badge': _('🇦🇪 الإمارات'),        'desc': _('DXB · برج خليفة'),         'image': 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=600&h=300&fit=crop&q=80'},
    {'iata': 'IST', 'name_ar': _('إسطنبول'),  'badge': _('🇹🇷 تركيا'),           'desc': _('IST · المسجد الأزرق'),     'image': 'https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?w=600&h=300&fit=crop&q=80'},
    {'iata': 'LHR', 'name_ar': _('لندن'),     'badge': _('🇬🇧 المملكة المتحدة'), 'desc': _('LHR · بيغ بن'),            'image': 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=600&h=300&fit=crop&q=80'},
    {'iata': 'FCO', 'name_ar': _('روما'),     'badge': _('🇮🇹 إيطاليا'),         'desc': _('FCO · الكولوسيوم'),        'image': 'https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=600&h=300&fit=crop&q=80'},
    {'iata': 'DOH', 'name_ar': _('الدوحة'),   'badge': _('🇶🇦 قطر'),             'desc': _('DOH · أفق المدينة'),       'image': 'https://images.unsplash.com/photo-1584551246679-0daf3d275d0f?w=600&h=300&fit=crop&q=80'},
    {'iata': 'MAD', 'name_ar': _('مدريد'),    'badge': _('🇪🇸 إسبانيا'),         'desc': _('MAD · القصر الملكي'),      'image': 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=600&h=300&fit=crop&q=80'},
    {'iata': 'CMN', 'name_ar': _('مراكش'),    'badge': _('🇲🇦 المغرب'),          'desc': _('CMN · المدينة العتيقة'),   'image': 'https://images.unsplash.com/photo-1539020140153-e479b8f22986?w=600&h=300&fit=crop&q=80'},
    {'iata': 'JFK', 'name_ar': _('نيويورك'),  'badge': _('🇺🇸 الولايات المتحدة'),'desc': _('JFK · مانهاتن'),           'image': 'https://images.unsplash.com/photo-1490644658840-3f2e3f8c5625?w=600&h=300&fit=crop&q=80'},
    {'iata': 'NRT', 'name_ar': _('طوكيو'),    'badge': _('🇯🇵 اليابان'),         'desc': _('NRT · برج طوكيو'),         'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&h=300&fit=crop&q=80'},
    {'iata': 'BCN', 'name_ar': _('برشلونة'),  'badge': _('🇪🇸 إسبانيا'),         'desc': _('BCN · ساغرادا فاميليا'),   'image': 'https://images.unsplash.com/photo-1511527661048-7fe73d85e9a4?w=600&h=300&fit=crop&q=80'},
    {'iata': 'AMS', 'name_ar': _('أمستردام'), 'badge': _('🇳🇱 هولندا'),          'desc': _('AMS · القنوات التاريخية'), 'image': 'https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=600&h=300&fit=crop&q=80'},
    {'iata': 'RUH', 'name_ar': _('الرياض'),   'badge': _('🇸🇦 السعودية'),        'desc': _('RUH · المملكة العربية'),   'image': 'https://images.unsplash.com/photo-1586724237569-f3d0c1dee8c6?w=600&h=300&fit=crop&q=80'},
    {'iata': 'ADD', 'name_ar': _('أديس أبابا'),'badge': _('🇪🇹 إثيوبيا'),         'desc': _('ADD · القلب الأفريقي'),    'image': 'https://images.unsplash.com/photo-1523805009345-7448845a9e53?w=600&h=300&fit=crop&q=80'},
    {'iata': 'KWI', 'name_ar': _('الكويت'),   'badge': _('🇰🇼 الكويت'),          'desc': _('KWI · أبراج الكويت'),      'image': 'https://images.unsplash.com/photo-1570735016541-36e4ac955b9b?w=600&h=300&fit=crop&q=80'},
    {'iata': 'SIN', 'name_ar': _('سنغافورة'), 'badge': _('🇸🇬 سنغافورة'),        'desc': _('SIN · مارينا باي'),        'image': 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=600&h=300&fit=crop&q=80'},
    {'iata': 'KUL', 'name_ar': _('كوالالمبور'),'badge': _('🇲🇾 ماليزيا'),         'desc': _('KUL · برجا بتروناس'),      'image': 'https://images.unsplash.com/photo-1596422846543-75c6fc197f0a?w=600&h=300&fit=crop&q=80'},
    {'iata': 'BKK', 'name_ar': _('بانكوك'),   'badge': _('🇹🇭 تايلاند'),         'desc': _('BKK · وات أرون'),          'image': 'https://images.unsplash.com/photo-1508009603885-247a597a1599?w=600&h=300&fit=crop&q=80'},
    {'iata': 'JED', 'name_ar': _('جدة'),      'badge': _('🇸🇦 السعودية'),        'desc': _('JED · نافورة الملك فهد'),  'image': 'https://images.unsplash.com/photo-1590050752112-9c8e547051f6?w=600&h=300&fit=crop&q=80'},
    {'iata': 'AMM', 'name_ar': _('عمّان'),    'badge': _('🇯🇴 الأردن'),          'desc': _('AMM · المدرج الروماني'),   'image': 'https://images.unsplash.com/photo-1588693959821-b0db4dece907?w=600&h=300&fit=crop&q=80'},
]

def apply_flight_markup(offer):
    original_str = str(offer.get('total_amount', '0'))
    original_price = float(original_str)
    markup = original_price * 0.10
    new_price = original_price + markup
    
    # Store the exact verbatim string for backend booking (Duffel's payment validation is strictly typed and can 500 on altered decimals)
    offer['custom_original_amount'] = original_str
    offer['custom_markup_amount'] = f"{markup:.2f}"
    
    # Overwrite total_amount to show customer the higher fee
    offer['total_amount'] = f"{new_price:.2f}"
    return offer

def home(request):
    return render(request, 'vols/home.html', {
        'airlines_list': AIRLINES_LIST,
        'destinations_list': DESTINATIONS_LIST
    })

def about_us(request):
    return render(request, 'vols/about_us.html')

def services(request):
    return render(request, 'vols/services.html')

def contact(request):
    return render(request, 'vols/contact.html')


# ---------------------------------------------------------------------------
# Auth — Signup / Login / Logout
# ---------------------------------------------------------------------------

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('vols:home')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.first_name = request.POST.get('first_name', '')
        user.last_name  = request.POST.get('last_name', '')
        user.email      = request.POST.get('email', '')
        user.is_active  = False
        user.save()
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        request.session['registration_otp'] = otp
        request.session['registration_user_id'] = user.id
        
        # Send Email
        subject = 'تفعيل حسابك - وكالة أبو منية'
        message = f'مرحباً {user.first_name or user.username}،\n\nرمز التفعيل الخاص بك هو: {otp}\n\nشكراً لتسجيلك معنا!'
        try:
            send_mail(subject, message, getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@abomonya.com'), [user.email], fail_silently=False)
        except Exception as e:
            print(f"Error sending email: {e}")
            
        messages.info(request, 'تم إرسال رمز التفعيل إلى بريدك الإلكتروني. يرجى إدخاله أدناه.')
        return redirect('vols:otp_verify')
    return render(request, 'vols/signup.html', {'form': form})


def otp_verify_view(request):
    if request.user.is_authenticated:
        return redirect('vols:home')
    
    user_id = request.session.get('registration_user_id')
    stored_otp = request.session.get('registration_otp')
    
    if not user_id or not stored_otp:
        messages.error(request, 'انتهت صلاحية جلسة التسجيل. يرجى المحاولة مرة أخرى.')
        return redirect('vols:signup')
        
    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        if entered_otp == stored_otp:
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                user.is_active = True
                user.save()
                auth_login(request, user)
                
                # Clear session keys
                del request.session['registration_otp']
                del request.session['registration_user_id']
                
                messages.success(request, 'تم تفعيل الحساب بنجاح! مرحباً بك.')
                return redirect('vols:home')
            except User.DoesNotExist:
                messages.error(request, 'حدث خطأ. المستخدم غير موجود.')
                return redirect('vols:signup')
        else:
            messages.error(request, 'رمز التفعيل غير صحيح. يرجى المحاولة مرة أخرى.')
            
    return render(request, 'vols/otp_verify.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('vols:home')
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        auth_login(request, user)
        messages.success(request, f'أهلاً بعودتك، {user.first_name or user.username}!')
        return redirect(request.POST.get('next') or 'vols:home')
    return render(request, 'vols/login.html', {'form': form, 'next': request.GET.get('next', '')})


def logout_view(request):
    auth_logout(request)
    messages.info(request, 'تم تسجيل خروجك بنجاح.')
    return redirect('vols:home')



# ---------------------------------------------------------------------------
# API - Places (City / Airport Auto-complete)
# ---------------------------------------------------------------------------

# Common Arabic -> English city/airport name map for Duffel lookup
ARABIC_CITY_MAP = {
    'الجزائر': 'Algiers', 'الجزائر العاصمة': 'Algiers',
    'مرسيليا': 'Marseille', 'باريس': 'Paris',
    'لندن': 'London', 'روما': 'Rome', 'ميلانو': 'Milan',
    'برشلونة': 'Barcelona', 'مدريد': 'Madrid',
    'إسطنبول': 'Istanbul', 'أنقرة': 'Ankara',
    'دبي': 'Dubai', 'أبوظبي': 'Abu Dhabi',
    'دوحة': 'Doha', 'مسقط': 'Muscat',
    'الرياض': 'Riyadh', 'جدة': 'Jeddah', 'الدمام': 'Dammam',
    'بيروت': 'Beirut', 'عمان': 'Amman', 'بغداد': 'Baghdad',
    'القاهرة': 'Cairo', 'الإسكندرية': 'Alexandria',
    'تونس': 'Tunis', 'الدار البيضاء': 'Casablanca',
    'الرباط': 'Rabat', 'مراكش': 'Marrakech', 'فاس': 'Fes',
    'خرطوم': 'Khartoum', 'بنغازي': 'Benghazi',
    'عدن': 'Aden', 'صنعاء': 'Sanaa',
    'تريبولي': 'Tripoli', 'فرانكفورت': 'Frankfurt',
    'أمستردام': 'Amsterdam', 'برلين': 'Berlin',
    'ميونخ': 'Munich', 'جنيف': 'Geneva',
    'ظبي': 'Abu Dhabi', 'الشارقة': 'Sharjah',
    'الكويت': 'Kuwait City', 'المنامة': 'Manama',
    'نيويورك': 'New York', 'لوس أنجلوس': 'Los Angeles',
    'شيكاغو': 'Chicago', 'طورنتو': 'Toronto',
    'مونتريال': 'Montreal', 'سيدني': 'Sydney',
    'ملبورن': 'Melbourne', 'بانكوك': 'Bangkok',
    'كوالا لمبور': 'Kuala Lumpur', 'سنغافورة': 'Singapore',
    'طهران': 'Tehran', 'كابول': 'Kabul',
    'كراتشي': 'Karachi', 'لاهور': 'Lahore',
    'مومباي': 'Mumbai', 'دلهي': 'Delhi',
    'كوبنهاغن': 'Copenhagen', 'ستوكهولم': 'Stockholm',
    'أثينا': 'Athens', 'براغ': 'Prague',
    'فيينا': 'Vienna', 'بروكسل': 'Brussels',
    'وهران': 'Oran', 'قسنطينة': 'Constantine', 'عنابة': 'Annaba',
    'بجاية': 'Bejaia', 'تلمسان': 'Tlemcen', 'سكيكدة': 'Skikda',
    'باتنة': 'Batna', 'تبسة': 'Tebessa', 'بشار': 'Bechar',
    'غرداية': 'Ghardaia', 'ورقلة': 'Ouargla',
    'تمنراست': 'Tamanrasset', 'إخنوكشن': 'In Amenas',
}

def api_places(request):
    raw_query = request.GET.get('q', '').strip()
    if not raw_query:
        return JsonResponse({'results': []})

    # Try Arabic -> English translation
    translated = ARABIC_CITY_MAP.get(raw_query)
    if not translated:
        # partial match: check if Arabic query starts with a key
        for ar, en in ARABIC_CITY_MAP.items():
            if ar.startswith(raw_query) or raw_query in ar:
                translated = en
                break

    # Search with both queries (translated + original)
    queries = [raw_query]
    if translated and translated.lower() != raw_query.lower():
        queries.insert(0, translated)  # translated first for best results

    seen_ids = set()
    all_results = []
    try:
        for q in queries:
            places = duffel_service.search_places(q)
            for p in places:
                if p.get('type') not in ['airport', 'city']:
                    continue
                pid = p.get('id')
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)
                iata = p.get('iata_code') or p.get('iata_city_code', '')
                all_results.append({
                    'id': pid,
                    'name': p.get('name'),
                    'type': p.get('type'),
                    'iata_code': iata,
                    'city_name': p.get('city_name', ''),
                    # Reverse-lookup Arabic name for display
                    'arabic_name': next((ar for ar, en in ARABIC_CITY_MAP.items()
                                        if en.lower() in [
                                            (p.get('name') or '').lower(),
                                            (p.get('city_name') or '').lower()
                                        ]), ''),
                })
        return JsonResponse({'results': all_results[:12]})
    except Exception as e:
        print(f"Places API Error: {e}")
        return JsonResponse({'results': []})


# ---------------------------------------------------------------------------
# Search – Call Duffel and display offers
# ---------------------------------------------------------------------------

def search_results(request):
    if request.method == 'POST':
        trip_type = request.POST.get('trip_type', 'oneway')
        passengers = request.POST.get('passengers', 1)
        cabin_class = request.POST.get('cabin_class', 'economy')

        slices = []

        if trip_type == 'oneway':
            slices.append({
                'origin': request.POST.get('origin_0', ''),
                'destination': request.POST.get('destination_0', ''),
                'departure_date': request.POST.get('departure_date_0', '')
            })
        
        elif trip_type == 'roundtrip':
            origin = request.POST.get('origin_0', '')
            destination = request.POST.get('destination_0', '')
            slices.append({
                'origin': origin,
                'destination': destination,
                'departure_date': request.POST.get('departure_date_0', '')
            })
            slices.append({
                'origin': destination,
                'destination': origin,
                'departure_date': request.POST.get('return_date', '')
            })
            
        elif trip_type == 'multicity':
            i = 0
            while True:
                orig = request.POST.get(f'origin_{i}')
                dest = request.POST.get(f'destination_{i}')
                date = request.POST.get(f'departure_date_{i}')
                if not orig or not dest or not date:
                    break
                slices.append({
                    'origin': orig,
                    'destination': dest,
                    'departure_date': date
                })
                i += 1

        # Ensure we have valid slices
        slices = [s for s in slices if s['origin'] and s['destination'] and s['departure_date']]
        
        if not slices:
            messages.error(request, "Veuillez fournir des informations de vol valides.")
            return redirect('vols:home')
            
        # Clean IATA codes (extract the 3-letter uppercase code)
        import re
        for s in slices:
            orig_match = re.search(r'\b([A-Z]{3})\b', s['origin'])
            dest_match = re.search(r'\b([A-Z]{3})\b', s['destination'])
            if orig_match:
                s['origin'] = orig_match.group(1)
            if dest_match:
                s['destination'] = dest_match.group(1)

        # Persist search params in session for re-use
        request.session['search'] = {
            'trip_type': trip_type,
            'slices': slices,
            'passengers': passengers,
            'cabin_class': cabin_class,
            'add_hotel': request.POST.get('add_hotel') == 'yes',
        }

        try:
            offers = duffel_service.search_flights(slices, passengers, cabin_class)
            # Enrich offers with formatted duration and 10% markup
            for offer in offers:
                apply_flight_markup(offer)
                for sl in offer.get('slices', []):
                    sl['duration_fmt'] = duffel_service.format_duration(sl.get('duration'))
            
            # --- Prioritize Arabic Airlines ---
            # List of major Arabic airlines IATA codes
            arabic_airlines = {
                'EK', # Emirates
                'QR', # Qatar Airways
                'EY', # Etihad Airways
                'SV', # Saudia
                'WY', # Oman Air
                'RJ', # Royal Jordanian
                'GF', # Gulf Air
                'KU', # Kuwait Airways
                'ME', # Middle East Airlines (MEA)
                'MS', # EgyptAir
                'FZ', # flydubai
                'G9', # Air Arabia
            }

            def sort_offers(o):
                # Check if any segment is operated by an Arabic airline
                has_arabic_airline = False
                for sl in o.get('slices', []):
                    for seg in sl.get('segments', []):
                        carrier_code = seg.get('operating_carrier', {}).get('iata_code') or seg.get('marketing_carrier', {}).get('iata_code')
                        if carrier_code in arabic_airlines:
                            has_arabic_airline = True
                            break
                    if has_arabic_airline:
                        break
                
                price = float(o.get('total_amount', 999999))
                # Sort criteria: 
                # 1. Arabic airlines first (0 = True, 1 = False)
                # 2. Then by cheapest price
                return (0 if has_arabic_airline else 1, price)

            # Sort the offers using our custom logic
            offers.sort(key=sort_offers)
            # -----------------------------------
            
            # Extract unique airlines for filtering
            unique_airlines = set()
            for offer in offers:
                for sl in offer.get('slices', []):
                    for seg in sl.get('segments', []):
                        airline_name = seg.get('marketing_carrier', {}).get('name')
                        if airline_name:
                            unique_airlines.add(airline_name)
            
            unique_airlines = sorted(list(unique_airlines))
            
            # Store offers in session (max 30 to keep session manageable)
            request.session['offers'] = offers[:30]
            
            context = {
                'offers': offers[:30],
                'search': request.session['search'],
                'airlines': unique_airlines,
            }
            return render(request, 'vols/results.html', context)

        except Exception as e:
            messages.error(request, f"Erreur lors de la recherche: {str(e)}")
            return redirect('vols:home')

    return redirect('vols:home')


# ---------------------------------------------------------------------------
# Passenger details form
# ---------------------------------------------------------------------------

def passenger_details(request, offer_id):
    # Try to find offer in session
    offers = request.session.get('offers', [])
    offer = next((o for o in offers if o.get('id') == offer_id), None)
    
    if not offer:
        # Fetch directly from Duffel as fallback
        try:
            offer = duffel_service.get_offer(offer_id)
        except Exception as e:
            messages.error(request, f"Offre introuvable: {str(e)}")
            return redirect('vols:home')

    search = request.session.get('search', {})
    num_passengers = int(search.get('passengers', 1))
    
    context = {
        'offer': offer,
        'offer_json': json.dumps(offer),
        'num_passengers': range(1, num_passengers + 1),
        'search': search,
        'duration_fmt': duffel_service.format_duration(
            offer.get('slices', [{}])[0].get('duration') if offer.get('slices') else ''
        ),
    }
    return render(request, 'vols/passenger_details.html', context)


# ---------------------------------------------------------------------------
# Confirm booking – POST from passenger form
# ---------------------------------------------------------------------------

def confirm_booking(request):
    if request.method != 'POST':
        return redirect('vols:home')

    offer_id = request.POST.get('offer_id')
    offers = request.session.get('offers', [])
    offer = next((o for o in offers if o.get('id') == offer_id), None)

    if not offer:
        try:
            offer = duffel_service.get_offer(offer_id)
            apply_flight_markup(offer)
        except Exception as e:
            messages.error(request, f"Offre introuvable: {str(e)}")
            return redirect('vols:home')

    search = request.session.get('search', {})
    num_passengers = int(search.get('passengers', 1))

    # Build passenger dicts for Duffel
    duffel_passengers = []

    import re
    import datetime
    latin_only = re.compile(r'^[A-Za-z\s]+$')

    for i in range(1, num_passengers + 1):
        first_name = request.POST.get(f'first_name_{i}', '').strip()
        last_name = request.POST.get(f'last_name_{i}', '').strip()
        
        if not latin_only.match(first_name) or not latin_only.match(last_name):
            messages.error(request, f"خطأ: يجب إدخال اسم المسافر {i} بحروف إنجليزية فقط كما في جواز السفر.")
            return redirect('vols:passenger_details', offer_id=offer_id)

        gender = request.POST.get(f'gender_{i}', 'm')
        passenger = {
            'id': offer['passengers'][i - 1]['id'],
            'title': 'mr' if gender == 'm' else 'ms',
            'given_name': first_name,
            'family_name': last_name,
            'born_on': request.POST.get(f'born_on_{i}', ''),
            'gender': gender,
            'email': request.POST.get(f'email_{i}', ''),
            'phone_number': request.POST.get(f'phone_{i}', '') or '+33600000000',
        }
        # Sanitize phone: strip spaces, dashes, parentheses — keep only + and digits
        raw_phone = request.POST.get(f'phone_{i}', '').strip()
        raw_phone = re.sub(r'[\s\-\(\)\.]+', '', raw_phone)  # remove whitespace/dashes/parens
        if not raw_phone.startswith('+'):
            raw_phone = '+' + raw_phone
        # Fallback to a valid default if still invalid (less than 7 digits)
        digits_only = re.sub(r'\D', '', raw_phone)
        if len(digits_only) < 7:
            raw_phone = '+33600000000'
        passenger['phone_number'] = raw_phone
            
        duffel_passengers.append(passenger)

    try:
        original_amount = offer.get('custom_original_amount', offer['total_amount'])
        markup_amount = offer.get('custom_markup_amount', 0)
        total_customer_price = float(offer['total_amount'])

        # Step 1: Book the ticket immediately with Duffel
        order = duffel_service.create_order(offer_id, duffel_passengers, original_amount, offer['total_currency'])

        # Step 2: Save confirmed booking to DB
        first_slice = offer.get('slices', [{}])[0]
        airline_name = first_slice.get('segments', [{}])[0].get('operating_carrier', {}).get('name', 'N/A')
        flight_num = first_slice.get('segments', [{}])[0].get('marketing_carrier_flight_number', '')

        booking = Booking.objects.create(
            duffel_order_id=order.get('id', ''),
            booking_reference=order.get('booking_reference', 'N/A'),
            origin=search.get('slices', [{}])[0].get('origin', ''),
            destination=search.get('slices', [{}])[-1].get('destination', ''),
            departure_date=search.get('slices', [{}])[0].get('departure_date', datetime.date.today()),
            airline=airline_name,
            flight_number=flight_num,
            cabin_class=search.get('cabin_class', ''),
            total_amount=total_customer_price,
            markup_amount=float(markup_amount),
            currency=offer.get('total_currency', 'USD'),
            status='confirmed',
        )

        for p in duffel_passengers:
            Passenger.objects.create(
                booking=booking,
                duffel_passenger_id=p.get('id', ''),
                title=p.get('title', 'mr'),
                first_name=p['given_name'],
                last_name=p['family_name'],
                born_on=p['born_on'],
                gender=p['gender'],
                email=p['email'],
                phone_number=p['phone_number'],
            )

        # Step 3: Redirect to payment choice page (Visa or Bank Transfer)
        return redirect('vols:payment_choice', booking_id=booking.id)

    except Exception as e:
        messages.error(request, f"Erreur lors de la réservation: {str(e)}")
        return redirect('vols:passenger_details', offer_id=offer_id)


def payment_choice(request, booking_id):
    """Show the payment method selection page after a confirmed booking."""
    booking = get_object_or_404(Booking, id=booking_id)
    passengers = booking.passengers.all()
    return render(request, 'vols/payment_choice.html', {
        'booking': booking,
        'passengers': passengers,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    })


def stripe_pay(request, booking_id):
    """Create a Stripe Checkout Session and redirect the user to it."""
    booking = get_object_or_404(Booking, id=booking_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    unit_amount = int(float(booking.total_amount) * 100)
    domain_url = request.build_absolute_uri('/')[:-1]

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': booking.currency.lower(),
                'unit_amount': unit_amount,
                'product_data': {
                    'name': f"تذكرة طيران: {booking.origin} → {booking.destination}",
                    'description': f"{booking.airline} | Ref: {booking.booking_reference}",
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        client_reference_id=str(booking.id),
        success_url=domain_url + reverse('vols:stripe_success') + f"?booking_id={booking.id}",
        cancel_url=domain_url + reverse('vols:payment_choice', args=[booking.id]),
    )
    return redirect(checkout_session.url, code=303)


def stripe_success(request):
    """Called after successful Stripe payment - mark booking as paid."""
    booking_id = request.GET.get('booking_id')
    if booking_id:
        booking = get_object_or_404(Booking, id=booking_id)
        booking.status = 'paid'
        booking.save()
        messages.success(request, "✅ تمت عملية الدفع بنجاح عبر بطاقة Visa!")
        return redirect('vols:confirmation', booking_id=booking.id)
    return redirect('vols:home')


def stripe_cancel(request):
    """Called if user cancels Stripe checkout - redirect back to payment choice."""
    booking_id = request.GET.get('booking_id')
    messages.warning(request, "تم إلغاء عملية الدفع. يمكنك الاختيار مجدداً.")
    if booking_id:
        return redirect('vols:payment_choice', booking_id=booking_id)
    return redirect('vols:home')


# ---------------------------------------------------------------------------
# Booking confirmation page
# ---------------------------------------------------------------------------

def confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    passengers = booking.passengers.all()
    context = {
        'booking': booking,
        'passengers': passengers,
    }
    return render(request, 'vols/confirmation.html', context)



# ---------------------------------------------------------------------------
# My bookings
# ---------------------------------------------------------------------------

def my_bookings(request):
    bookings = Booking.objects.prefetch_related('passengers').all()
    return render(request, 'vols/my_bookings.html', {'bookings': bookings})


# ===========================================================================
# 🏨 HOTELS (AGODA INTEGRATION)
# ===========================================================================

def api_hotel_destinations(request):
    """Autocomplete for hotel destinations (cities)."""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    
    destinations = agoda_service.search_destinations(query)
    
    results = []
    for d in destinations:
        results.append({
            'city_id': d.get('cityId'),
            'city_name': d.get('cityName'),
            'country_name': d.get('countryName', ''),
            'name_ar': d.get('nameAr', '')
        })
        
    return JsonResponse({'results': results})


def hotel_search(request):
    """Handle the hotel search form submission."""
    if request.method != 'POST':
        return redirect('vols:home')
        
    city_id = request.POST.get('hotel_city_id')
    city_name = request.POST.get('hotel_city_name', '')
    check_in = request.POST.get('check_in')
    check_out = request.POST.get('check_out')
    adults = int(request.POST.get('adults', 2))
    rooms = int(request.POST.get('rooms', 1))

    if not city_id or not check_in or not check_out:
        messages.error(request, "Veuillez fournir toutes les informations nécessaires pour la recherche d'hôtel.")
        return redirect('vols:home')

    try:
        hotels = agoda_service.search_hotels(
            city_id=int(city_id),
            check_in=check_in,
            check_out=check_out,
            adults=adults,
            rooms=rooms
        )
        
        # Save search criteria and results in session
        request.session['hotel_search'] = {
            'city_id': city_id,
            'city_name': city_name,
            'check_in': check_in,
            'check_out': check_out,
            'adults': adults,
            'rooms': rooms,
        }
        
        request.session['hotel_results'] = hotels[:50]  # Store up to 50 results
        return redirect('vols:hotel_results')
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la recherche d'hôtels: {str(e)}")
        return redirect('vols:home')


def hotel_results(request):
    """Display the hotel search results."""
    search_crit = request.session.get('hotel_search')
    hotels = request.session.get('hotel_results', [])
    
    if not search_crit:
        return redirect('vols:home')
        
    context = {
        'search': search_crit,
        'hotels': hotels,
    }
    return render(request, 'vols/hotel_results.html', context)


def hotel_detail(request, hotel_id):
    """Show details for a specific hotel, including room options."""
    search_crit = request.session.get('hotel_search')
    if not search_crit:
        messages.warning(request, "Votre session a expiré, veuillez relancer la recherche.")
        return redirect('vols:home')

    try:
        hotel = agoda_service.get_hotel(
            hotel_id=hotel_id,
            check_in=search_crit['check_in'],
            check_out=search_crit['check_out'],
            adults=search_crit['adults'],
            rooms=search_crit['rooms']
        )
        
        context = {
            'search': search_crit,
            'hotel': hotel,
        }
        return render(request, 'vols/hotel_detail.html', context)
        
    except Exception as e:
        messages.error(request, f"Impossible de récupérer les détails de l'hôtel: {e}")
        return redirect('vols:hotel_results')


def hotel_book(request):
    """Process the booking form, save it, and redirect to Agoda."""
    if request.method != 'POST':
        return redirect('vols:home')
        
    hotel_id = int(request.POST.get('hotel_id'))
    hotel_name = request.POST.get('hotel_name')
    room_price = float(request.POST.get('room_price', 0))
    markup_amount = float(request.POST.get('markup_amount', 0))
    customer_price = float(request.POST.get('customer_price', 0))
    
    guest_name = request.POST.get('guest_name')
    guest_email = request.POST.get('guest_email', '')
    guest_phone = request.POST.get('guest_phone', '')
    
    search_crit = request.session.get('hotel_search', {})
    check_in = search_crit.get('check_in')
    check_out = search_crit.get('check_out')
    city_name = search_crit.get('city_name', '')
    nights = 1  # Calculated in service, fallback to 1
    
    from datetime import datetime
    try:
        ci = datetime.strptime(check_in, '%Y-%m-%d')
        co = datetime.strptime(check_out, '%Y-%m-%d')
        nights = max((co - ci).days, 1)
    except:
        pass

    # Create the internal booking record (status=pending)
    booking = HotelBooking.objects.create(
        hotel_id=hotel_id,
        hotel_name=hotel_name,
        city_name=city_name,
        check_in=check_in,
        check_out=check_out,
        nights=nights,
        adults=search_crit.get('adults', 2),
        rooms=search_crit.get('rooms', 1),
        
        cost_price=room_price,
        markup_pct=agoda_service.AGODA_MARKUP_PCT,
        markup_amount=markup_amount,
        customer_price=customer_price,
        currency='USD',
        
        guest_name=guest_name,
        guest_email=guest_email,
        guest_phone=guest_phone,
        status='pending'
    )
    
    # Generate the Agoda deep-link
    booking_url = agoda_service.get_booking_url(
        hotel_id=hotel_id,
        check_in=check_in,
        check_out=check_out,
        adults=search_crit.get('adults', 2),
        rooms=search_crit.get('rooms', 1)
    )
    
    # Normally we might redirect them immediately,
    # or show them a page with the redirect link.
    return redirect(booking_url)


def hotel_bookings(request):
    """List all hotel bookings."""
    bookings = HotelBooking.objects.all()
    # In a real app with user auth linked to bookings, filter by request.user
    return render(request, 'vols/hotel_bookings.html', {'bookings': bookings})


# ===========================================================================
# 🚀 ADMIN DASHBOARD API (REACT/NEXT.JS)
# ===========================================================================
from django.db.models import Sum, Count
from django.contrib.admin.views.decorators import staff_member_required

def api_admin_stats(request):
    """Returns global statistics for the admin dashboard."""
    # Flight Stats
    total_flight_bookings = Booking.objects.count()
    total_flight_revenue = Booking.objects.filter(status='confirmed').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    flight_profit = Booking.objects.filter(status='confirmed').aggregate(Sum('markup_amount'))['markup_amount__sum'] or 0
    
    # Hotel Stats
    total_hotel_bookings = HotelBooking.objects.count()
    total_hotel_revenue = HotelBooking.objects.filter(status='confirmed').aggregate(Sum('customer_price'))['customer_price__sum'] or 0
    hotel_profit = HotelBooking.objects.filter(status='confirmed').aggregate(Sum('markup_amount'))['markup_amount__sum'] or 0
    
    total_profit = flight_profit + hotel_profit
    
    # Clients (unique emails from Passengers and Hotel Guests)
    flight_clients = Passenger.objects.values('email').distinct().count()
    hotel_clients = HotelBooking.objects.exclude(guest_email='').values('guest_email').distinct().count()
    # Approximate unique clients
    total_clients = flight_clients + hotel_clients
    
    return JsonResponse({
        'flight_bookings': total_flight_bookings,
        'flight_revenue': float(total_flight_revenue),
        'hotel_bookings': total_hotel_bookings,
        'hotel_revenue': float(total_hotel_revenue),
        'total_profit': float(total_profit),
        'total_revenue': float(total_flight_revenue + total_hotel_revenue),
        'total_clients': total_clients
    })

def api_admin_bookings(request):
    """Returns a list of all flight bookings for the admin panel."""
    bookings = Booking.objects.prefetch_related('passengers').order_by('-created_at')
    data = []
    for b in bookings:
        passengers = list(b.passengers.values('first_name', 'last_name', 'email'))
        client_name = f"{passengers[0]['first_name']} {passengers[0]['last_name']}" if passengers else "Inconnu"
        
        data.append({
            'id': b.id,
            'reference': b.booking_reference,
            'itinerary': f"{b.origin} ✈ {b.destination}",
            'date': b.departure_date.strftime('%Y-%m-%d') if b.departure_date else '',
            'airline': b.airline,
            'client': client_name,
            'amount': float(b.total_amount),
            'currency': b.currency,
            'status': b.status,
            'created_at': b.created_at.strftime('%Y-%m-%d %H:%M')
        })
    return JsonResponse({'results': data})

def api_admin_clients(request):
    """Returns a list of unique clients."""
    # Group passengers by email to get unique clients
    passengers = Passenger.objects.values('email', 'first_name', 'last_name', 'phone_number').annotate(bookings_count=Count('booking')).order_by('-bookings_count')
    data = []
    for p in passengers:
        data.append({
            'name': f"{p['first_name']} {p['last_name']}",
            'email': p['email'],
            'phone': p['phone_number'],
            'bookings_count': p['bookings_count']
        })
    return JsonResponse({'results': list(data)})

import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_admin_cancel_booking(request, booking_id):
    """Cancel a booking via Duffel and update status."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    try:
        booking = Booking.objects.get(id=booking_id)
        if booking.status == 'cancelled':
            return JsonResponse({'error': 'Déjà annulé'}, status=400)
            
        result = duffel_service.cancel_order(booking.duffel_order_id)
        booking.status = 'cancelled'
        booking.save()
        
        return JsonResponse({'success': True, 'message': 'Réservation annulée avec succès', 'duffel_response': result})
    except Booking.DoesNotExist:
        return JsonResponse({'error': 'Réservation introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def react_dashboard_view(request):
    """Serves the standalone Vanilla React dashboard."""
    return render(request, 'vols/admin_dashboard_react.html')
