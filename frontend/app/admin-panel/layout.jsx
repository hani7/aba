'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState, useEffect } from 'react';

export default function AdminLayout({ children }) {
  const pathname = usePathname();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (localStorage.getItem('admin_nexa_auth') === 'true') {
      setIsAuthenticated(true);
    }
  }, []);

  const handleLogin = (e) => {
    e.preventDefault();
    if (password === 'admin123') {
      setIsAuthenticated(true);
      localStorage.setItem('admin_nexa_auth', 'true');
      setError('');
    } else {
      setError('Mot de passe incorrect');
    }
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('admin_nexa_auth');
    setPassword('');
  };

  const links = [
    { name: 'Dashboard', href: '/admin-panel', icon: '📊' },
    { name: 'Réservations', href: '/admin-panel/bookings', icon: '✈️' },
    { name: 'Clients', href: '/admin-panel/clients', icon: '👥' },
    { name: 'Retour au site', href: '/', icon: '🏠' },
  ];

  if (!isAuthenticated && pathname.startsWith('/admin-panel')) {
    return (
      <div className="admin-login-container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#0f172a' }}>
        <form onSubmit={handleLogin} className="glass-panel" style={{ padding: '2.5rem', borderRadius: '1rem', width: '100%', maxWidth: '400px', textAlign: 'center', border: '1px solid rgba(255,255,255,0.1)' }}>
          <h2 style={{ marginBottom: '1.5rem', color: '#f8fafc', fontSize: '1.5rem', fontWeight: 'bold' }}>
            <span style={{ marginRight: '0.5rem' }}>🔒</span> 
            Connexion Admin
          </h2>
          {error && <p style={{ color: '#ef4444', marginBottom: '1rem', fontSize: '0.9rem' }}>{error}</p>}
          <div style={{ marginBottom: '1.5rem' }}>
            <input 
              type="password" 
              placeholder="Mot de passe" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: '100%', padding: '0.75rem 1rem', borderRadius: '0.5rem', border: '1px solid #334155', background: '#1e293b', color: '#fff', outline: 'none' }}
              required
            />
          </div>
          <button type="submit" style={{ width: '100%', padding: '0.75rem', background: '#3b82f6', color: '#fff', border: 'none', borderRadius: '0.5rem', cursor: 'pointer', fontWeight: 'bold', transition: 'background 0.2s' }} onMouseOver={(e) => e.target.style.background = '#2563eb'} onMouseOut={(e) => e.target.style.background = '#3b82f6'}>
            Se connecter
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="admin-container" dir="ltr">
      {/* Sidebar */}
      <aside className="admin-sidebar glass-panel">
        <div className="sidebar-header">
          <h2 className="admin-brand">
            <span className="brand-icon">🌟</span>
            NexaAdmin
          </h2>
        </div>
        
        <nav className="sidebar-nav">
          {links.map((link) => {
            const isActive = pathname === link.href || (pathname.startsWith(link.href) && link.href !== '/admin-panel' && link.href !== '/');
            return (
              <Link 
                key={link.name} 
                href={link.href} 
                className={`nav-link ${isActive ? 'active' : ''}`}
              >
                <span className="nav-icon">{link.icon}</span>
                <span className="nav-text">{link.name}</span>
              </Link>
            );
          })}
        </nav>
        
        <div className="sidebar-footer">
          <div className="admin-profile" style={{ display: 'flex', alignItems: 'center', width: '100%' }}>
            <div className="avatar">AD</div>
            <div className="admin-info">
              <strong>Admin User</strong>
              <span>Gestionnaire</span>
            </div>
            <button 
              onClick={handleLogout} 
              style={{ marginLeft: 'auto', background: 'transparent', border: 'none', cursor: 'pointer', fontSize: '1.2rem'}} 
              title="Déconnexion"
            >
              🚪
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="admin-main">
        <header className="admin-header glass-panel">
          <div className="header-search">
            <span className="search-icon">🔍</span>
            <input type="text" placeholder="Rechercher (Réservation, Client...)" className="search-input" />
          </div>
          <div className="header-actions">
            <button className="action-btn">🔔</button>
            <button className="action-btn">⚙️</button>
          </div>
        </header>
        
        <div className="admin-content">
          {children}
        </div>
      </main>
    </div>
  );
}
