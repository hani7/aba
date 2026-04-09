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
from django.views.decorators.cache import cache_page
from .services import duffel_service
from .services import travelpayouts_service
from .services import booking_service
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
    {'iata': 'DOH', 'name_ar': _('الدوحة'),   'badge': _('🇶🇦 قطر'),             'desc': _('DOH · أفق المدينة'),       'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Doha_-_West_Bay_Skyline_03.jpg/960px-Doha_-_West_Bay_Skyline_03.jpg'},
    {'iata': 'MAD', 'name_ar': _('مدريد'),    'badge': _('🇪🇸 إسبانيا'),         'desc': _('MAD · القصر الملكي'),      'image': 'https://images.unsplash.com/photo-1543783207-ec64e4d95325?w=600&h=300&fit=crop&q=80'},
    {'iata': 'CMN', 'name_ar': _('مراكش'),    'badge': _('🇲🇦 المغرب'),          'desc': _('CMN · المدينة العتيقة'),   'image': 'https://images.unsplash.com/photo-1533167649158-6d508895b680?w=600&h=300&fit=crop&q=80'},
    {'iata': 'JFK', 'name_ar': _('نيويورك'),  'badge': _('🇺🇸 الولايات المتحدة'),'desc': _('JFK · مانهاتن'),           'image': 'https://images.unsplash.com/photo-1490644658840-3f2e3f8c5625?w=600&h=300&fit=crop&q=80'},
    {'iata': 'NRT', 'name_ar': _('طوكيو'),    'badge': _('🇯🇵 اليابان'),         'desc': _('NRT · برج طوكيو'),         'image': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=600&h=300&fit=crop&q=80'},
    {'iata': 'BCN', 'name_ar': _('برشلونة'),  'badge': _('🇪🇸 إسبانيا'),         'desc': _('BCN · ساغرادا فاميليا'),   'image': 'https://images.unsplash.com/photo-1511527661048-7fe73d85e9a4?w=600&h=300&fit=crop&q=80'},
    {'iata': 'AMS', 'name_ar': _('أمستردام'), 'badge': _('🇳🇱 هولندا'),          'desc': _('AMS · القنوات التاريخية'), 'image': 'https://images.unsplash.com/photo-1534351590666-13e3e96b5017?w=600&h=300&fit=crop&q=80'},
    {'iata': 'RUH', 'name_ar': _('الرياض'),   'badge': _('🇸🇦 السعودية'),        'desc': _('RUH · المملكة العربية'),   'image': 'https://images.unsplash.com/photo-1586724237569-f3d0c1dee8c6?w=600&h=300&fit=crop&q=80'},
    {'iata': 'ADD', 'name_ar': _('أديس أبابا'),'badge': _('🇪🇹 إثيوبيا'),         'desc': _('ADD · القلب الأفريقي'),    'image': 'https://images.unsplash.com/photo-1523805009345-7448845a9e53?w=600&h=300&fit=crop&q=80'},
    {'iata': 'KWI', 'name_ar': _('الكويت'),   'badge': _('🇰🇼 الكويت'),          'desc': _('KWI · أبراج الكويت'),      'image': 'https://images.unsplash.com/photo-1512632578888-169bbbc64f33?w=600&h=300&fit=crop&q=80'},
    {'iata': 'SIN', 'name_ar': _('سنغافورة'), 'badge': _('🇸🇬 سنغافورة'),        'desc': _('SIN · مارينا باي'),        'image': 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?w=600&h=300&fit=crop&q=80'},
    {'iata': 'KUL', 'name_ar': _('كوالالمبور'),'badge': _('🇲🇾 ماليزيا'),         'desc': _('KUL · برجا بتروناس'),      'image': 'https://images.unsplash.com/photo-1555848962-6e79363ec58f?w=600&h=300&fit=crop&q=80'},
    {'iata': 'BKK', 'name_ar': _('بانكوك'),   'badge': _('🇹🇭 تايلاند'),         'desc': _('BKK · وات أرون'),          'image': 'https://images.unsplash.com/photo-1563492065599-3520f775eeed?w=600&h=300&fit=crop&q=80'},
    {'iata': 'ALG', 'name_ar': _('الجزائر'),  'badge': _('🇩🇿 الجزائر'),         'desc': _('ALG · مقام الشهيد'),       'image': 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Martyrs_Memorial._Algiers%2C_Algeria.jpg/960px-Martyrs_Memorial._Algiers%2C_Algeria.jpg'},
    {'iata': 'AMM', 'name_ar': _('عمّان'),    'badge': _('🇯🇴 الأردن'),          'desc': _('AMM · المدرج الروماني'),   'image': 'https://images.unsplash.com/photo-1541410965313-d53b3c16ef17?w=600&h=300&fit=crop&q=80'},
]

# Fixed exchange rates to USD (approximate 2025 rates)
CURRENCY_TO_USD = {
    'USD': 1.0,
    'EUR': 1.08,
    'GBP': 1.27,
    'DZD': 0.0074,
    'MAD': 0.099,
    'TND': 0.32,
    'AED': 0.272,
    'SAR': 0.267,
    'QAR': 0.274,
    'KWD': 3.25,
    'BHD': 2.65,
    'OMR': 2.60,
    'EGP': 0.021,
    'TRY': 0.031,
    'CHF': 1.12,
    'CAD': 0.74,
    'AUD': 0.65,
    'JPY': 0.0067,
    'CNY': 0.138,
    'INR': 0.012,
    'MYR': 0.226,
    'SGD': 0.74,
    'THB': 0.028,
    'ZAR': 0.054,
    'NOK': 0.093,
    'SEK': 0.096,
    'DKK': 0.145,
}

def convert_to_usd(amount, currency):
    """Convert amount to USD using fixed rates. Returns rounded string."""
    try:
        rate = CURRENCY_TO_USD.get((currency or '').upper(), 1.0)
        return round(float(amount) * rate, 2)
    except (TypeError, ValueError):
        return None

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

    # Pre-convert penalty amounts to USD for display
    conditions = offer.get('conditions') or {}
    for key in ('refund_before_departure', 'change_before_departure'):
        cond = conditions.get(key)
        if cond and cond.get('penalty_amount'):
            usd = convert_to_usd(cond['penalty_amount'], cond.get('penalty_currency', 'USD'))
            cond['penalty_amount_usd'] = usd

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

@cache_page(60 * 60 * 24)  # Cache for 24 hours
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
    locale = getattr(request, 'LANGUAGE_CODE', 'ar')
    try:
        for q in queries:
            places = duffel_service.search_places(q, locale=locale)
            for p in places:
                if p.get('type') not in ['airport', 'city']:
                    continue
                pid = p.get('id')
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)
                iata = p.get('iata_code') or p.get('iata_city_code') or ''
                city_name = p.get('city_name') or ''
                all_results.append({
                    'id': pid,
                    'name': p.get('name') or '',
                    'type': p.get('type'),
                    'iata_code': iata,
                    'city_name': city_name,
                    # Reverse-lookup Arabic name for display
                    'arabic_name': next((ar for ar, en in ARABIC_CITY_MAP.items()
                                        if en.lower() in [
                                            (p.get('name') or '').lower(),
                                            city_name.lower()
                                        ]), ''),
                })
        return JsonResponse({'results': all_results[:15]})
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

            # --- Exclude Duffel Airways (virtual/sandbox carrier) ---
            def has_duffel_airways(offer):
                for sl in offer.get('slices', []):
                    for seg in sl.get('segments', []):
                        carrier_name = (seg.get('marketing_carrier') or {}).get('name', '')
                        if 'duffel airways' in carrier_name.lower():
                            return True
                return False

            offers = [o for o in offers if not has_duffel_airways(o)]
            # --------------------------------------------------------

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
        # Sanitize phone: strip spaces, dashes, parentheses
        raw_phone = request.POST.get(f'phone_{i}', '').strip()
        raw_phone = re.sub(r'[\s\-\(\)\.]+', '', raw_phone)
        
        # Format as E.164 for Duffel validation
        if raw_phone.startswith('00'):
            raw_phone = '+' + raw_phone[2:]
        elif raw_phone.startswith('0'):
            raw_phone = '+212' + raw_phone[1:] # Assume a default country code if missing (e.g. +212 for Morocco, or edit if needed)
        elif not raw_phone.startswith('+'):
            raw_phone = '+' + raw_phone
            
        digits_only = re.sub(r'\D', '', raw_phone)
        if len(digits_only) < 7:
            raw_phone = '+212600000000' # Minimum valid length
            
        passenger['phone_number'] = raw_phone
            
        duffel_passengers.append(passenger)

    try:
        original_amount = offer.get('custom_original_amount', offer['total_amount'])
        markup_amount = offer.get('custom_markup_amount', 0)
        total_customer_price = float(offer['total_amount'])

        # Step 1: Check Payment Requirements
        requires_instant = offer.get('payment_requirements', {}).get('requires_instant_payment', False)
        if requires_instant:
            messages.error(request, "عذراً، رحلات هذا الطيران تتطلب الدفع الإلكتروني الفوري للإصدار (Low Cost) ولا تدعم الحجز المؤقت للتحويل البنكي. يرجى تعديل البحث لمعظم الطيران النظامي.")
            return redirect('vols:passenger_details', offer_id=offer_id)

        # Step 2: Hold the ticket with Duffel
        order = duffel_service.create_order(offer_id, duffel_passengers, original_amount, offer['total_currency'], hold=True)

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
            status='pending',
        )

        for idx, p in enumerate(duffel_passengers, 1):
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
                passport_number=request.POST.get(f'passport_{idx}', '').upper()
            )

        # Step 3: Redirect to payment choice page (Visa or Bank Transfer)
        return redirect('vols:payment_choice', booking_id=booking.id)

    except Exception as e:
        if 'OFFER_EXPIRED' in str(e):
            messages.error(request, "⏰ عذراً، انتهت صلاحية هذا العرض. يرجى البحث مجدداً للحصول على أسعار محدثة.")
            return redirect('vols:search_results')
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
        return redirect('vols:my_bookings')
    return redirect('vols:home')


def stripe_cancel(request):
    """Called if user cancels Stripe checkout - redirect back to payment choice."""
    booking_id = request.GET.get('booking_id')
    messages.warning(request, "تم إلغاء عملية الدفع. يمكنك الاختيار مجدداً.")
    if booking_id:
        return redirect('vols:payment_choice', booking_id=booking_id)
    return redirect('vols:home')



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
            city_id=int(city_id) if city_id else 0,
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
            hotel_id=int(hotel_id),
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
        
    def to_float(val):
        if not val: return 0.0
        return float(str(val).replace(',', '.'))

    hotel_id = int(request.POST.get('hotel_id'))
    hotel_name = request.POST.get('hotel_name')
    room_price = to_float(request.POST.get('room_price', 0))
    markup_amount = to_float(request.POST.get('markup_amount', 0))
    customer_price = to_float(request.POST.get('customer_price', 0))
    
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
        markup_pct=agoda_service.HOTEL_MARKUP_PCT,
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
        hotel_id=int(hotel_id),
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
        passengers = list(b.passengers.values('first_name', 'last_name', 'email', 'phone_number', 'title', 'gender', 'born_on'))
        client_name = f"{passengers[0]['first_name']} {passengers[0]['last_name']}" if passengers else "Inconnu"
        client_phone = passengers[0]['phone_number'] if passengers else ""
        client_email = passengers[0]['email'] if passengers else ""
        
        data.append({
            'id': b.id,
            'reference': b.booking_reference,
            'itinerary': f"{b.origin} ✈ {b.destination}",
            'origin': b.origin,
            'destination': b.destination,
            'date': b.departure_date.strftime('%Y-%m-%d') if b.departure_date else '',
            'airline': b.airline,
            'flight_number': getattr(b, 'flight_number', ''),
            'cabin_class': getattr(b, 'cabin_class', ''),
            'client': client_name,
            'client_phone': client_phone,
            'client_email': client_email,
            'passengers': passengers,
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


@csrf_exempt
def api_admin_issue_booking(request, booking_id):
    """
    Issue a held ticket programmatically from admin dashboard
    (Called after admin verifies manual bank transfer receipt).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if already issued
    if booking.status not in ['pending', 'confirmed']:
        return JsonResponse({'error': 'Booking must be pending to be issued.'}, status=400)
        
    try:
        # Subtract from Duffel Balance by issuing the ticket mapping original amount
        # Note: We must pay the original_amount to Duffel, not the markup price!
        # The create_order fetched original_amount but we didn't save it directly besides subtracting total_amount and markup.
        duffel_cost = float(booking.total_amount) - float(booking.markup_amount)
        result = duffel_service.issue_ticket(booking.duffel_order_id, duffel_cost, booking.currency)
        
        booking.status = 'paid'
        booking.save()
        return JsonResponse({'success': True, 'msg': 'تم إصدار التذكرة بنجاح من نظام Duffel.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def react_dashboard_view(request):
    """Serves the standalone Vanilla React dashboard."""
    return render(request, 'vols/admin_dashboard_react.html')


def generate_ticket_pdf(request, booking_id):
    """Generates and returns a downloadable A4 PDF e-ticket for a booking — full Emirates style."""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                     Paragraph, Spacer, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    import io, os

    booking  = get_object_or_404(Booking, id=booking_id)
    passengers = list(booking.passengers.all())
    lead = passengers[0] if passengers else None

    # ── Colors ──────────────────────────────────────────────────────────────
    DARK     = colors.HexColor('#0b1437')
    GREY_HDR = colors.HexColor('#b0b0b0')
    NAVY_HDR = colors.HexColor('#0b1437')
    LIGHT_BG = colors.HexColor('#f8fafc')
    WHITE    = colors.white

    # ── Styles ───────────────────────────────────────────────────────────────
    def S(name, **kw):
        defaults = dict(fontName='Helvetica', fontSize=9, leading=12, textColor=DARK)
        defaults.update(kw)
        return ParagraphStyle(name, **defaults)

    title_s   = S('T',  fontName='Helvetica-Bold', fontSize=20, textColor=DARK)
    sub_s     = S('Su', fontSize=9,  textColor=colors.grey)
    lbl_s     = S('Lb', fontSize=7,  textColor=colors.grey, leading=9)
    val_s     = S('Va', fontName='Helvetica-Bold', fontSize=9, textColor=DARK, leading=12)
    sec_s     = S('Sh', fontName='Helvetica-Bold', fontSize=9, textColor=WHITE, leading=13)
    small_s   = S('Sm', fontSize=7,  textColor=colors.grey, leading=9)
    note_s    = S('No', fontSize=7,  textColor=colors.grey, alignment=TA_CENTER)
    footer_s  = S('Fo', fontSize=8,  textColor=colors.grey, alignment=TA_CENTER)

    # ── Full page width ──────────────────────────────────────────────────────
    PAGE_W = A4[0] - 3*cm   # usable width after margins

    def section_hdr(title, bg=GREY_HDR):
        tbl = Table([[Paragraph(title, sec_s)]], colWidths=[PAGE_W])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        return tbl

    def info_grid(rows_of_pairs):
        """Render a list of [(label,value), ...] rows in a 3-column grid."""
        all_rows = []
        for pairs in rows_of_pairs:
            col_w = PAGE_W / len(pairs)
            lbls = [Paragraph(l, lbl_s) for l, _ in pairs]
            vals = [Paragraph(str(v), val_s) for _, v in pairs]
            t = Table([lbls, vals], colWidths=[col_w]*len(pairs))
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
                ('LEFTPADDING', (0,0), (-1,-1), 5),
                ('RIGHTPADDING', (0,0), (-1,-1), 5),
                ('TOPPADDING', (0,0), (-1,-1), 3),
                ('BOTTOMPADDING', (0,0), (-1,-1), 3),
                ('LINEBELOW', (0,1), (-1,1), 0.3, colors.HexColor('#e2e8f0')),
            ]))
            all_rows.append(t)
        return all_rows

    # ── Build story ──────────────────────────────────────────────────────────
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm,
        title=f"e-Ticket {booking.booking_reference}"
    )
    story = []

    eticket_num = f"176{booking.id:06d}"
    cabin_map   = {'economy':'ECONOMY', 'business':'BUSINESS', 'first':'FIRST CLASS'}
    cabin       = cabin_map.get(booking.cabin_class, (booking.cabin_class or '').upper())
    dep_date    = booking.departure_date.strftime('%d %b %Y').upper() if booking.departure_date else 'N/A'
    created_str = booking.created_at.strftime('%d %b %Y').upper()

    # ─── HEADER ──────────────────────────────────────────────────────────────
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.jpg')
    if os.path.exists(logo_path):
        from reportlab.platypus import Image as RLImage
        logo = RLImage(logo_path, width=3*cm, height=1.8*cm)
        hdr_data = [[logo, Paragraph('e-Ticket Receipt & Itinerary', title_s)]]
        hdr_tbl = Table(hdr_data, colWidths=[3.5*cm, PAGE_W - 3.5*cm])
    else:
        hdr_tbl = Table([[Paragraph('e-Ticket Receipt & Itinerary', title_s)]])
    hdr_tbl.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                                  ('LEFTPADDING',(0,0),(-1,-1),0)]))
    story.append(hdr_tbl)
    story.append(Paragraph(f'Booking Reference (PNR): <b>{booking.booking_reference}</b>', sub_s))
    story.append(HRFlowable(width='100%', thickness=2, color=DARK, spaceAfter=8))

    # ─── LEGAL ───────────────────────────────────────────────────────────────
    story.append(Paragraph(
        "Your electronic ticket is stored in our computer reservation system. This e-Ticket receipt / itinerary "
        "is your record of your electronic ticket and forms part of your contract of carriage. You may need to "
        "show this receipt at the airport and/or to prove return or onward travel to customs and immigration officials.",
        small_s))
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph(
        "<b>Economy Class passengers</b> should report to check-in desks 3 hours prior to departure. "
        "<b>Business/First Class</b> passengers should report not later than 1 hour prior to departure. "
        "Boarding begins at least 35 minutes before scheduled departure time. Gates close 15 minutes prior.",
        small_s))
    story.append(Spacer(1, 0.25*cm))

    # ─── SECTION 1: PASSENGER & TICKET INFO ──────────────────────────────────
    story.append(section_hdr("PASSENGER AND TICKET INFORMATION"))
    story.append(Spacer(1, 0.08*cm))

    for p in passengers:
        pax_name = f"{p.last_name.upper()}/{p.first_name.upper()} {p.title.upper()}"
        for t in info_grid([
            [("PASSENGER NAME", pax_name), ("E-TICKET NUMBER", eticket_num), ("BOOKING REFERENCE", booking.booking_reference)],
            [("DATE OF BIRTH", str(p.born_on)), ("GENDER", "MALE" if p.gender == 'm' else "FEMALE"), ("PASSPORT NUMBER", "TBD AT CHECK-IN")],
            [("EMAIL", p.email or "N/A"), ("PHONE", p.phone_number or "N/A"), ("ISSUED BY/DATE", f"ABU MONYA AGENCY / {created_str}")],
        ]):
            story.append(t)
            story.append(Spacer(1, 0.05*cm))

    if not passengers:
        for t in info_grid([
            [("PASSENGER NAME", "N/A"), ("E-TICKET NUMBER", eticket_num), ("BOOKING REFERENCE", booking.booking_reference)],
            [("PASSPORT NUMBER", "TBD AT CHECK-IN"), ("ISSUED BY/DATE", f"ABU MONYA AGENCY / {created_str}"), ("", "")],
        ]):
            story.append(t)
            story.append(Spacer(1, 0.05*cm))

    story.append(Spacer(1, 0.2*cm))

    # ─── SECTION 2: TRAVEL INFORMATION ───────────────────────────────────────
    story.append(section_hdr("TRAVEL INFORMATION"))
    story.append(Spacer(1, 0.08*cm))

    col_w = [2.8*cm, 2.8*cm, 4.5*cm, 2.4*cm, 2.4*cm, 3.6*cm]
    travel_hdrs = [Paragraph(h, lbl_s) for h in
                   ['FLIGHT', 'DEPART/ARRIVE', 'AIRPORT/TERMINAL', 'CHECK-IN OPENS', 'CLASS', 'COUPON VALIDITY']]
    travel_row1 = [
        Paragraph(f"<b>{booking.airline} {booking.flight_number}</b><br/>CONFIRMED", val_s),
        Paragraph(f"{dep_date}<br/>TBD", val_s),
        Paragraph(f"{booking.origin} INTNL ({booking.origin})<br/>TERMINAL TBD", val_s),
        Paragraph(f"{dep_date}<br/>TBD", val_s),
        Paragraph(f"{cabin}<br/>SEAT", val_s),
        Paragraph("NOT BEFORE<br/>NOT AFTER", small_s),
    ]
    travel_row2 = [
        Paragraph("", small_s),
        Paragraph(f"{dep_date}<br/>TBD", small_s),
        Paragraph(f"{booking.destination} INTNL ({booking.destination})", small_s),
        Paragraph("", small_s),
        Paragraph("BAGGAGE<br/>ALLOW. 30KGS", small_s),
        Paragraph("", small_s),
    ]
    travel_tbl = Table([travel_hdrs, travel_row1, travel_row2], colWidths=col_w)
    travel_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('LINEBELOW', (0,1), (-1,1), 0.5, DARK),
        ('LINEBELOW', (0,2), (-1,2), 0.3, colors.HexColor('#e2e8f0')),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(travel_tbl)
    story.append(Spacer(1, 0.2*cm))

    # ─── SECTION 3: FARE INFO ─────────────────────────────────────────────────
    story.append(section_hdr("FARE AND ADDITIONAL INFORMATION"))
    story.append(Spacer(1, 0.08*cm))

    fare_left = [
        [Paragraph("FARE", lbl_s),        Paragraph(f"{booking.currency} {booking.total_amount}", val_s)],
        [Paragraph("TAXES/FEES/CHARGES", lbl_s), Paragraph("INCLUDED IN FARE", val_s)],
        [Paragraph("TOTAL", lbl_s),        Paragraph(f"<b>{booking.currency} {booking.total_amount}</b>", val_s)],
        [Paragraph("FORM OF PAYMENT", lbl_s), Paragraph("ONLINE / BANK TRANSFER", val_s)],
    ]
    fare_right = [
        [Paragraph("ADDITIONAL INFORMATION", lbl_s)],
        [Paragraph("NON-END/REFUND RESTRICTIONS APPLY", small_s)],
        [Paragraph("VALID ON FLIGHT DATE ONLY", small_s)],
        [Paragraph("", small_s)],
    ]
    fare_left_tbl  = Table(fare_left,  colWidths=[3.8*cm, 5.2*cm])
    fare_right_tbl = Table(fare_right, colWidths=[8.5*cm])
    for t in [fare_left_tbl, fare_right_tbl]:
        t.setStyle(TableStyle([
            ('LEFTPADDING',(0,0),(-1,-1),4), ('RIGHTPADDING',(0,0),(-1,-1),4),
            ('TOPPADDING',(0,0),(-1,-1),2),  ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ]))

    fare_outer = Table([[fare_left_tbl, fare_right_tbl]], colWidths=[9*cm, 9.5*cm])
    fare_outer.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(fare_outer)
    story.append(Paragraph("* AT CHECK-IN YOU MAY NEED TO PRESENT THE PROOF OF PAYMENT *", note_s))
    story.append(Spacer(1, 0.15*cm))

    # ─── SECTION 4: FARE CALCULATIONS ─────────────────────────────────────────
    story.append(section_hdr("FARE CALCULATIONS"))
    story.append(Spacer(1, 0.05*cm))
    calc_text = (f"{booking.origin} AIRLINE {booking.destination} "
                 f"{booking.total_amount:.2f} {booking.currency} END ROE 1.0000")
    story.append(Table([[Paragraph(calc_text, small_s)]], colWidths=[PAGE_W],
                        style=[('BACKGROUND',(0,0),(-1,-1),LIGHT_BG),
                               ('LEFTPADDING',(0,0),(-1,-1),6),
                               ('TOPPADDING',(0,0),(-1,-1),4),
                               ('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(Spacer(1, 0.2*cm))

    # ─── SECTION 5: CLIENT CONTACT ────────────────────────────────────────────
    story.append(section_hdr("CLIENT CONTACT INFORMATION", bg=NAVY_HDR))
    story.append(Spacer(1, 0.08*cm))

    client_name  = lead.first_name + ' ' + lead.last_name if lead else 'N/A'
    client_email = lead.email if lead else 'N/A'
    client_phone = lead.phone_number if lead else 'N/A'
    pdf_url = request.build_absolute_uri(f'/api/admin/ticket/{booking.id}/pdf/')

    for t in info_grid([
        [("CLIENT NAME", client_name), ("EMAIL", client_email), ("PHONE", client_phone)],
        [("BOOKING STATUS", booking.status.upper()), ("TICKET CREATED", created_str), ("PDF LINK", pdf_url[:60] + '...' if len(pdf_url) > 60 else pdf_url)],
    ]):
        story.append(t)
        story.append(Spacer(1, 0.05*cm))

    story.append(Spacer(1, 0.4*cm))

    # ─── FOOTER ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=colors.lightgrey))
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph(
        f"© {booking.created_at.year} Abu Monya Agency. All rights reserved. &nbsp;|&nbsp; Page 1 of 1",
        footer_s))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="eticket_{booking.booking_reference}.pdf"'
    return response
