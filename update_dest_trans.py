import sys

content = """
    # Destinations
    "القاهرة": ("Cairo", "Le Caire"),
    "🇪🇬 مصر": ("🇪🇬 Egypt", "🇪🇬 Égypte"),
    "CAI · أهرامات الجيزة": ("CAI · Pyramids of Giza", "CAI · Pyramides de Gizeh"),

    "باريس": ("Paris", "Paris"),
    "🇫🇷 فرنسا": ("🇫🇷 France", "🇫🇷 France"),
    "CDG · برج إيفل": ("CDG · Eiffel Tower", "CDG · Tour Eiffel"),

    "دبي": ("Dubai", "Dubaï"),
    "🇦🇪 الإمارات": ("🇦🇪 UAE", "🇦🇪 EAU"),
    "DXB · برج خليفة": ("DXB · Burj Khalifa", "DXB · Burj Khalifa"),

    "إسطنبول": ("Istanbul", "Istanbul"),
    "🇹🇷 تركيا": ("🇹🇷 Turkey", "🇹🇷 Turquie"),
    "IST · المسجد الأزرق": ("IST · Blue Mosque", "IST · Mosquée Bleue"),

    "لندن": ("London", "Londres"),
    "🇬🇧 المملكة المتحدة": ("🇬🇧 UK", "🇬🇧 Royaume-Uni"),
    "LHR · بيغ بن": ("LHR · Big Ben", "LHR · Big Ben"),

    "روما": ("Rome", "Rome"),
    "🇮🇹 إيطاليا": ("🇮🇹 Italy", "🇮🇹 Italie"),
    "FCO · الكولوسيوم": ("FCO · Colosseum", "FCO · Colisée"),

    "الدوحة": ("Doha", "Doha"),
    "🇶🇦 قطر": ("🇶🇦 Qatar", "🇶🇦 Qatar"),
    "DOH · أفق المدينة": ("DOH · City Skyline", "DOH · Skyline de la Ville"),

    "مدريد": ("Madrid", "Madrid"),
    "🇪🇸 إسبانيا": ("🇪🇸 Spain", "🇪🇸 Espagne"),
    "MAD · القصر الملكي": ("MAD · Royal Palace", "MAD · Palais Royal"),

    "مراكش": ("Marrakech", "Marrakech"),
    "🇲🇦 المغرب": ("🇲🇦 Morocco", "🇲🇦 Maroc"),
    "CMN · المدينة العتيقة": ("CMN · Medina", "CMN · Médina"),

    "نيويورك": ("New York", "New York"),
    "🇺🇸 الولايات المتحدة": ("🇺🇸 USA", "🇺🇸 États-Unis"),
    "JFK · مانهاتن": ("JFK · Manhattan", "JFK · Manhattan"),

    "طوكيو": ("Tokyo", "Tokyo"),
    "🇯🇵 اليابان": ("🇯🇵 Japan", "🇯🇵 Japon"),
    "NRT · برج طوكيو": ("NRT · Tokyo Tower", "NRT · Tour de Tokyo"),

    "برشلونة": ("Barcelona", "Barcelone"),
    "BCN · ساغرادا فاميليا": ("BCN · Sagrada Familia", "BCN · Sagrada Familia"),

    "أمستردام": ("Amsterdam", "Amsterdam"),
    "🇳🇱 هولندا": ("🇳🇱 Netherlands", "🇳🇱 Pays-Bas"),
    "AMS · القنوات التاريخية": ("AMS · Historic Canals", "AMS · Canaux Historiques"),

    "الرياض": ("Riyadh", "Riyad"),
    "🇸🇦 السعودية": ("🇸🇦 Saudi Arabia", "🇸🇦 Arabie Saoudite"),
    "RUH · المملكة العربية": ("RUH · Saudi Kingdom", "RUH · Royaume Saoudien"),

    "أديس أبابا": ("Addis Ababa", "Addis-Abeba"),
    "🇪🇹 إثيوبيا": ("🇪🇹 Ethiopia", "🇪🇹 Éthiopie"),
    "ADD · القلب الأفريقي": ("ADD · The African Heart", "ADD · Le Cœur Africain"),

    "الكويت": ("Kuwait", "Koweït"),
    "🇰🇼 الكويت": ("🇰🇼 Kuwait", "🇰🇼 Koweït"),
    "KWI · أبراج الكويت": ("KWI · Kuwait Towers", "KWI · Tours de Koweït"),

    "سنغافورة": ("Singapore", "Singapour"),
    "🇸🇬 سنغافورة": ("🇸🇬 Singapore", "🇸🇬 Singapour"),
    "SIN · مارينا باي": ("SIN · Marina Bay", "SIN · Marina Bay"),

    "كوالالمبور": ("Kuala Lumpur", "Kuala Lumpur"),
    "🇲🇾 ماليزيا": ("🇲🇾 Malaysia", "🇲🇾 Malaisie"),
    "KUL · برجا بتروناس": ("KUL · Petronas Twin Towers", "KUL · Tours Jumelles Petronas"),

    "بانكوك": ("Bangkok", "Bangkok"),
    "🇹🇭 تايلاند": ("🇹🇭 Thailand", "🇹🇭 Thaïlande"),
    "BKK · وات أرون": ("BKK · Wat Arun", "BKK · Wat Arun"),

    "جدة": ("Jeddah", "Djeddah"),
    "JED · نافورة الملك فهد": ("JED · King Fahd's Fountain", "JED · Fontaine du roi Fahd"),

    "عمّان": ("Amman", "Amman"),
    "🇯🇴 الأردن": ("🇯🇴 Jordan", "🇯🇴 Jordanie"),
    "AMM · المدرج الروماني": ("AMM · Roman Theatre", "AMM · Théâtre Romain")
}
"""

import codecs
with codecs.open('build_translations.py', 'r', 'utf-8') as f:
    text = f.read()

text = text.replace('}\n\nen_dict = {k: v[0]', content + '\n\nen_dict = {k: v[0]')

with codecs.open('build_translations.py', 'w', 'utf-8') as f:
    f.write(text)

print("Appended destinations to build_translations.py")
