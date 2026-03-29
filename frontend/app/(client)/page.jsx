'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [tripType, setTripType] = useState('oneway');
  const [slices, setSlices] = useState([{ id: 0, origin: '', destination: '', date: '' }]);
  const [returnDate, setReturnDate] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // initialize first date
    const d = new Date().toISOString().split('T')[0];
    setSlices([{ id: 0, origin: '', destination: '', date: d }]);
  }, []);

  const getToday = () => {
    try { return new Date().toISOString().split('T')[0]; } catch(e) { return ''; }
  };

  const handleTripTypeChange = (e) => {
    const type = e.target.value;
    setTripType(type);
    if (type !== 'multicity') {
      setSlices([slices[0]]);
    }
  };

  const addSlice = () => {
    if (slices.length >= 6) {
      alert('يُسمح بـ 6 رحلات كحد أقصى.');
      return;
    }
    const lastDest = slices[slices.length - 1].destination;
    setSlices([...slices, { id: Date.now(), origin: lastDest, destination: '', date: getToday() }]);
  };

  const removeSlice = (idToRemove) => {
    setSlices(slices.filter((s) => s.id !== idToRemove));
  };

  const swapPlaces = () => {
    const newSlices = [...slices];
    const temp = newSlices[0].origin;
    newSlices[0].origin = newSlices[0].destination;
    newSlices[0].destination = temp;
    setSlices(newSlices);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => {
      router.push('/results');
    }, 1000);
  };

  return (
    <>
      <section className="hero">
        <div className="hero-bg">
          <div className="hero-orb hero-orb-1"></div>
          <div className="hero-orb hero-orb-2"></div>
          <div className="hero-orb hero-orb-3"></div>
        </div>
        <div className="container hero-content">
          <div className="hero-badge"><span>✈</span> Powered by Duffel Places API</div>
          <h1 className="hero-title">
            رحلتك القادمة،<br /><span className="gold">في ثوانٍ معدودة.</span>
          </h1>
          <p className="hero-subtitle">
            ابحث باسم المدينة أو المطار. قارن آلاف العروض في الوقت الفعلي.
          </p>

          <form onSubmit={handleSubmit} className="search-card">
            <div className="trip-type-selector">
              <label className="radio-tab">
                <input type="radio" name="trip_type" value="oneway" checked={tripType === 'oneway'} onChange={handleTripTypeChange} />
                <span>ذهاب فقط</span>
              </label>
              <label className="radio-tab">
                <input type="radio" name="trip_type" value="roundtrip" checked={tripType === 'roundtrip'} onChange={handleTripTypeChange} />
                <span>ذهاب وعودة</span>
              </label>
              <label className="radio-tab">
                <input type="radio" name="trip_type" value="multicity" checked={tripType === 'multicity'} onChange={handleTripTypeChange} />
                <span>وجهات متعددة</span>
              </label>
            </div>

            <div id="slices-container">
              {slices.map((slice, index) => (
                <div key={slice.id} className="slice-row search-grid" style={{ gridTemplateColumns: tripType === 'multicity' ? '1fr auto 1fr 1fr auto' : (tripType === 'roundtrip' ? '1fr auto 1fr 1fr 1fr' : '1fr auto 1fr 1fr'), marginTop: index > 0 ? '16px' : '0' }}>
                  
                  <div className="form-field autocomplete-wrapper">
                    <label className="field-label">{index === 0 ? 'المغادرة' : ''}</label>
                    <div className="input-icon-wrap">
                      <span className="fi">🛫</span>
                      <input type="text" placeholder={index === 0 ? "مثل: باريس، LHR، JFK" : "المغادرة"} required className="field-input as-ac" value={slice.origin} onChange={(e) => {
                        const ns = [...slices]; ns[index].origin = e.target.value; setSlices(ns);
                      }} />
                    </div>
                  </div>

                  {index === 0 ? (
                    <button type="button" className="swap-btn" onClick={swapPlaces}>⇄</button>
                  ) : <div style={{width: '44px'}}></div>}

                  <div className="form-field autocomplete-wrapper">
                    <label className="field-label">{index === 0 ? 'الوجهة' : ''}</label>
                    <div className="input-icon-wrap">
                      <span className="fi">🛬</span>
                      <input type="text" placeholder={index === 0 ? "مثل: لندن، DXB" : "الوجهة"} required className="field-input as-ac" value={slice.destination} onChange={(e) => {
                        const ns = [...slices]; ns[index].destination = e.target.value; setSlices(ns);
                      }} />
                    </div>
                  </div>

                  <div className="form-field">
                    <label className="field-label">{index === 0 ? 'تاريخ (الذهاب)' : ''}</label>
                    <div className="input-icon-wrap">
                      <span className="fi">📅</span>
                      <input type="date" required className="field-input" min={getToday()} value={slice.date} onChange={(e) => {
                        const ns = [...slices]; ns[index].date = e.target.value; setSlices(ns);
                      }} />
                    </div>
                  </div>

                  {index === 0 && tripType === 'roundtrip' && (
                    <div className="form-field">
                      <label className="field-label">تاريخ (العودة)</label>
                      <div className="input-icon-wrap">
                        <span className="fi">📅</span>
                        <input type="date" required className="field-input" min={slices[0].date || getToday()} value={returnDate} onChange={e => setReturnDate(e.target.value)} />
                      </div>
                    </div>
                  )}

                  {index > 0 && tripType === 'multicity' && (
                    <button type="button" className="btn btn-ghost" onClick={() => removeSlice(slice.id)} style={{ color: 'var(--danger)', borderColor: 'var(--danger)', borderRadius: '50%', width: '44px', height: '44px', padding: '0', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>✕</button>
                  )}
                </div>
              ))}
            </div>

            {tripType === 'multicity' && (
              <button type="button" className="btn btn-ghost btn-sm" onClick={addSlice} style={{ display: 'inline-flex', marginBottom: '24px', marginTop: '16px' }}>
                + إضافة رحلة
              </button>
            )}

            <hr className="form-divider" />

            <div className="search-grid search-bottom">
              <div className="form-field">
                <label className="field-label">المسافرون</label>
                <div className="input-icon-wrap">
                  <span className="fi">👤</span>
                  <select name="passengers" className="field-input" defaultValue="1">
                    <option value="1">بالغ واحد</option>
                    <option value="2">بالغان</option>
                    <option value="3">3 بالغين</option>
                    <option value="4">4 بالغين</option>
                    <option value="5">5 بالغين</option>
                  </select>
                </div>
              </div>

              <div className="form-field">
                <label className="field-label">الدرجة</label>
                <div className="input-icon-wrap">
                  <span className="fi">💺</span>
                  <select name="cabin_class" className="field-input" defaultValue="economy">
                    <option value="economy">سياحية</option>
                    <option value="premium_economy">سياحية ممتازة</option>
                    <option value="business">أعمال</option>
                    <option value="first">أولى</option>
                  </select>
                </div>
              </div>
              
              <div className="form-actions-submit">
                  <button type="submit" className="btn btn-primary btn-large search-submit" disabled={loading}>
                      {!loading ? <span className="btn-text">🔍 ابحث عن رحلات</span> : <span className="btn-loader">⏳ جاري البحث...</span>}
                  </button>
              </div>
            </div>
          </form>
        </div>
      </section>

      <section className="features section">
        <div className="container">
          <h2 className="section-title text-center">لماذا تختار <span className="gold">SkyBook</span>؟</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>نتائح فورية</h3>
              <p>آلاف العروض في الوقت الفعلي بفضل واجهة برمجة تطبيقات Duffel.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔍</div>
              <h3>إكمال تلقائي ذكي</h3>
              <p>البحث بسهولة باسم المدينة أو المطار (+ 10 آلاف موقع).</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌍</div>
              <h3>وجهات متعددة</h3>
              <p>أنشئ مسارات معقدة بكل سهولة.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🔒</div>
              <h3>دفع آمن</h3>
              <p>معاملات مشفرة ومتوافقة مع معايير الحماية.</p>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
