'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Results() {
  const [filter, setFilter] = useState('all');
  const [stops, setStops] = useState('all');

  // Hardcoded mock data to demonstrate the structure with React mappings
  const mockSearch = { passengers: 2, cabin_class: 'economy', slices: [{ origin: 'PAR', destination: 'LON' }] };
  const mockAirlines = ['Air France', 'British Airways'];
  const mockOffers = [
    {
      id: 'off_1',
      total_amount: 154,
      total_currency: 'EUR',
      slices: [
        {
          duration_fmt: '1h 15m',
          departure_date: '2026-04-10',
          segments: [
            {
              marketing_carrier: { name: 'Air France', iata_code: 'AF' },
              marketing_carrier_flight_number: '1234',
              departing_at: '2026-04-10T10:00:00',
              arriving_at: '2026-04-10T11:15:00',
              origin: { iata_code: 'CDG' },
              destination: { iata_code: 'LHR' }
            }
          ]
        }
      ]
    }
  ];

  const visibleOffers = mockOffers.filter(o => {
    const matchesAirline = filter === 'all' || o.slices.some(s => s.segments.some(seg => seg.marketing_carrier.name === filter));
    const matchesStops = stops === 'all' || o.slices.every(s => {
      const segCount = s.segments.length;
      if (stops === 'direct') return segCount === 1;
      if (stops === '1') return segCount === 2;
      if (stops === '2+') return segCount > 2;
      return true;
    });
    return matchesAirline && matchesStops;
  });

  return (
    <section className="section">
      <div className="container">
        
        <div className="results-header">

          <div className="route-meta">
            <span>📅 2026-04-10</span>
            <span>👤 {mockSearch.passengers} مسافرون</span>
            <span>💺 {mockSearch.cabin_class === 'economy' ? 'سياحية' : 'أخرى'}</span>
          </div>
          <Link href="/" className="btn btn-ghost btn-sm">← تعديل</Link>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
            <p className="results-count" style={{ marginBottom: 0 }}>
              {mockOffers.length > 0 ? (
                <><strong className="gold" id="visibleCount">{visibleOffers.length}</strong> عرض/عروض وُجدت</>
              ) : (
                'لم يتم العثور على أي عروض لهذا البحث المعقد.'
              )}
            </p>

            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <div className="filter-group" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label htmlFor="stopsFilter" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '600' }}>عدد التوقفات</label>
                  <select id="stopsFilter" className="field-input" style={{ padding: '8px 14px', width: 'auto', borderRadius: '999px', textTransform: 'none' }} value={stops} onChange={(e) => setStops(e.target.value)}>
                      <option value="all">جميع الرحلات</option>
                      <option value="direct">مباشر</option>
                      <option value="1">محطة واحدة</option>
                      <option value="2+">محطتان أو أكثر</option>
                  </select>
              </div>

              {mockAirlines.length > 0 && (
              <div className="filter-group" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <label htmlFor="airlineFilter" style={{ fontSize: '0.85rem', color: 'var(--text-muted)', fontWeight: '600' }}>الشركة</label>
                  <select id="airlineFilter" className="field-input" style={{ padding: '8px 14px', width: 'auto', borderRadius: '999px', textTransform: 'none' }} value={filter} onChange={(e) => setFilter(e.target.value)}>
                      <option value="all">جميع الشركات</option>
                      {mockAirlines.map(a => (
                        <option key={a} value={a}>{a}</option>
                      ))}
                  </select>
              </div>
              )}
            </div>
        </div>

        {mockOffers.length > 0 ? (
        <div className="offers-list">
          {visibleOffers.map((offer, i) => (
          <div className="offer-card" key={offer.id}>
            <div className="offer-slices">
                {offer.slices.map((slice, idx) => {
                  const segment = slice.segments[0];
                  const last_seg = slice.segments[slice.segments.length - 1];
                  return (
                    <div key={idx} style={{width: '100%'}}>
                      <div className="slice-details">
                          <div className="offer-airline">
                              <div className="airline-logo-placeholder">✈</div>
                              <div>
                                  <div className="airline-name">{segment.marketing_carrier.name || "الشركة"}</div>
                                  <div className="flight-number">رحلة: {segment.marketing_carrier.iata_code}{segment.marketing_carrier_flight_number || ""}</div>
                              </div>
                          </div>

                          <div className="offer-route">
                              <div className="route-time">
                                  <div className="time">{segment.departing_at.slice(11,16)}</div>
                                  <div className="airport">{segment.origin.iata_code}</div>
                                  <div className="airport" style={{fontWeight: 400, fontSize: '10px'}}>{slice.departure_date.slice(5)}</div>
                              </div>
                              
                              <div className="route-line">
                                  <div className="line-dur">{slice.duration_fmt}</div>
                                  <div className="line-bar">
                                      <div className="line"></div>
                                      <div className="plane-icon">✈</div>
                                  </div>
                                  <div className="line-stops">
                                      {slice.segments.length > 1 ? `${slice.segments.length - 1} توقف` : 'مباشر'}
                                  </div>
                              </div>
                              
                              <div className="route-time">
                                  <div className="time">{last_seg.arriving_at.slice(11,16)}</div>
                                  <div className="airport">{last_seg.destination.iata_code}</div>
                              </div>
                          </div>
                      </div>
                      {idx !== offer.slices.length - 1 && <hr style={{border: 0, height: '1px', background: 'var(--border)', margin: '12px 0'}} />}
                    </div>
                  );
                })}
            </div>

            <div className="offer-price">
              <div className="price-amount">
                {offer.total_amount} <span className="price-currency">{offer.total_currency}</span>
              </div>
              <div className="price-per">المجموع ({mockSearch.passengers} مسافرون)</div>
              <Link href={`/booking/${offer.id}`} className="btn btn-primary btn-sm" style={{marginTop: '8px'}}>
                احجز ←
              </Link>
            </div>
          </div>
          ))}
        </div>
        ) : (
        <div className="empty-state">
          <div className="empty-icon">🔍</div>
          <h3>لا توجد رحلات متاحة</h3>
          <p>جرب تواريخ أو مدن أخرى أو اعكس الوجهات.</p>
          <Link href="/" className="btn btn-primary">بحث جديد</Link>
        </div>
        )}
      </div>
    </section>
  );
}
