"""
add_missing_translations.py
Adds all missing strings from home, contact, about, services, and navbar
to the existing English PO file, then recompiles the .mo.
"""
import sys, os
import polib

sys.stdout.reconfigure(encoding='utf-8')

EN_PO_PATH = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
EN_MO_PATH = EN_PO_PATH.replace('.po', '.mo')

# All missing translations from all pages
MISSING = {
    # ── HOME PAGE ────────────────────────────────────────────────
    'وكالة أبو منية — ابحث عن رحلتك': 'Abu Monya Agency — Search Your Flight',
    'أكثر من 10,000 مسار جوي': 'More than 10,000 air routes',
    'السفر يبدأ هنا': 'Your Journey Starts Here',
    'ابحثوا الآن': 'Search Now',
    'قارنوا آلاف العروض من أكبر شركات الطيران — بأسعار مضمونة وتجربة سهلة.': 'Compare thousands of offers from the biggest airlines — at guaranteed prices and with an easy experience.',
    'رحلات الطيران': 'Flights',
    'فنادق': 'Hotels',
    'شركاؤنا من شركات الطيران': 'Our Airline Partners',
    'أبرز الوجهات ✈': 'Top Destinations ✈',
    'الوجهات الأكثر طلباً هذا الموسم': 'Most requested destinations this season',
    'عروض متاحة': 'Offers Available',
    'لماذا تختار وكالة أبو منية؟': 'Why choose Abu Monya Agency?',
    'نتائج فورية': 'Instant Results',
    'آلاف العروض في الوقت الفعلي بفضل واجهة Duffel API المتقدمة.': 'Thousands of offers in real time thanks to the advanced Duffel API.',
    'بحث ذكي بالعربية': 'Smart Arabic Search',
    'ابحث بالعربية أو الإنجليزية — النظام يترجم تلقائياً.': 'Search in Arabic or English — the system translates automatically.',
    'وجهات متعددة': 'Multi-destination',
    'أنشئ رحلات ذهاباً وإياباً أو متعددة الوجهات بسهولة.': 'Create round-trip or multi-destination trips easily.',
    'عملات متعددة': 'Multiple Currencies',
    'اعرض الأسعار بالدولار الأمريكي أو الجنيه السوداني بضغطة واحدة.': 'Display prices in USD or Sudanese Pound with one click.',
    # ── CONTACT PAGE ─────────────────────────────────────────────
    'تواصل معنا': 'Contact Us',
    'GET IN TOUCH': 'GET IN TOUCH',
    'Name': 'Name',
    'Your Name': 'Your Name',
    'E-mail': 'E-mail',
    'your@email.com': 'your@email.com',
    'Subject': 'Subject',
    'Message Subject': 'Message Subject',
    'Message': 'Message',
    'Write your message here...': 'Write your message here...',
    'SEND MESSAGE': 'SEND MESSAGE',
    'الخرطوم السوق العربي. تقاطع شارع الحرية مع شارع مصطفى الأمين، غرب مستشفى الراهبات، عمارة عامر العقارية الطابق الثاني، شقة رقم 3': 'Khartoum, Arab Market. Intersection of Al-Hurriya Street and Mustafa Al-Amin Street, west of the Sisters Hospital, Amer Real Estate Building, 2nd floor, Apartment No. 3',
    'تابعنا على': 'Follow Us On',
    # ── NAVBAR (base.html) ────────────────────────────────────────
    'الرئيسية': 'Home',
    'من نحن': 'About Us',
    'خدماتنا': 'Services',
    'تسجيل الخروج': 'Log Out',
    'حسابي': 'My Account',
    'حجوزاتي': 'My Bookings',
    'حجز رحلات الطيران': 'Book Flights',
    # ── FOOTER (base.html) ────────────────────────────────────────
    'أبو منية للسياحة': 'Abu Monya Tourism',
    'نحن هنا لنجعل تجربة سفرك أسهل وأكثر متعة من خلال توفير أفضل العروض والخدمات.': 'We are here to make your travel experience easier and more enjoyable by providing the best deals and services.',
    'اكتشف': 'Discover',
    'الوجهات السياحية': 'Destinations',
    'نشاطاتنا': 'Our Activities',
    'الدعم': 'Support',
    'الأسئلة الشائعة': 'FAQ',
    'قانوني': 'Legal',
    'سياسة الخصوصية': 'Privacy Policy',
    'شروط الخدمة': 'Terms of Service',
    'جميع الحقوق محفوظة لوكالة': 'All rights reserved to',
    'جميع الحقوق محفوظة': 'All rights reserved',
    # ── SEARCH FORM ───────────────────────────────────────────────
    'ذهاب فقط': 'One-way',
    'ذهاب وعودة': 'Round Trip',
    'رحلة مباشرة': 'Multi-city',
    'المغادرة من': 'Departing from',
    'الوجهة': 'Destination',
    'إضافة رحلة': 'Add Flight',
    'المسافرون': 'Passengers',
    'بالغ': 'Adult',
    'بالغون': 'Adults',
    'طفل': 'Child',
    'رضيع': 'Infant',
    'تطبيق': 'Apply',
    'بحث عن رحلات': 'Search Flights',
    'تاريخ الذهاب': 'Departure date',
    'تاريخ العودة': 'Return date',
    'الدرجة': 'Class',
    'الدرجة الاقتصادية': 'Economy',
    'درجة رجال الأعمال': 'Business',
    'الدرجة الأولى': 'First Class',
    # ── ABOUT PAGE ────────────────────────────────────────────────
    'من نحن — وكالة أبو منية': 'About Us — Abu Monya Agency',
    'قصتنا': 'Our Story',
    'مهمتنا': 'Our Mission',
    'فريقنا': 'Our Team',
    'رؤيتنا': 'Our Vision',
    # ── SERVICES PAGE ─────────────────────────────────────────────
    'خدماتنا — وكالة أبو منية': 'Our Services — Abu Monya Agency',
    'خدماتنا المميزة': 'Our Premium Services',
    # ── GENERAL ───────────────────────────────────────────────────
    'وكالة أبو منية': 'Abu Monya Agency',
    'احجز رحلاتك بأفضل الأسعار مع وكالة أبو منية، بدعم من': 'Book your flights at the best prices with Abu Monya Agency, powered by',
}

# Load existing PO
po = polib.pofile(EN_PO_PATH, encoding='utf-8')
existing_msgids = {e.msgid for e in po}
print(f"Existing entries: {len(po)}")

added = 0
updated = 0
for msgid, msgstr in MISSING.items():
    existing = po.find(msgid)
    if existing:
        if not existing.msgstr:
            existing.msgstr = msgstr
            updated += 1
    else:
        entry = polib.POEntry(msgid=msgid, msgstr=msgstr)
        po.append(entry)
        added += 1

print(f"Added: {added} new entries")
print(f"Updated: {updated} existing empty entries")

# Save
po.save(EN_PO_PATH)
print(f"Saved {EN_PO_PATH}")

# Recompile
po.save_as_mofile(EN_MO_PATH)
print(f"Compiled {EN_MO_PATH}")

# Verify key strings
print("\n=== Verification ===")
verify = polib.pofile(EN_PO_PATH, encoding='utf-8')
keys_to_check = [
    'الرئيسية', 'من نحن', 'خدماتنا', 'تواصل معنا',
    'السفر يبدأ هنا', 'ابحثوا الآن', 'أبرز الوجهات ✈',
    'نتائج فورية', 'عملات متعددة',
    'اكتشف', 'الدعم', 'قانوني', 'سياسة الخصوصية',
    'الأسئلة الشائعة', 'شروط الخدمة', 'نشاطاتنا',
    'GET IN TOUCH', 'SEND MESSAGE',
]
ok_count = 0
for key in keys_to_check:
    e = verify.find(key)
    if e and e.msgstr:
        print(f"  ✓ {key[:35]} -> {e.msgstr[:35]}")
        ok_count += 1
    else:
        print(f"  ✗ MISSING: {key}")

print(f"\nResult: {ok_count}/{len(keys_to_check)} OK")
print(f"Total entries in PO: {len(verify)}")
