"""
build_fresh_en_po.py
Reads the Arabic .po file (which has correct Arabic msgid strings)
and pairs them with the English translations we already know.
Writes a fresh, correctly encoded English .po file.
"""
import sys
import os
import polib

sys.stdout.reconfigure(encoding='utf-8')

AR_PO_PATH = os.path.join('locale', 'ar', 'LC_MESSAGES', 'django.po')
EN_PO_PATH = os.path.join('locale', 'en', 'LC_MESSAGES', 'django.po')
EN_MO_PATH = EN_PO_PATH.replace('.po', '.mo')

# Load the Arabic PO to get all correct msgid strings
ar_po = polib.pofile(AR_PO_PATH, encoding='utf-8')
print(f"Loaded Arabic PO: {len(ar_po)} entries")

# All known translations
TRANSLATIONS = {
    # --- Existing good translations (copied from the original good PO) ---
    'جميع المطارات': 'All airports',
    'آخر موعد دفع': 'Payment deadline',
    'أحمد': 'Ahmed',
    'أداء ومقاييس الموقع': 'Site performance and metrics',
    'أرقام': 'Numbers',
    'أسعار شاملة مع هامش ربح وكالة أبو منية': 'Prices inclusive of Abu Monya agency markup',
    'أفضل الفنادق في': 'Best hotels in',
    'أنثى': 'Female',
    'أهلاً بعودتك! سجّل دخولك لعرض حجوزاتك': 'Welcome back! Log in to view your bookings',
    'أهم المرافق': 'Top amenities',
    'إتمام الحجز': 'Complete booking',
    'إرسال': 'Send',
    'إلغاء': 'Cancel',
    'إنشاء الحساب': 'Create account',
    'إنشاء حساب': 'Create account',
    'إنشاء حساب جديد': 'Create a new account',
    'إنشاء حساب مجاني': 'Create a free account',
    'إيرادات': 'Revenue',
    'إيميل': 'Email',
    'ابحث عن رحلة': 'Search for a flight',
    'ابحث عن فندق لهذه الرحلة': 'Search for a hotel for this trip',
    'احجز فندقك الآن بسهولة': 'Book your hotel easily now',
    'احمد فاروق': 'Ahmed Farouq',
    'اختر غرفتك': 'Choose your room',
    'استرداد قبل المغادرة': 'Refund before departure',
    'استمتع بأرقى المرافق والخدمة التي تلبي أعلى المعايير العالمية': 'Enjoy the finest facilities and service meeting top global standards',
    'اسم الحساب': 'Account name',
    'اسم الضيف': 'Guest name',
    'اسم العائلة': 'Last name',
    'اسم العميل': 'Customer name',
    'اسم المستخدم': 'Username',
    'اسم المستخدم أو كلمة المرور غير صحيحة': 'Incorrect username or password',
    'اكتشف أجمل الفنادق لرحلتك': 'Discover the best hotels for your trip',
    'الأعلى إلى الأقل': 'Highest to lowest',
    'الأقل إلى الأعلى': 'Lowest to highest',
    'الإجراءات': 'Actions',
    'الإيرادات الإجمالية': 'Total Revenue',
    'الاسم الأول': 'First name',
    'البريد الإلكتروني': 'Email address',
    'البنك': 'Bank',
    'التحويل لبوابة الدفع': 'Redirecting to payment gateway',
    'التذكرة': 'Ticket',
    'التواريخ': 'Dates',
    'الجنس': 'Gender',
    'الحالة': 'Status',
    'الحجوزات': 'Bookings',
    'الحجوزات والإلغاءات': 'Bookings and Cancellations',
    'الربح الصافي': 'Net profit',
    'السعر الإجمالي': 'Total price',
    'الشركة': 'Company',
    'العملاء الفريدون': 'Unique customers',
    'العودة إلى التسجيل': 'Back to sign up',
    'العودة إلى العروض': 'Back to offers',
    'العودة إلى نتائج البحث': 'Back to search results',
    'العودة للموقع': 'Back to website',
    'الغرف المتاحة': 'Available rooms',
    'الفئة': 'Category',
    'المبلغ': 'Amount',
    'المبلغ المستحق': 'Amount due',
    'المبلغ المستحق للدفع': 'Amount due for payment',
    'المتابعة للدفع الآمن': 'Proceed to secure payment',
    'المجموع الفرعي': 'Subtotal',
    'المرجع': 'Reference',
    'المسار': 'Route',
    'المسافرون والزوار الدائمون': 'Frequent passengers and visitors',
    'المقترح': 'Suggested',
    'الهوية مطلوبة': 'ID required',
    'انضم إلى آلاف المسافرين واحجز رحلتك بكل سهولة': 'Join thousands of travelers and book your trip with ease',
    'بحث جديد': 'New search',
    'بنك الخليج الدولي': 'Gulf International Bank',
    'تأكيد': 'Confirm',
    'تأكيد البريد الإلكتروني': 'Verify Email',
    'تأكيد الحجز': 'Booking Confirmation',
    'تأكيد كلمة المرور': 'Confirm password',
    'تاريخ الطلب': 'Order date',
    'تاريخ الميلاد': 'Date of birth',
    'تحويل بنكي أو إيداع نقدي': 'Bank transfer or cash deposit',
    'تذكرة رحلتك': 'Your flight ticket',
    'ترتيب حسب السعر': 'Sort by price',
    'تسجيل الدخول': 'Log In',
    'تسجيل الدخول للإدارة': 'Admin Login',
    'تسجيل خروج': 'Log Out',
    'تشغيل': 'Operated by',
    'تشمل هامش خدمة الوكالة': 'Includes agency service margin',
    'تعديل': 'Edit',
    'تغيير قبل المغادرة': 'Change before departure',
    'تفاصيل الرحلة': 'Flight Details',
    'تفعيل الحساب': 'Activate Account',
    'تقييم': 'Rating',
    'تكييف': 'Air conditioning',
    'تم الإلغاء بنجاح': 'Cancelled successfully',
    'تمت عملية الدفع الإلكتروني بنجاح': 'Electronic payment completed successfully',
    'توفر محدود': 'Limited availability',
    'توقف': 'Stop',
    'جاري استرداد رحلات الطيران': 'Retrieving flights...',
    'جاري التحميل': 'Loading...',
    'جرب تواريخ أو مدن أخرى أو اعكس الوجهات': 'Try other dates or cities, or reverse destinations',
    'جميع الرحلات': 'All flights',
    'جميع الشركات': 'All airlines',
    'جيد': 'Good',
    'جيد جداً': 'Very Good',
    'حجز رحلات الطيران': 'Flight Booking',
    'حجوزات الفنادق السابقة': 'Past Hotel Bookings',
    'حجوزاتي': 'My Bookings',
    'حسابي': 'My Account',
    'حفظ التذكرة': 'Save Ticket',
    'خدمة الغرف': 'Room Service',
    'خطأ في السيرفر': 'Server error',
    'دخول': 'Enter',
    'ذكر': 'Male',
    'رحلات كحد أقصى': 'flights maximum',
    'رحلة جديدة': 'New Flight',
    'رقم الايبان': 'IBAN Number',
    'رقم الحجز': 'Booking Number',
    'رقم الحساب': 'Account Number',
    'رقم الهاتف': 'Phone Number',
    'رقم جواز السفر': 'Passport Number',
    'رمز التفعيل': 'Activation Code',
    'سأقوم بالتحويل البنكي': 'I will make a bank transfer',
    'شروط التذكرة': 'Ticket Conditions',
    'طائرة': 'Aircraft',
    'عادي': 'Regular',
    'عدد الأشخاص (الحد الأقصى': 'Number of people (Max',
    'عدد التوقفات': 'Number of stops',
    'عدد الحجوزات': 'Number of bookings',
    'عدد الغرف': 'Number of rooms',
    'عرض التفاصيل وتحميل التذكرة': 'View details and download ticket',
    'عرض/عروض وُجدت': 'offer(s) found',
    'عن الفندق': 'About the hotel',
    'غير متوفر': 'Not available',
    'غير مسموح': 'Not allowed',
    'فتح': 'Open',
    'فندق متاح': 'available hotel',
    'قاعدة العملاء': 'Client Base',
    'قطعة': 'Piece',
    'كلمة المرور': 'Password',
    'لا توجد تفاصيل معدات': 'No equipment details',
    'لا توجد حجوزات': 'No bookings found',
    'لا توجد رحلات متاحة': 'No flights available',
    'لا توجد غرف متاحة لهذا الفندق للتواريخ المحددة': 'No rooms available for this hotel on selected dates',
    'لا توجد فنادق متاحة': 'No hotels available',
    'لا توجد نتائج': 'No results found',
    'لتحميل التذكرة': 'To download the ticket',
    'لديك حساب بالفعل؟': 'Already have an account?',
    'لقد أرسلنا رمز تفعيل إلى بريدك الإلكتروني': 'We have sent an activation code to your email',
    'للإجمالي': 'for the total',
    'للتواريخ المحددة': 'for selected dates',
    'لم نتمكن من العثور على فنادق في': "We couldn't find hotels in",
    'لم يتم العثور على أي عروض لهذا البحث المعقد': 'No offers found for this search',
    'لوحة تحكم إدارة الرحلات': 'Flight Management Dashboard',
    'ليالي': 'nights',
    'ليس لديك أي حجوزات في الوقت الحالي': 'You do not have any bookings at the moment',
    'ليس لديك حجوزات فنادق حالياً': 'You have no current hotel bookings',
    'ليس لديك حساب؟': "Don't have an account?",
    'ليلة': 'night',
    'مؤكد': 'Confirmed',
    'مباشر': 'Direct',
    'مبنى': 'Terminal',
    'مثال': 'Example',
    'محطة واحدة': '1 Stop',
    'محطتان أو أكثر': '2+ Stops',
    'محمد': 'Mohammed',
    'مرحباً': 'Welcome',
    'مسبح': 'Pool',
    'معلومات المسافر': 'Passenger Information',
    'مقاعد متاحة': 'Seats available',
    'مقبول': 'Acceptable',
    'ملخص الرحلة': 'Flight Summary',
    'ملغى': 'Cancelled',
    'نتائج البحث': 'Search Results',
    'نتمنى لكم رحلة سعيدة': 'We wish you a pleasant flight',
    'نظرة عامة': 'Overview',
    'نوع السرير': 'Bed Type',
    'واي فاي مجاني': 'Free Wi-Fi',
    'يجب كتابة الاسم بحروف إنجليزية فقط': 'Name must be written in English characters only',
    'يرجى إتمام التحويل البنكي لتفعيل تذكرتك': 'Please complete the bank transfer to activate your ticket',
    'يرجى إتمام عملية الدفع لإصدار التذاكر الإلكترونية': 'Please complete payment to issue e-tickets',
    'يرجى إدخال بيانات الضيف الأساسي لتأكيد الحجز': 'Please enter primary guest details to confirm booking',
    'يرجى تسجيل الدخول أولاً للوصول إلى هذه الصفحة': 'Please log in first to access this page',
    'يرجى تصحيح الأخطاء أدناه': 'Please correct the errors below',
    'يرجى ملء جميع الحقول المطلوبة': 'Please fill in all required fields',
    'يسعدنا إرسال رابط تذكرتكم': 'We are pleased to send your ticket link',
    'يظهر السعر بعملة': 'Price is shown in',
    'يمكنك تغييرها من الشريط العلوي': 'You can change it from the top bar',
    'دليل الاستخدام': 'User Guide',
    'مسافر': 'Passenger',
    'مسافرون': 'Passengers',
    'شحن': 'Checked',
    'يد': 'Carry-on',
    'المجموع': 'Total',
    'متاح': 'Available',
    'احجز': 'Book',
    'رحلة': 'Flight',
    'مسموح': 'Allowed',
    'حجز الآن': 'Book Now',
    'وكالة': 'Agency',
    'أبو منية': 'Abu Monya',
    'الرئيسية': 'Home',
    'فنادق': 'Hotels',
    'حجوزات الطيران': 'Flight Bookings',
    'حجوزات الفنادق': 'Hotel Bookings',
    'خدماتنا': 'Services',
    'من نحن': 'About Us',
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
    'السفر يبدأ هنا': 'Your Journey Starts Here',
    'ابحثوا الآن': 'Search Now',
    'رحلات الطيران': 'Flights',
    'ذهاب فقط': 'One-way',
    'ذهاب وعودة': 'Round Trip',
    'وجهات متعددة': 'Multi-city',
    'المغادرة': 'From',
    'الوجهة': 'To',
    'إضافة رحلة': 'Add Flight',
    'المسافرون': 'Passengers',
    'بالغ واحد': '1 Adult',
    # Destinations
    'القاهرة': 'Cairo',
    'باريس': 'Paris',
    'دبي': 'Dubai',
    'إسطنبول': 'Istanbul',
    'لندن': 'London',
    'روما': 'Rome',
    'الدوحة': 'Doha',
    'مدريد': 'Madrid',
    'مراكش': 'Marrakech',
    'نيويورك': 'New York',
    'طوكيو': 'Tokyo',
    'برشلونة': 'Barcelona',
    'أمستردام': 'Amsterdam',
    'الرياض': 'Riyadh',
    'أديس أبابا': 'Addis Ababa',
    'الكويت': 'Kuwait City',
    'سنغافورة': 'Singapore',
    'كوالالمبور': 'Kuala Lumpur',
    'بانكوك': 'Bangkok',
    'الجزائر': 'Algiers',
    'عمّان': 'Amman',
    'جدة': 'Jeddah',
    # Footer
    'أبو منية للسياحة': 'Abu Monya Tourism',
    'نحن هنا لنجعل تجربة سفرك أسهل وأكثر متعة من خلال توفير أفضل العروض والخدمات.': 'We are here to make your travel experience easier and more enjoyable by providing the best deals and services.',
    'اكتشف': 'Discover',
    'الوجهات السياحية': 'Destinations',
    'نشاطاتنا': 'Our Activities',
    'حجز الفنادق': 'Hotel Booking',
    'الدعم': 'Support',
    'الأسئلة الشائعة': 'FAQ',
    'قانوني': 'Legal',
    'سياسة الخصوصية': 'Privacy Policy',
    'شروط الخدمة': 'Terms of Service',
    # Privacy page
    'سياسة الخصوصية — وكالة أبو منية': 'Privacy Policy — Abu Monya Agency',
    'آخر تحديث: أبريل 2026': 'Last Updated: April 2026',
    '1. المعلومات التي نجمعها': '1. Information We Collect',
    'نحن نجمع المعلومات التي تقدمها لنا مباشرة عند حجز رحلة، مثل الاسم، تفاصيل جواز السفر، البريد الإلكتروني، ورقم الهاتف.': 'We collect information you provide directly to us when booking a trip, such as name, passport details, email, and phone number.',
    '2. كيف نستخدم معلوماتك': '2. How We Use Your Information',
    'نستخدم معلوماتك لمعالجة حجوزاتك، إرسال التذاكر، وتزويدك بتحديثات الرحلات. كما نستخدمها للتواصل معك بشأن عروضنا الترويجية إذا اخترت الاشتراك.': 'We use your information to process your bookings, send tickets, and provide flight updates. We also use it to communicate with you about our promotional offers if you choose to subscribe.',
    '3. مشاركة البيانات': '3. Data Sharing',
    'نحن نشارك بياناتك فقط مع مقدمي الخدمات الضروريين (مثل شركات الطيران عبر Duffel أو الفنادق عبر Agoda) لإتمام حجزك. نحن لا نبيع بياناتك لأطراف ثالثة.': 'We only share your data with necessary service providers (such as airlines via Duffel or hotels via Agoda) to complete your booking. We do not sell your data to third parties.',
    '4. أمن البيانات': '4. Data Security',
    'نحن نستخدم بروتوكولات أمان متقدمة ونشفير SSL لحماية معلوماتك الحساسة وخصوصاً بيانات الدفع.': 'We use advanced security protocols and SSL encryption to protect your sensitive information, especially payment data.',
    '5. حقوقك': '5. Your Rights',
    'لك الحق في الوصول إلى معلوماتك الشخصية التي نحتفظ بها، أو طلب تصحيحها أو حذفها في أي وقت عبر التواصل معنا.': 'You have the right to access the personal information we hold about you, or request its correction or deletion at any time by contacting us.',
    # Terms page
    'شروط الخدمة — وكالة أبو منية': 'Terms of Service — Abu Monya Agency',
    'يرجى قراءة هذه الشروط بعناية قبل استخدام خدماتنا.': 'Please read these terms carefully before using our services.',
    '1. الخدمات المقدمة': '1. Services Provided',
    'وكالة أبو منية هي وسيط بين المسافر ومقدمي خدمات السفر (شركات الطيران والفنادق). نحن نسهل عملية الحجز ولكننا لسنا مسؤولين عن التغييرات التي تجريها شركات الطيران في المواعيد أو الخدمات.': 'Abu Monya Agency is an intermediary between the traveler and travel service providers (airlines and hotels). We facilitate the booking process but are not responsible for changes made by airlines to schedules or services.',
    '2. الأسعار والدفع': '2. Prices and Payment',
    'جميع الأسعار المعروضة تشمل الرسوم والضرائب المطبقة في وقت الحجز. تحتفظ الوكالة بالحق في تغيير الأسعار قبل تأكيد الحجز النهائي في حال حدوث تغييرات من المصدر.': 'All displayed prices include fees and taxes applicable at the time of booking. The agency reserves the right to change prices before final booking confirmation in case of changes from the source.',
    '3. الإلغاء والاسترداد': '3. Cancellation and Refund',
    'تخضع شروط الإلغاء لسياسات شركة الطيران أو الفندق المحجوز. في حال طلب الإلغاء، قد يتم تطبيق رسوم إدارية من قبل الوكالة بالإضافة إلى رسوم مقدم الخدمة.': 'Cancellation terms are subject to the policies of the booked airline or hotel. In case of a cancellation request, administrative fees may be applied by the agency in addition to service provider fees.',
    '4. جوازات السفر والتأشيرات': '4. Passports and Visas',
    'يتحمل المسافر كامل المسؤولية عن التأكد من صلاحية جواز سفره (6 أشهر على الأقل) والحصول على التأشيرات اللازمة لوجهته.': 'The traveler bears full responsibility for ensuring the validity of their passport (at least 6 months) and obtaining the necessary visas for their destination.',
    '5. التعديلات على الشروط': '5. Amendments to Terms',
    'نحتفظ بالحق في تعديل هذه الشروط في أي وقت. استمرارك في استخدام الموقع بعد التعديلات يعني موافقتك عليها.': 'We reserve the right to amend these terms at any time. Your continued use of the site after amendments means you agree to them.',
    # FAQ page
    'الأسئلة الشائعة — وكالة أبو منية': 'FAQ — Abu Monya Agency',
    'كل ما تحتاج معرفته عن الحجز والخدمات في مكان واحد': 'Everything you need to know about booking and services in one place',
    'كيف يمكنني حجز تذكرة طيران؟': 'How can I book a flight ticket?',
    'ببساطة، استخدم محرك البحث في الصفحة الرئيسية، اختر وجهتك وتاريخ سفرك، ثم اختر الرحلة المناسبة وأكمل بيانات الركاب وادفع إلكترونياً.': 'Simply use the search engine on the home page, choose your destination and travel date, then choose the appropriate flight, complete passenger details, and pay electronically.',
    'هل يمكنني إلغاء حجزي أو تعديله؟': 'Can I cancel or modify my booking?',
    "نعم، يمكنك طلب إلغاء أو تعديل الحجز عبر صفحة 'حجوزاتي' أو بالتواصل مع فريق الدعم. يرجى الملاحظة أن الرسوم تعتمد على سياسة شركة الطيران.": "Yes, you can request to cancel or modify a booking via the 'My Bookings' page or by contacting the support team. Please note that fees depend on the airline's policy.",
    'ما هي طرق الدفع المتاحة؟': 'What are the available payment methods?',
    'نحن نقبل الدفع عبر بطاقات الماستركارد، والفيزا كارد، وعبر Stripe. كما نوفر خيارات الدفع المحلية في بعض الدول.': 'We accept payment via Mastercard, Visa, and Stripe. We also provide local payment options in some countries.',
    'متى سأستلم تذكرتي الإلكترونية؟': 'When will I receive my e-ticket?',
    'بعد إتمام عملية الدفع بنجاح، ستصلك التذكرة فوراً على بريدك الإلكتروني، كما يمكنك تحميلها من حسابك على الموقع.': 'After successful payment, you will receive the ticket immediately via email, and you can also download it from your account on the site.',
    # Destinations page
    'استكشف وجهاتنا — وكالة أبو منية': 'Explore Our Destinations — Abu Monya Agency',
    'استكشف وجهاتنا حول العالم': 'Explore Our Destinations Around the World',
    'اكتشف أفضل المدن والرحلات التي نقدمها بأفضل الأسعار': 'Discover the best cities and flights we offer at the best prices',
    '✨ عروض متاحة': '✨ Offers Available',
    # Activities page
    'نشاطاتنا — وكالة أبو منية': 'Our Activities — Abu Monya Agency',
    'نشاطاتنا وفعالياتنا': 'Our Activities & Events',
    'نحن نلتزم بالتواجد في قلب الأحداث الكبرى لتطوير خدماتنا وتقديم الأفضل لعملائنا.': 'We are committed to being at the heart of major events to develop our services and provide the best for our clients.',
    'منتدى العمرة والزيارة - المملكة العربية السعودية': 'Umrah & Ziyarah Forum - Saudi Arabia',
    'لقطات من مشاركة وكالة أبو منية في فعاليات منتدى العمرة والزيارة لتوسيع شراكاتنا وخدماتنا.': "Snapshots from Abu Monya Agency's participation in the Umrah & Ziyarah Forum events to expand our partnerships and services.",
    'السعودية': 'Saudi Arabia',
    'منتدى العمرة والزيارة': 'Umrah & Ziyarah Forum',
    # Page titles
    'وكالة أبو منية': 'Abu Monya Agency',
    'حجز رحلات الطيران': 'Flight Booking',
}

# Build the new PO file
new_po = polib.POFile()
new_po.metadata = {
    'Project-Id-Version': '1.0',
    'Report-Msgid-Bugs-To': '',
    'POT-Creation-Date': '2026-04-09 16:00+0100',
    'PO-Revision-Date': '2026-04-09 16:00+0100',
    'Language': 'en',
    'MIME-Version': '1.0',
    'Content-Type': 'text/plain; charset=utf-8',
    'Content-Transfer-Encoding': '8bit',
}

# Add all entries from Arabic PO, using our translations dict
matched = 0
unmatched = 0
for ar_entry in ar_po:
    msgid = ar_entry.msgid
    if not msgid:
        continue
    msgstr = TRANSLATIONS.get(msgid, '')
    entry = polib.POEntry(msgid=msgid, msgstr=msgstr)
    new_po.append(entry)
    if msgstr:
        matched += 1
    else:
        unmatched += 1

print(f"Matched: {matched}, No translation yet: {unmatched}")

# Also add any extra entries from TRANSLATIONS not in ArPO (new page strings)
ar_msgids = {e.msgid for e in ar_po}
for msgid, msgstr in TRANSLATIONS.items():
    if msgid not in ar_msgids:
        entry = polib.POEntry(msgid=msgid, msgstr=msgstr)
        new_po.append(entry)
        print(f"  Added new: {msgid[:40]}")

# Save as UTF-8
new_po.save(EN_PO_PATH)
print(f"\nSaved fresh {EN_PO_PATH} with {len(new_po)} entries")

# Compile .mo
new_po.save_as_mofile(EN_MO_PATH)
print(f"Compiled {EN_MO_PATH}")

# Verify
verify_po = polib.pofile(EN_PO_PATH, encoding='utf-8')
for key in ['سياسة الخصوصية', 'الأسئلة الشائعة', 'نشاطاتنا', 'شروط الخدمة', 'اكتشف', 'الدعم', 'قانوني']:
    e = verify_po.find(key)
    if e and e.msgstr:
        print(f"OK: {key} -> {e.msgstr}")
    else:
        print(f"MISSING: {key}")
