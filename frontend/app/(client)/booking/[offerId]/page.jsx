'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { use } from 'react';

export function generateStaticParams() {
  return [{ offerId: 'mock' }];
}

export default function PassengerDetails({ params }) {
  const router = useRouter();
  const { offerId } = use(params);
  const [loading, setLoading] = useState(false);

  // Mock Data
  const offer = { total_amount: 154, total_currency: 'EUR', cabin_class: 'economy' };
  const search = { passengers: 2 };
  const slices = [{ origin: { iata_code: 'PAR' }, destination: { iata_code: 'LON' }, duration_fmt: '1h 15m', segments: [{ departing_at: '2026-04-10T10:00:00' }] }];

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      router.push('/confirmation/BKG12345');
    }, 1200);
  };

  return (
    <section className="section">
      <div className="container">
        <div className="recap-card" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center', borderBottom: '1px solid var(--border)', paddingBottom: '16px', marginBottom: '16px' }}>
              <div className="recap-meta" style={{ fontSize: '1.1rem' }}>
                <span>💰 <strong className="gold">{offer.total_amount} {offer.total_currency}</strong></span>
                <span>💺 {offer.cabin_class === 'economy' ? 'سياحية' : 'أخرى'}</span>
                <span>👤 {search.passengers} مسافرون</span>
              </div>
          </div>
          
          {slices.map((slice, idx) => (
          <div className="recap-route" style={{ marginBottom: '8px' }} key={idx}>
            <span className="gold" style={{ fontSize: '0.9rem', marginRight: '12px' }}>رحلة {idx + 1}</span>
            <span className="recap-city" style={{ fontSize: '1.2rem' }}>{slice.origin.iata_code}</span>
            <span className="route-arrow">→</span>
            <span className="recap-city" style={{ fontSize: '1.2rem' }}>{slice.destination.iata_code}</span>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginLeft: '16px' }}>📅 {slice.segments[0].departing_at.slice(0,10)} — 🕐 {slice.duration_fmt}</span>
          </div>
          ))}
        </div>

        <h2 className="section-title">معلومات المسافرين</h2>

        <form onSubmit={handleSubmit}>
          {Array.from({ length: search.passengers }).map((_, i) => (
          <div className="passenger-card" key={i}>
            <div className="passenger-header">
              <span className="passenger-badge">مسافر {i + 1}</span>
            </div>

            <div className="form-grid">
              <div className="form-field">
                <label className="field-label">الاسم الأول *</label>
                <input type="text" name={`first_name_${i}`} required className="field-input" placeholder="محمد" />
              </div>
              <div className="form-field">
                <label className="field-label">اسم العائلة *</label>
                <input type="text" name={`last_name_${i}`} required className="field-input" placeholder="أحمد" />
              </div>
              <div className="form-field">
                <label className="field-label">تاريخ الميلاد *</label>
                <input type="date" name={`born_on_${i}`} required className="field-input" max="2005-01-01" />
              </div>
              <div className="form-field">
                <label className="field-label">الجنس *</label>
                <div className="input-icon-wrap">
                  <select name={`gender_${i}`} className="field-input" defaultValue="m">
                    <option value="m">ذكر</option>
                    <option value="f">أنثى</option>
                  </select>
                </div>
              </div>
              <div className="form-field form-field-wide">
                <label className="field-label">البريد الإلكتروني *</label>
                <input type="email" name={`email_${i}`} required className="field-input" placeholder="mohammed@email.com" />
              </div>
              <div className="form-field form-field-wide">
                <label className="field-label">رقم الهاتف (اختياري)</label>
                <input type="tel" name={`phone_${i}`} className="field-input" placeholder="+212 6 00 00 00 00" />
              </div>
            </div>
          </div>
          ))}

          <div className="price-summary">
            <div className="price-row">
              <span>المجموع الفرعي ({search.passengers} مسافرون)</span>
              <span className="gold">{offer.total_amount} {offer.total_currency}</span>
            </div>
            <div className="price-row price-total">
              <span>المجموع</span>
              <span className="gold price-big">{offer.total_amount} {offer.total_currency}</span>
            </div>
          </div>

          <div className="form-actions">
            <button type="button" onClick={() => router.back()} className="btn btn-ghost">← العودة إلى العروض</button>
            <button type="submit" className="btn btn-primary btn-large" disabled={loading}>
              {!loading ? <span className="btn-text">✅ تأكيد الحجز</span> : <span className="btn-loader">⏳ جاري المعالجة...</span>}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
