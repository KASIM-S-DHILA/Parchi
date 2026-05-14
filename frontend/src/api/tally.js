/**
 * api/tally.js
 * All API calls to the FastAPI backend in one place.
 * The backend proxies everything to Tally.
 */

const BASE = '/api';

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || `API error: ${res.status}`);
  }
  return data;
}

// Health
export const checkHealth    = ()      => request('/health');

// Stock
export const getStockItems  = ()      => request('/stock');
export const getStockItem   = (name)  => request(`/stock/${encodeURIComponent(name)}`);

// Ledgers
export const getLedgers     = (group = 'Sundry Debtors') =>
  request(`/ledgers?group=${encodeURIComponent(group)}`);

// Challans
export const getChallans    = ()      => request('/challans');
export const getEffectiveStock = ()   => request('/challans/effective-stock');

export const createChallan  = (payload) =>
  request('/challans', { method: 'POST', body: JSON.stringify(payload) });

export const cancelChallan  = (challanNumber, challanDate) =>
  request(`/challans/${encodeURIComponent(challanNumber)}/cancel?challan_date=${challanDate}`, {
    method: 'POST',
  });
