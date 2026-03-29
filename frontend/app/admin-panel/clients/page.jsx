'use client';
import { useState, useEffect } from 'react';

export default function AdminClients() {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/admin/clients/')
      .then(res => {
        if (!res.ok) throw new Error("Erreur serveur");
        return res.json();
      })
      .then(data => {
        setClients(data.results || []);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="admin-loader"><div className="spinner"></div><p>Chargement des clients...</p></div>;
  if (error) return <div className="admin-error">❌ {error}</div>;

  return (
    <div className="admin-page-container">
      <div className="page-header">
        <h1>Liste de vos Clients</h1>
        <p>Gérez vos passagers et analysez leur fidélité.</p>
      </div>

      <div className="table-wrapper glass-panel">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Client (Passager)</th>
              <th>Adresse E-mail</th>
              <th>Numéro de Téléphone</th>
              <th>Total des Vols</th>
              <th>Statut Client</th>
            </tr>
          </thead>
          <tbody>
            {clients.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: '#666' }}>
                  Aucun client trouvé pour le moment.
                </td>
              </tr>
            ) : (
              clients.map((client, idx) => (
                <tr key={idx}>
                  <td><strong>{client.name}</strong></td>
                  <td><a href={`mailto:${client.email}`} className="email-link">{client.email}</a></td>
                  <td>{client.phone || '-'}</td>
                  <td>
                     <span className="flight-count-badge">{client.bookings_count}</span>
                  </td>
                  <td>
                    {client.bookings_count > 2 ? (
                       <span className="status-badge status-vip">🌟 VIP</span>
                    ) : (
                       <span className="status-badge status-standard">Standard</span>
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
