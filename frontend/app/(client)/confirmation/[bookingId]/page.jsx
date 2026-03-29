import Link from 'next/link';

export function generateStaticParams() {
  return [{ bookingId: 'mock' }];
}

export default function Confirmation({ params }) {
  // Static mock layout for the booking confirmation
  const booking = {
    booking_reference: 'BKG12345',
    origin: 'PAR',
    destination: 'LON',
    departure_date: '2026-04-10',
    airline: 'Air France',
    flight_number: 'AF1234',
    cabin_class: 'economy',
    total_amount: 154,
    currency: 'EUR'
  };

  const passengers = [
    { first_name: 'محمد', last_name: 'أحمد', email: 'mohammed@email.com' },
    { first_name: 'فاطمة', last_name: 'علي', email: 'fatima@email.com' }
  ];

  return (
    <section className="section">
      <div className="container confirm-container">
        
        <div className="confirm-hero">
          <div className="confirm-check">✓</div>
          <h1 className="confirm-title">تم تأكيد الحجز!</h1>
          <p className="confirm-subtitle">تم حجز رحلتك بنجاح. رحلة سعيدة!</p>
        </div>

        <div className="booking-ref-card">
          <p className="ref-label">رقم مرجع الحجز</p>
          <p className="ref-code">{booking.booking_reference}</p>
        </div>

        <div className="detail-card">
          <h3 className="detail-card-title">✈ تفاصيل الرحلة</h3>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">مسار الرحلة</span>
              <span className="detail-value">{booking.origin} → {booking.destination}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">تاريخ المغادرة</span>
              <span className="detail-value">{booking.departure_date}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">الشركة</span>
              <span className="detail-value">{booking.airline}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">رقم الرحلة</span>
              <span className="detail-value">{booking.flight_number}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">الدرجة</span>
              <span className="detail-value">{booking.cabin_class === 'economy' ? 'سياحية' : 'أخرى'}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">الإجمالي المدفوع</span>
              <span className="detail-value gold">{booking.total_amount} {booking.currency}</span>
            </div>
          </div>
        </div>

        <div className="detail-card">
          <h3 className="detail-card-title">👤 مسافرون</h3>
          {passengers.map((p, idx) => (
          <div className="passenger-row" key={idx}>
            <span className="passenger-num">{idx + 1}</span>
            <span>{p.first_name} {p.last_name}</span>
            <span className="text-muted">{p.email}</span>
          </div>
          ))}
        </div>

        <div className="confirm-actions">
          <Link href="/" className="btn btn-ghost">🏠 الرئيسية</Link>
          <Link href="/my-bookings" className="btn btn-primary">📋 حجوزاتي</Link>
        </div>

      </div>
    </section>
  );
}
