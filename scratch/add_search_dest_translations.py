"""
add_search_dest_translations.py
Adds all missing English translations for:
- Search form: cabin class, passengers, trip type, date labels, placeholders
- Destination card: badge (country) and desc (landmark) strings
"""
import sys, os
import polib

sys.stdout.reconfigure(encoding='utf-8')

EN_PO_PATH = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
EN_MO_PATH = EN_PO_PATH.replace('.po', '.mo')

MISSING = {
    # ── SEARCH FORM — Cabin Class ────────────────────────────────
    'الدرجة': 'Class',
    'سياحية': 'Economy',
    'سياحية ممتازة': 'Premium Economy',
    'أعمال': 'Business Class',
    'أولى': 'First Class',
    # ── SEARCH FORM — Passengers ─────────────────────────────────
    'المسافرون': 'Passengers',
    'بالغ واحد': '1 Adult',
    'بالغان': '2 Adults',
    '3 بالغين': '3 Adults',
    '4 بالغين': '4 Adults',
    '5 بالغين': '5 Adults',
    # ── SEARCH FORM — Trip Type ──────────────────────────────────
    'ذهاب فقط': 'One Way',
    'ذهاب وعودة': 'Round Trip',
    'وجهات متعددة': 'Multi-city',
    # ── SEARCH FORM — Labels & Placeholders ──────────────────────
    'المغادرة': 'From',
    'الوجهة': 'To',
    'تاريخ (الذهاب)': 'Departure Date',
    'تاريخ (العودة)': 'Return Date',
    'مثل: باريس، LHR، JFK': 'E.g. Paris, LHR, JFK',
    'مثل: لندن، DXB': 'E.g. London, DXB',
    'إضافة رحلة': 'Add Flight',
    'ابحث عن رحلات': 'Search Flights',
    # ── DESTINATION BADGES (country) ─────────────────────────────
    '🇪🇬 مصر': '🇪🇬 Egypt',
    '🇫🇷 فرنسا': '🇫🇷 France',
    '🇦🇪 الإمارات': '🇦🇪 UAE',
    '🇹🇷 تركيا': '🇹🇷 Turkey',
    '🇬🇧 المملكة المتحدة': '🇬🇧 UK',
    '🇮🇹 إيطاليا': '🇮🇹 Italy',
    '🇶🇦 قطر': '🇶🇦 Qatar',
    '🇪🇸 إسبانيا': '🇪🇸 Spain',
    '🇲🇦 المغرب': '🇲🇦 Morocco',
    '🇺🇸 الولايات المتحدة': '🇺🇸 USA',
    '🇯🇵 اليابان': '🇯🇵 Japan',
    '🇳🇱 هولندا': '🇳🇱 Netherlands',
    '🇸🇦 السعودية': '🇸🇦 Saudi Arabia',
    '🇪🇹 إثيوبيا': '🇪🇹 Ethiopia',
    '🇰🇼 الكويت': '🇰🇼 Kuwait',
    '🇸🇬 سنغافورة': '🇸🇬 Singapore',
    '🇲🇾 ماليزيا': '🇲🇾 Malaysia',
    '🇹🇭 تايلاند': '🇹🇭 Thailand',
    '🇩🇿 الجزائر': '🇩🇿 Algeria',
    '🇯🇴 الأردن': '🇯🇴 Jordan',
    # ── DESTINATION DESC (IATA · Landmark) ───────────────────────
    'CAI · أهرامات الجيزة': 'CAI · Giza Pyramids',
    'CDG · برج إيفل': 'CDG · Eiffel Tower',
    'DXB · برج خليفة': 'DXB · Burj Khalifa',
    'IST · المسجد الأزرق': 'IST · Blue Mosque',
    'LHR · بيغ بن': 'LHR · Big Ben',
    'FCO · الكولوسيوم': 'FCO · Colosseum',
    'DOH · أفق المدينة': 'DOH · City Skyline',
    'MAD · القصر الملكي': 'MAD · Royal Palace',
    'CMN · المدينة العتيقة': 'CMN · Medina',
    'JFK · مانهاتن': 'JFK · Manhattan',
    'NRT · برج طوكيو': 'NRT · Tokyo Tower',
    'BCN · ساغرادا فاميليا': 'BCN · Sagrada Família',
    'AMS · القنوات التاريخية': 'AMS · Historic Canals',
    'RUH · المملكة العربية': 'RUH · Kingdom of Arabia',
    'ADD · القلب الأفريقي': 'ADD · Heart of Africa',
    'KWI · أبراج الكويت': 'KWI · Kuwait Towers',
    'SIN · مارينا باي': 'SIN · Marina Bay',
    'KUL · برجا بتروناس': 'KUL · Petronas Towers',
    'BKK · وات أرون': 'BKK · Wat Arun',
    'ALG · مقام الشهيد': 'ALG · Martyrs\' Memorial',
    'AMM · المدرج الروماني': 'AMM · Roman Theatre',
    'JED · نافورة الملك فهد': 'JED · King Fahd Fountain',
}

# Load existing PO
po = polib.pofile(EN_PO_PATH, encoding='utf-8')
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

print(f"Added: {added}  |  Updated empty: {updated}")

# Save and compile
po.save(EN_PO_PATH)
po.save_as_mofile(EN_MO_PATH)
print("Saved & compiled!")

# Verify critical strings
print("\n=== Verification ===")
verify = polib.pofile(EN_PO_PATH, encoding='utf-8')
checks = [
    'الدرجة', 'سياحية', 'سياحية ممتازة', 'أعمال', 'أولى',
    'ذهاب فقط', 'ذهاب وعودة', 'وجهات متعددة',
    '🇫🇷 فرنسا', '🇹🇷 تركيا', '🇬🇧 المملكة المتحدة',
    'CDG · برج إيفل', 'IST · المسجد الأزرق', 'LHR · بيغ بن',
    'FCO · الكولوسيوم', 'ALG · مقام الشهيد',
]
ok = sum(1 for k in checks if verify.find(k) and verify.find(k).msgstr)
for k in checks:
    e = verify.find(k)
    status = f"✓ {e.msgstr[:30]}" if e and e.msgstr else "✗ MISSING"
    print(f"  {k[:35]}: {status}")
print(f"\nResult: {ok}/{len(checks)} OK  |  Total: {len(verify)} entries")
