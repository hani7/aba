import sys, os
import polib

sys.stdout.reconfigure(encoding='utf-8')

PO = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
MO = PO.replace('.po', '.mo')

po = polib.pofile(PO, encoding='utf-8')

fixes = {
    # ── RESULTS PAGE ─────────────────────────────────────────────
    'نتائج البحث': 'Search Results',
    'مسافر': 'Passenger',
    'مسافرون': 'Passengers',
    'تعديل': 'Modify',
    'عرض/عروض وُجدت': 'offer(s) found',
    'لم يتم العثور على أي عروض لهذا البحث المعقد': 'No offers found for this search',
    'عدد التوقفات': 'Stops',
    'جميع الرحلات': 'All Flights',
    'مباشر': 'Direct',
    'محطة واحدة': '1 Stop',
    'محطتان أو أكثر': '2+ Stops',
    'الشركة': 'Airline',
    'جميع الشركات': 'All Airlines',
    'ترتيب حسب السعر': 'Sort by Price',
    'المقترح': 'Suggested',
    'الأقل إلى الأعلى': 'Lowest to Highest',
    'الأعلى إلى الأقل': 'Highest to Lowest',
    'اكتشف أجمل الفنادق لرحلتك': 'Discover the best hotels for your trip',
    'بناءً على اختيارك، وجدنا لك خيارات مميزة للإقامة': 'Based on your selection, we found great accommodation options',
    'احجز فندقك الآن بسهولة': 'Book your hotel easily now',
    'ابحث عن فندق لهذه الرحلة': 'Search for a hotel for this trip',
    'رحلة': 'Flight',
    'تفاصيل الأمتعة': 'Baggage Details',
    'شحن': 'Checked',
    'يد': 'Carry-on',
    'لا توجد تفاصيل معدات': 'No baggage details',
    'المجموع': 'Total',
    'توفر محدود': 'Limited availability',
    'متاح': 'Available',
    'آخر موعد دفع': 'Payment deadline',
    'احجز': 'Book',
    'تفاصيل الرحلة': 'Flight Details',
    'مقاعد متاحة': 'Seats available',
    'الهوية مطلوبة': 'ID required',
    'مبنى': 'Terminal',
    'تشغيل': 'Operated by',
    'المسافة': 'Distance',
    'طائرة': 'Aircraft',
    'محطة توقف (تغيير طائرة في': 'Layover (plane change in',
    'شروط التذكرة': 'Ticket Conditions',
    'استرداد قبل المغادرة': 'Refund before departure',
    'مسموح': 'Allowed',
    '(غرامة': '(Penalty',
    'غير مسموح': 'Not allowed',
    'تغيير قبل المغادرة': 'Change before departure',
    'لا توجد رحلات متاحة': 'No flights available',
    'جرب تواريخ أو مدن أخرى أو اعكس الوجهات': 'Try other dates or cities, or reverse destinations',
    'بحث جديد': 'New Search',
    'حجز الآن': 'Book Now',
    'قطعة': 'piece',
    # ── PASSENGER DETAILS PAGE ────────────────────────────────────
    'معلومات المسافر(ين': 'Passenger Information',
    'معلومات المسافر': 'Passenger Information',
    'الاسم الأول (باللغة الإنجليزية كما في الجواز': 'First Name (in English as in passport',
    'اسم العائلة (باللغة الإنجليزية': 'Last Name (in English',
    'تاريخ الميلاد': 'Date of Birth',
    'الجنس': 'Gender',
    'ذكر': 'Male',
    'أنثى': 'Female',
    'البريد الإلكتروني': 'Email Address',
    'رقم الهاتف (مع رمز الدولة': 'Phone Number (with country code',
    'رقم جواز السفر': 'Passport Number',
    'مثال': 'Example',
    'المجموع الفرعي': 'Subtotal',
    'يظهر السعر بعملة': 'Price is shown in',
    'حسب اختيارك': 'based on your selection',
    'يمكنك تغييرها من الشريط العلوي': 'You can change it from the top bar',
    'العودة إلى العروض': 'Back to Offers',
    'المتابعة للدفع الآمن': 'Proceed to Secure Payment',
    'التحويل لبوابة الدفع': 'Redirecting to payment gateway',
    'يجب كتابة الاسم بحروف إنجليزية فقط': 'Name must be written in English characters only',
    # ── PAYMENT PAGE ─────────────────────────────────────────────
    'تأكيد الحجز': 'Booking Confirmation',
    'رقم الحجز': 'Booking Reference',
    'يرجى إتمام التحويل البنكي لتفعيل تذكرتك': 'Please complete the bank transfer to activate your ticket',
    'المبلغ المستحق': 'Amount Due',
    'تحويل بنكي أو إيداع نقدي': 'Bank Transfer or Cash Deposit',
    'قم بتحويل المبلغ إلى أحد حساباتنا البنكية وأرسل إيصال الدفع عبر الواتساب لتأكيد حجزك': 'Transfer the amount to one of our bank accounts and send the payment receipt via WhatsApp to confirm your booking',
    'البنك': 'Bank',
    'اسم الحساب': 'Account Name',
    'رقم الحساب': 'Account Number',
    'رقم الايبان': 'IBAN Number',
    'بنك الخليج الدولي': 'Gulf International Bank',
    'احمد فاروق': 'Ahmed Farouq',
    'أرسل إيصال التحويل عبر الواتساب فور إتمامه لتأكيد الحجز': 'Send the transfer receipt via WhatsApp immediately after completing it to confirm your booking',
    'إرسال الإيصال عبر الواتساب': 'Send Receipt via WhatsApp',
    'المسافرون': 'Passengers',
}

added = updated = 0
for msgid, msgstr in fixes.items():
    e = po.find(msgid)
    if e:
        if not e.msgstr:
            e.msgstr = msgstr
            updated += 1
    else:
        po.append(polib.POEntry(msgid=msgid, msgstr=msgstr))
        added += 1

po.save(PO)
po.save_as_mofile(MO)
print(f"Done: +{added} new, ~{updated} updated | Total: {len(po)}")

verify = polib.pofile(PO, encoding='utf-8')
fail = []
for msgid in fixes:
    e = verify.find(msgid)
    if not (e and e.msgstr):
        fail.append(msgid)

print(f"Verified: {len(fixes)-len(fail)}/{len(fixes)} OK")
if fail:
    for f in fail:
        print(f"  FAIL: {f}")
