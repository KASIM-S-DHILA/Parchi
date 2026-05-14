import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getChallans } from '../api/tally';

export default function ChallanList() {
  const [challans, setChallans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getChallans();
      setChallans(data.challans || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  // Format Tally date YYYYMMDD → DD/MM/YYYY
  const formatDate = (d) => {
    if (!d || d.length < 8) return d;
    return `${d.slice(6, 8)}/${d.slice(4, 6)}/${d.slice(0, 4)}`;
  };

  const getStatusBadgeClass = (status) => {
    switch (status?.toLowerCase()) {
      case 'issued': return 'badge-info';
      case 'delivered': return 'badge-success';
      case 'converted': return 'badge-primary';
      case 'cancelled': return 'badge-danger';
      case 'draft': return 'badge-warning';
      default: return '';
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Challans</h1>
          <p>All Delivery Notes from Tally with local status tracking</p>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn btn-ghost" onClick={load} disabled={loading}>
            {loading ? <span className="spinner" /> : '↻'} Refresh
          </button>
          <Link to="/challans/new" className="btn btn-primary">
            + New Challan
          </Link>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          ⚠ {error}
          <button className="btn btn-ghost btn-sm" onClick={load}>Retry</button>
        </div>
      )}

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Challan No.</th>
              <th>Date</th>
              <th>Status</th>
              <th>Party</th>
              <th>Narration</th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr>
                <td colSpan={5} style={{ textAlign: 'center', padding: '40px' }}>
                  <div className="spinner" style={{ margin: '0 auto' }} />
                </td>
              </tr>
            )}
            {!loading && challans.length === 0 && !error && (
              <tr>
                <td colSpan={5}>
                  <div className="empty-state">
                    <div className="empty-state-icon">📄</div>
                    <h3>No Delivery Notes found</h3>
                    <p>Create your first challan to get started</p>
                    <Link to="/challans/new" className="btn btn-primary" style={{ marginTop: '16px' }}>
                      + New Challan
                    </Link>
                  </div>
                </td>
              </tr>
            )}
            {!loading && challans.map((c, i) => (
              <tr key={i}>
                <td style={{ fontWeight: 600 }}>{c.voucher_number}</td>
                <td>{formatDate(c.date)}</td>
                <td>
                  <span className={`badge ${getStatusBadgeClass(c.status)}`}>
                    {c.status || 'Issued'}
                  </span>
                </td>
                <td>{c.party}</td>
                <td style={{ color: 'var(--text-muted)', fontSize: '0.8125rem' }}>
                  {c.narration || '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
