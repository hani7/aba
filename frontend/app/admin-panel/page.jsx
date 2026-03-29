'use client';
import { useState, useEffect } from 'react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch('/api/admin/stats/')
      .then(res => {
        if (!res.ok) throw new Error("Erreur lors de la récupération des données");
        return res.json();
      })
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div className="admin-loader"><div className="spinner"></div><p>Chargement des statistiques...</p></div>;
  if (error) return <div className="admin-error">❌ {error}</div>;

  return (
    <div className="dashboard-wrapper">
      <div className="dashboard-header">
        <h1>Vue d'ensemble</h1>
        <p>Bienvenue sur votre tableau de bord NexaTrade.</p>
      </div>

      <div className="kpi-grid">
        <div className="kpi-card glass-panel gradient-1">
          <div className="kpi-icon">💰</div>
          <div className="kpi-content">
            <h3>Chiffre d'Affaires</h3>
            <p className="kpi-value">{stats?.total_revenue?.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}</p>
            <span className="kpi-trend positive">↑ +12% ce mois</span>
          </div>
        </div>

        <div className="kpi-card glass-panel gradient-2">
          <div className="kpi-icon">✈️</div>
          <div className="kpi-content">
            <h3>Réservations Vols</h3>
            <p className="kpi-value">{stats?.flight_bookings}</p>
            <span className="kpi-sub">{stats?.flight_revenue?.toLocaleString('en-US', { style: 'currency', currency: 'USD' })} générés</span>
          </div>
        </div>

        <div className="kpi-card glass-panel gradient-3">
          <div className="kpi-icon">🏨</div>
          <div className="kpi-content">
            <h3>Réservations Hôtels</h3>
            <p className="kpi-value">{stats?.hotel_bookings}</p>
            <span className="kpi-sub">Profit: {stats?.total_profit?.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}</span>
          </div>
        </div>

        <div className="kpi-card glass-panel gradient-4">
          <div className="kpi-icon">👥</div>
          <div className="kpi-content">
            <h3>Clients Uniques</h3>
            <p className="kpi-value">{stats?.total_clients}</p>
            <span className="kpi-trend positive">↑ +5% nouveautés</span>
          </div>
        </div>
      </div>

      <div className="dashboard-charts">
        <div className="chart-card glass-panel">
          <h3>Activité Récente</h3>
          <div className="chart-placeholder">
            {/* Vous pourriez intégrer Chart.js ou Recharts ici */}
            <div className="bar-graph">
                <div className="bar" style={{height: '40%'}}></div>
                <div className="bar" style={{height: '60%'}}></div>
                <div className="bar" style={{height: '30%'}}></div>
                <div className="bar" style={{height: '80%'}}></div>
                <div className="bar" style={{height: '50%'}}></div>
                <div className="bar" style={{height: '90%'}}></div>
                <div className="bar" style={{height: '70%'}}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
