import { useEffect, useState } from 'react';
import { getEffectiveStock } from '../api/tally';
import './EffectiveStock.css';

export default function EffectiveStock() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState('');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEffectiveStock();
      setItems(data.items || []);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const filtered = items.filter(i =>
    (i.name || '').toLowerCase().includes(search.toLowerCase())
  );

  const lowStockCount   = items.filter(i => i.effective_stock <= 0).length;
  const inChallanCount  = items.filter(i => i.challan_qty > 0).length;
  const totalItems      = items.length;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Effective Stock</h1>
          <p>Live view: Tally stock minus items out on open challans</p>
        </div>
        <button className="btn btn-ghost" onClick={load} disabled={loading}>
          {loading ? <span className="spinner" /> : '↻'} Refresh
        </button>
      </div>

      {/* Summary Stats */}
      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-label">Total Items</span>
          <span className="stat-value">{totalItems}</span>
          <span className="stat-sub">in Tally</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Out on Challan</span>
          <span className="stat-value" style={{ color: 'var(--color-warning)' }}>{inChallanCount}</span>
          <span className="stat-sub">items dispatched, not billed</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Zero / Negative</span>
          <span className="stat-value" style={{ color: 'var(--color-danger)' }}>{lowStockCount}</span>
          <span className="stat-sub">items at or below 0</span>
        </div>
      </div>

      {/* Search */}
      <div className="search-bar">
        <input
          className="input"
          placeholder="Search items..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          id="stock-search"
        />
      </div>

      {/* Error */}
      {error && (
        <div className="error-banner">
          ⚠ {error}
          <button className="btn btn-ghost btn-sm" onClick={load}>Retry</button>
        </div>
      )}

      {/* Table */}
      {!error && (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Item Name</th>
                <th>Tally Stock</th>
                <th>On Challan</th>
                <th>Effective Stock</th>
                <th>Rate</th>
                <th>Unit</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '40px' }}>
                    <div className="spinner" style={{ margin: '0 auto' }} />
                  </td>
                </tr>
              )}
              {!loading && filtered.length === 0 && (
                <tr>
                  <td colSpan={6}>
                    <div className="empty-state">
                      <div className="empty-state-icon">📦</div>
                      <h3>No items found</h3>
                      <p>{search ? 'Try a different search' : 'Make sure Tally is open with a company selected'}</p>
                    </div>
                  </td>
                </tr>
              )}
              {!loading && filtered.map((item, i) => {
                const isLow = item.effective_stock <= 0;
                const hasDispatched = item.challan_qty > 0;
                return (
                  <tr key={i} className={isLow ? 'row-danger' : hasDispatched ? 'row-warning' : ''}>
                    <td className="item-name">{item.name}</td>
                    <td>{item.tally_stock.toFixed(2)}</td>
                    <td>
                      {hasDispatched
                        ? <span className="badge badge-warning">−{item.challan_qty}</span>
                        : <span className="text-muted">—</span>}
                    </td>
                    <td>
                      <span className={`eff-stock ${isLow ? 'danger' : 'normal'}`}>
                        {item.effective_stock.toFixed(2)}
                      </span>
                    </td>
                    <td>₹{item.rate.toLocaleString('en-IN')}</td>
                    <td>{item.unit}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
