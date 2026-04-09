import sys, os
import polib

sys.stdout.reconfigure(encoding='utf-8')

PO = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
MO = PO.replace('.po', '.mo')

po = polib.pofile(PO, encoding='utf-8')

fixes = {
    # About Us — Hero
    'وكالة أبو منية للسفر والسياحة':
        'Abu Monya Travel & Tourism Agency',

    'وكالة أبومنية للسفر والسياحة وكالة وطنية تعمل في مجال السفر والسياحة الداخلية والخارجية وفق قانون تنظيم العمل السياحي وتنظيم عمل سلطة الطيران المدني في السودان.':
        'Abu Monya Travel & Tourism is a national agency operating in the field of domestic and international travel and tourism, in accordance with the Tourism Regulation Law and the Civil Aviation Authority regulations in Sudan.',

    # Vision card
    'رؤيتنا': 'Our Vision',
    'نتطلع لأن تكون وكالة ابومنية للسفر والسياحة الأولي و المحرك الفاعل للسفر وللسياحة محليا وإقليميا ودوليا .':
        'We aspire for Abu Monya Travel & Tourism to be the leading and driving force in travel and tourism locally, regionally, and internationally.',

    # Mission card
    'مهمتنا': 'Our Mission',
    'تلبية احتياجات عملائنا وفق رؤية إستراتيجية تلبي طموحاتهم و احتياجاتهم في مجال السفر والسياحة. وتعظيم الميزة النسبية والتنافسية للسودان كمنطقه جذب سياحي.':
        "Meeting our clients' needs through a strategic vision that fulfills their ambitions in travel and tourism, and maximizing Sudan's competitive advantage as a tourist destination.",

    # Goals section
    'أهدافنا': 'Our Goals',
    'الريادة في مجال السفر والسياحة محليا ودولياً.':
        'Leadership in the field of travel and tourism locally and internationally.',
    'استخدام النظم الاكترونيه والمعلوماتية عبر كافة الوسائط لتقديم أجود أنواع الخدمات.':
        'Using electronic and information systems across all platforms to deliver the highest quality services.',
    'ابتكار أنشطة سياحية وخدمات تلبي احتياجات عملائنا الكرام .':
        'Innovating tourism activities and services that meet the needs of our valued clients.',
}

added = updated = 0
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
    print(f"  [{status}] {msgid[:45]}")
