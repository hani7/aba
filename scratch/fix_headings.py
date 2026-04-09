import sys, os
import polib

sys.stdout.reconfigure(encoding='utf-8')

PO = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
MO = PO.replace('.po', '.mo')

po = polib.pofile(PO, encoding='utf-8')

fixes = {
    # Privacy section headings — match exactly what the template sends
    'المعلومات التي نجمعها':   'Information We Collect',
    'كيف نستخدم معلوماتك':    'How We Use Your Information',
    'مشاركة البيانات':         'Data Sharing',
    'أمن البيانات':            'Data Security',
    'حقوقك':                  'Your Rights',
    # Terms section headings
    'الخدمات المقدمة':         'Services Provided',
    'الأسعار والدفع':          'Prices and Payment',
    'الإلغاء والاسترداد':      'Cancellation and Refund',
    'جوازات السفر والتأشيرات': 'Passports and Visas',
    'التعديلات على الشروط':    'Amendments to Terms',
    # Home features heading
    'لماذا تختار وكالة أبو منية؟': 'Why Choose Abu Monya Agency?',
    # Footer copyright
    'جميع الحقوق محفوظة لوكالة': 'All rights reserved to',
    'جميع الحقوق محفوظة': 'All rights reserved',
}

added = 0
updated = 0
for msgid, msgstr in fixes.items():
    e = po.find(msgid)
    if e:
        e.msgstr = msgstr
        updated += 1
    else:
        po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))
        added += 1

po.save(PO)
po.save_as_mofile(MO)
print(f"Done: +{added} new, ~{updated} updated | Total: {len(po)}")

verify = polib.pofile(PO, encoding='utf-8')
for msgid, msgstr in fixes.items():
    e = verify.find(msgid)
    status = 'OK' if (e and e.msgstr) else 'FAIL'
    print(f"  [{status}] {msgid[:40]} -> {msgstr[:35]}")
