import sys, polib
sys.stdout.reconfigure(encoding='utf-8')
po = polib.pofile('locale/en/LC_MESSAGES/django.po', encoding='utf-8')
keys = ['ابحثوا الآن', 'السفر يبدأ هنا', 'أكثر من 10,000 مسار جوي', 'لماذا تختار وكالة أبو منية؟']
for k in keys:
    e = po.find(k)
    if e and e.msgstr:
        print(f'OK: {k} -> {e.msgstr}')
    else:
        print(f'MISSING: {k}')
