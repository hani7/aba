import Link from 'next/link';

export default function MyBookings() {
  const bookings = [
    {
      booking_reference: 'BKG12345',
      origin: 'PAR',
      destination: 'LON',
      departure_date: '2026-04-10',
      airline: 'Air France',
      total_amount: 154,
      currency: 'EUR',
      passengers: 2
    }
  ];

  return (
    <section className="section">
      <div className="container">
        <div className="page-header">
          <h1 className="page-title">📋 حجوزاتي</h1>
          <Link href="/" className="btn btn-primary btn-sm">+ رحلة جديدة</Link>
        </div>

        {bookings.length > 0 ? (
        <div className="bookings-list">
          {bookings.map((booking, idx) => (
          <div className="booking-card" key={idx}>
            <div className="booking-ref">
              <span className="ref-label">المرجع</span>
              <span className="ref-code-small">{booking.booking_reference}</span>
            </div>
            <div className="booking-route">
              <span className="route-city-lg">{booking.origin}</span>
              <span className="route-arrow">→</span>
              <span className="route-city-lg">{booking.destination}</span>
            </div>
            <div className="booking-meta">
              <span>📅 {booking.departure_date}</span>
              <span>✈ {booking.airline}</span>
              <span>👤 {booking.passengers} مسافرون</span>
            </div>
            <div className="booking-amount">
              <span className="gold">{booking.total_amount} {booking.currency}</span>
            </div>
            <div className="booking-status">
              <span className="badge badge-success">مؤكد</span>
            </div>
          </div>
          ))}
        </div>
        ) : (
        <div className="empty-state">
          <div className="empty-icon">🎫</div>
          <h3>لا توجد حجوزات</h3>
          <p>ليس لديك أي حجوزات في الوقت الحالي.</p>
          <Link href="/" className="btn btn-primary">ابحث عن رحلة</Link>
        </div>
        )}

      </div>
    </section>
  );
}
