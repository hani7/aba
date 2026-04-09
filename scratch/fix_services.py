import sys, os
import polib

sys.stdout.reconfigure(encoding='utf-8')

PO = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
MO = PO.replace('.po', '.mo')

po = polib.pofile(PO, encoding='utf-8')

fixes = {
    # Services page — subtitle
    'خدماتنا': 'Our Services',
    'في أبومنية نسعد بتقديم أميز الخدمات التي تلبي طموحكم وعروض دورية خاصة للعملاء':
        'At Abu Monya, we are pleased to offer the finest services that meet your ambitions, along with exclusive periodic offers for our clients.',

    # Card 1 — Medical Tourism
    'سياحة علاجية': 'Medical Tourism',
    'نقوم بتقديم كافة الحلول الخاصة بالسياحة العلاجية وخدمات طبية عالمية المستوى، يقوم موظفي السياحة العلاجية في أبومنية بتقديم خيارات عديدة للعلاج بالخارج بجودة عالية وأسعار تنافسية.':
        'We provide all solutions for medical tourism and world-class medical services. Our medical tourism staff at Abu Monya offer a wide range of overseas treatment options with high quality and competitive prices.',

    # Card 2 — International Tourism
    'سياحة عالمية': 'International Tourism',
    'أكتشف العالم عبر الرحلات السياحية.. نحن نقدم لكم عروض وباقات سياحية متكاملة وبأسعار هي الافضل حسب ميزانيتك وبخدمة عالية الجودة. نقوم بتأمين حجوزات مكان الاقامة للأفراد والعائلات والمجموعات السياحية حسب رغبة العميل.':
        'Discover the world through tourism trips. We offer comprehensive tour packages and promotions at the best prices for your budget, with high-quality service. We arrange accommodation bookings for individuals, families, and tour groups according to client preferences.',

    # Card 3 — Local Tourism
    'سياحة محلية': 'Local Tourism',
    'يزخر السودان بالكثير من المناطق السياحية المحلية كوجهة سياحية أصيلة ومثيرة ومميزة... من خلال قسم السياحة في وكالة أبومنية نقوم بتقديم بكجات وجولات سياحية مختلفة.':
        'Sudan is rich with local tourist destinations that are authentic, exciting, and unique. Through the tourism department at Abu Monya Agency, we offer a variety of tourism packages and guided tours.',

    # Card 4 — Domestic & International Travel
    'سفر داخلي وعالمي': 'Domestic & International Travel',
    'نقوم بتصميم رحلتك بما يتناسب رؤيتك بأسعار تنافسية وفريق عمل مؤهل لخدمتك.. نقوم بإصدار التذاكر الجوية الداخلية والعالمية حيث نالت الوكالة عضوية الاياتا وأصبحت مؤهلة لإصدار التذاكر الجوية على جميع الخطوط المنضوية تحت نظام الاياتا والبي اس بي.':
        'We design your trip to match your vision at competitive prices with a qualified team at your service. We issue domestic and international air tickets — the agency holds IATA membership, qualifying it to issue tickets on all airlines under the IATA and BSP systems.',

    # Card 5 — Bus Tickets
    'تذاكر بصات': 'Bus Tickets',
    'نقدم خدمات النقل البري الداخلي والخارجي عبر أكبر شركات الميناء البري حيث نوفر أحدث موديلات البصات السفرية الشحن البري.':
        'We provide domestic and international land transport services through the largest bus terminal companies, offering the latest models of travel buses and land freight.',

    # Card 6 — Flight Tickets
    'تذاكر طيران': 'Flight Tickets',
    'حلق معنا حول العالم...خيارات أكثر ومتنوعة عبر شركات خطوط الطيران العالمية. صمم رحلتك إلكترونيا وقدم طلب عبر نافذه احجز الآن.':
        'Fly with us around the world... More and varied options through international airline companies. Design your trip online and submit a request via the Book Now window.',

    # Card 7 — Hajj & Umrah
    'حج وعمرة': 'Hajj & Umrah',
    'خدمتهم شرف لنا 😊 نقدم عروض العمره لزوار وضيوف الرحمن.. تفويج وفود و حجز فندقي للحج والعمره بأسعار تناسب الجميع. وخدمات خاصة لكبار الزوار وخدماتنا هي الأفضل بإذن الله....VIP وأسعارنا هي الأنسب.':
        'Serving them is our honor 😊 We offer Umrah packages for the guests of Allah — group dispatching and hotel bookings for Hajj and Umrah at prices suitable for everyone, plus VIP services for distinguished visitors at the best prices.',

    # Card 8 — Visas
    'تأشيرات': 'Visas',
    'تتيح هذه الخدمة إمكانية تقديم وإدارة المعاملات الخاصة بالتأشيرات وإجراءات الجوازات والإقامات لجميع السفارات بكل سهولة وكفائة.':
        'This service provides the ability to submit and manage visa transactions, passport procedures, and residency permits for all embassies with ease and efficiency.',
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
all_ok = True
for msgid, msgstr in fixes.items():
    e = verify.find(msgid)
    ok = e and e.msgstr
    if not ok:
        all_ok = False
    print(f"  [{'OK' if ok else 'FAIL'}] {msgid[:50]}")

print(f"\nAll OK: {all_ok}")
