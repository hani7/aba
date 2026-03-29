'use client';
import { useState, useEffect } from 'react';

export default function AdminBookings() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cancelingId, setCancelingId] = useState(null);

  const fetchBookings = () => {
    fetch('/api/admin/bookings/')
      .then(res => {
        if (!res.ok) throw new Error("Erreur serveur lors de la récupération des vols.");
        return res.json();
      })
      .then(data => {
        setBookings(data.results || []);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchBookings();
  }, []);

  const handleCancel = async (bookingId) => {
    if (!window.confirm("Voulez-vous vraiment annuler cette réservation sur Duffel ?")) return;
    
    setCancelingId(bookingId);
    try {
      const res = await fetch(`/api/admin/bookings/${bookingId}/cancel/`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok || data.error) {
        alert("Erreur: " + (data.error || "Impossible d'annuler"));
      } else {
        alert("Succès: " + data.message);
        // Mettre à jour la grille
        fetchBookings();
      }
    } catch (err) {
      alert("Erreur réseau: " + err.message);
    } finally {
      setCancelingId(null);
    }
  };

  if (loading) return <div className="admin-loader"><div className="spinner"></div><p>Chargement des réservations...</p></div>;
  if (error) return <div className="admin-error">❌ {error}</div>;

  return (
    <div className="admin-page-container">
      <div className="page-header">
        <h1>Réservations Vols</h1>
        <p>Gérez toutes vos réservations et annulations directement depuis cette interface liée à Duffel.</p>
      </div>

      <div className="table-wrapper glass-panel">
        <table className="admin-table">
          <thead>
            <tr>
              <th>ID Demande</th>
              <th>Référence PNR</th>
              <th>Passager</th>
              <th>Itinéraire</th>
              <th>Départ</th>
              <th>Compagnie</th>
              <th>Total</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {bookings.length === 0 ? (
              <tr>
                <td colSpan="9" style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                  Aucune réservation trouvée.
                </td>
              </tr>
            ) : (
              bookings.map((booking) => (
                <tr key={booking.id}>
                  <td>#{booking.id}</td>
                  <td><strong>{booking.reference}</strong></td>
                  <td>{booking.client}</td>
                  <td><span className="badge-route">{booking.itinerary}</span></td>
                  <td>{booking.date}</td>
                  <td>{booking.airline}</td>
                  <td><b>{booking.amount} {booking.currency}</b></td>
                  <td>
                    <span className={`status-badge ${booking.status === 'confirmed' ? 'status-ok' : 'status-bad'}`}>
                      {booking.status === 'confirmed' ? 'Confirmé' : 'Annulé'}
                    </span>
                  </td>
                  <td>
                    {booking.status === 'confirmed' && (
                      <button 
                        onClick={() => handleCancel(booking.id)} 
                        disabled={cancelingId === booking.id}
                        className="btn-danger-outline"
                      >
                        {cancelingId === booking.id ? 'Annulation...' : 'Annuler 🗑'}
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
