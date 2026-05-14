import { NavLink, Outlet } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { checkHealth } from '../api/tally';
import './Layout.css';

export default function Layout() {
  const [status, setStatus] = useState({ connected: null, companies: [] });

  useEffect(() => {
    const poll = async () => {
      try {
        const data = await checkHealth();
        // Defensive check: ensure companies is an array
        const sanitized = {
          connected: !!data.connected,
          companies: Array.isArray(data.companies) ? data.companies : []
        };
        setStatus(sanitized);
      } catch (err) {
        console.error('Health check failed', err);
        setStatus({ connected: false, companies: [] });
      }
    };
    poll();
    const interval = setInterval(poll, 15000);
    return () => clearInterval(interval);
  }, []);

  const dotClass = status.connected === null
    ? 'loading'
    : status.connected ? 'connected' : 'disconnected';

  const companyName = status.companies && status.companies.length > 0
    ? (typeof status.companies[0] === 'string' ? status.companies[0] : status.companies[0]['#text'] || 'Tally Connected')
    : 'Tally Connected';

  const statusText = status.connected === null
    ? 'Checking...'
    : status.connected
      ? companyName
      : 'Tally Not Reachable';

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="brand-icon">📋</span>
          <span className="brand-name">Parchi</span>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <span>⚡</span> Effective Stock
          </NavLink>
          <NavLink to="/challans" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <span>📄</span> Challans
          </NavLink>
          <NavLink to="/challans/new" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
            <span>➕</span> New Challan
          </NavLink>
        </nav>

        <div className="sidebar-footer">
          <div className="tally-status">
            <span className={`status-dot ${dotClass}`} />
            <span className="status-label" title={statusText}>{statusText}</span>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
