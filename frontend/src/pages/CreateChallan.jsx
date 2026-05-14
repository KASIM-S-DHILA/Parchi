import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getLedgers, getStockItems, createChallan } from '../api/tally';
import './CreateChallan.css';

export default function CreateChallan() {
  const navigate = useNavigate();
  const [ledgers, setLedgers]     = useState([]);
  const [stockItems, setStockItems] = useState([]);
  const [loading, setLoading]     = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError]         = useState(null);
  const [success, setSuccess]     = useState(null);

  // Form state
  const [challanNo, setChallanNo]   = useState('');
  const [party, setParty]           = useState('');
  const [narration, setNarration]   = useState('');
  const [items, setItems]           = useState([
    { name: '', qty: '', rate: '', unit: 'Nos' }
  ]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [ledsData, stockData] = await Promise.all([getLedgers(), getStockItems()]);
        setLedgers(ledsData.ledgers || []);
        setStockItems(stockData.items || []);
      } catch (e) {
        setError(`Failed to load Tally data: ${e.message}`);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Auto-fill rate when item is selected
  const handleItemChange = (index, field, value) => {
    const updated = [...items];
    updated[index][field] = value;
    if (field === 'name') {
      const found = stockItems.find(s => s.name === value);
      if (found) {
        updated[index].rate = found.rate.toString();
        updated[index].unit = found.unit;
      }
    }
    setItems(updated);
  };

  const addItem = () => setItems([...items, { name: '', qty: '', rate: '', unit: 'Nos' }]);

  const removeItem = (i) => {
    if (items.length === 1) return;
    setItems(items.filter((_, idx) => idx !== i));
  };

  const totalAmount = items.reduce((sum, i) => {
    const qty  = parseFloat(i.qty)  || 0;
    const rate = parseFloat(i.rate) || 0;
    return sum + (qty * rate);
  }, 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!challanNo || !party || items.some(i => !i.name || !i.qty || !i.rate)) {
      setError('Please fill all required fields and ensure all items have name, quantity, and rate.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await createChallan({
        challan_number: challanNo,
        party_name: party,
        narration,
        items: items.map(i => ({
          name: i.name,
          qty: parseFloat(i.qty),
          rate: parseFloat(i.rate),
          unit: i.unit || 'Nos',
        })),
      });
      setSuccess(`Challan ${challanNo} created in Tally successfully!`);
      setTimeout(() => navigate('/challans'), 2000);
    } catch (e) {
      setError(`Failed to create challan: ${e.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="page" style={{ alignItems: 'center', justifyContent: 'center', minHeight: '60vh' }}>
        <div className="spinner" style={{ width: 40, height: 40 }} />
        <p>Loading Tally data...</p>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>New Challan</h1>
          <p>Creates a Delivery Note in Tally</p>
        </div>
      </div>

      {success && <div className="success-banner">✓ {success}</div>}
      {error   && <div className="error-banner">⚠ {error}</div>}

      <form onSubmit={handleSubmit} className="challan-form">
        {/* Header section */}
        <div className="card form-section">
          <h3>Challan Details</h3>
          <div className="form-grid">
            <div className="form-group">
              <label className="input-label" htmlFor="challanNo">Challan Number *</label>
              <input
                id="challanNo"
                className="input"
                placeholder="e.g. DC-2024-001"
                value={challanNo}
                onChange={e => setChallanNo(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label className="input-label" htmlFor="party">Party (Customer) *</label>
              <select
                id="party"
                className="input"
                value={party}
                onChange={e => setParty(e.target.value)}
                required
              >
                <option value="">Select customer...</option>
                {ledgers.map((l, i) => (
                  <option key={i} value={l.name}>{l.name}</option>
                ))}
              </select>
            </div>
            <div className="form-group full-width">
              <label className="input-label" htmlFor="narration">Narration / Remarks</label>
              <input
                id="narration"
                className="input"
                placeholder="Optional notes..."
                value={narration}
                onChange={e => setNarration(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Items section */}
        <div className="card form-section">
          <div className="section-header">
            <h3>Items</h3>
            <button type="button" className="btn btn-ghost btn-sm" onClick={addItem}>
              + Add Item
            </button>
          </div>

          <div className="items-list">
            {items.map((item, i) => (
              <div key={i} className="item-row">
                <div className="form-group" style={{ flex: 3 }}>
                  <label className="input-label">Item *</label>
                  <select
                    className="input"
                    value={item.name}
                    onChange={e => handleItemChange(i, 'name', e.target.value)}
                    required
                  >
                    <option value="">Select item...</option>
                    {stockItems.map((s, j) => (
                      <option key={j} value={s.name}>{s.name} (Stock: {s.closing_balance} {s.unit})</option>
                    ))}
                  </select>
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="input-label">Qty *</label>
                  <input
                    className="input"
                    type="number"
                    min="0.001"
                    step="0.001"
                    placeholder="0"
                    value={item.qty}
                    onChange={e => handleItemChange(i, 'qty', e.target.value)}
                    required
                  />
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="input-label">Rate *</label>
                  <input
                    className="input"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                    value={item.rate}
                    onChange={e => handleItemChange(i, 'rate', e.target.value)}
                    required
                  />
                </div>
                <div className="form-group" style={{ flex: 0.7 }}>
                  <label className="input-label">Unit</label>
                  <input className="input" value={item.unit} onChange={e => handleItemChange(i, 'unit', e.target.value)} />
                </div>
                <div className="form-group amount-col">
                  <label className="input-label">Amount</label>
                  <div className="amount-display">
                    ₹{((parseFloat(item.qty) || 0) * (parseFloat(item.rate) || 0)).toLocaleString('en-IN', { minimumFractionDigits: 2 })}
                  </div>
                </div>
                {items.length > 1 && (
                  <button type="button" className="btn btn-danger btn-icon" onClick={() => removeItem(i)} title="Remove">✕</button>
                )}
              </div>
            ))}
          </div>

          <div className="total-row">
            <span>Total Amount</span>
            <span className="total-amount">₹{totalAmount.toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
          </div>
        </div>

        {/* Actions */}
        <div className="form-actions">
          <button type="button" className="btn btn-ghost" onClick={() => navigate('/challans')}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? <><span className="spinner" /> Creating...</> : '✓ Create Challan in Tally'}
          </button>
        </div>
      </form>
    </div>
  );
}
