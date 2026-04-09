import polib
import sys

# Force UTF-8 output for Arabic
sys.stdout.reconfigure(encoding='utf-8')

po = polib.pofile('locale/en/LC_MESSAGES/django.po', encoding='utf-8')

keys = [
    'سياسة الخصوصية',
    'الأسئلة الشائعة',
    'شروط الخدمة',
    'نشاطاتنا',
    'منتدى العمرة والزيارة',
    'اكتشف',
    'الدعم',
    'قانوني',
    'الوجهات السياحية',
    'أبو منية للسياحة',
    'نحن هنا لنجعل تجربة سفرك أسهل وأكثر متعة من خلال توفير أفضل العروض والخدمات.',
    'دليل الاستخدام',
    'آخر تحديث: أبريل 2026',
    'كيف يمكنني حجز تذكرة طيران؟',
    'ما هي طرق الدفع المتاحة؟',
    'منتدى العمرة والزيارة - المملكة العربية السعودية',
    'نشاطاتنا وفعالياتنا',
]

print('=== Translation Verification Report ===\n')
missing = []
ok = []

for key in keys:
    entry = po.find(key)
    if entry and entry.msgstr:
        ok.append((key, entry.msgstr))
        print(f'OK: {key[:45]} -> {entry.msgstr[:45]}')
    else:
        missing.append(key)
        print(f'MISSING: {key}')

print(f'\n--- Summary ---')
print(f'OK: {len(ok)}/{len(keys)}')
print(f'Missing: {len(missing)}/{len(keys)}')
