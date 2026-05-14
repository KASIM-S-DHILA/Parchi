# Parchi — Feature Roadmap

> Tracks every feature with priority, status, and phase.

## Status: 🔲 Planned | 🔨 In Progress | ✅ Done | ❌ Dropped
## Phase: P1 (Proof of Concept) | P2 (Core Product) | P3 (Advanced)

---

## Phase 1 — Proof of Concept

| # | Feature | Description | Status |
|---|---|---|---|
| 1.1 | Tally Connection | FastAPI connects to Tally XML API on localhost:9000 | ✅ |
| 1.2 | Fetch Stock Items | Pull stock items with closing balances | ✅ |
| 1.3 | Fetch Ledgers | Pull sundry debtors (customers) | ✅ |
| 1.4 | Create Challan | Create Delivery Note in Tally | ✅ |
| 1.5 | Effective Stock View | Tally Stock − Open Challans = Available | ✅ |
| 1.6 | Challan List | View all open delivery notes | ✅ |

---

## Phase 2 — Core Product

### Challan Layer
| # | Feature | Status |
|---|---|---|
| 2.1 | Challan Lifecycle (Draft→Issued→Delivered→Converted) | 🔲 |
| 2.2 | Draft Challans (save locally in SQLite) | 🔲 |
| 2.3 | Convert to Bill (with duplicate prevention) | 🔲 |
| 2.4 | Cancel Challan (owner-only) | 🔲 |
| 2.5 | Partial Delivery tracking | 🔲 |
| 2.6 | Return Challan | 🔲 |
| 2.7 | Challan Print/PDF | 🔲 |
| 2.8 | Challan Notes/Remarks | 🔲 |

### Auth & Users
| # | Feature | Status |
|---|---|---|
| 2.9 | Login with bcrypt | 🔲 |
| 2.10 | User Roles (Owner vs Staff) | 🔲 |
| 2.11 | Activity Log | 🔲 |
| 2.12 | Session Timeout | 🔲 |

### Database & Settings
| # | Feature | Status |
|---|---|---|
| 2.13 | SQLite + SQLCipher setup | 🔲 |
| 2.14 | Recovery Phrase (first-time setup) | 🔲 |
| 2.15 | Auto Backup (.db daily copy) | 🔲 |
| 2.16 | Read-Only Mode toggle | 🔲 |
| 2.17 | Tally Connection Config | 🔲 |

---

## Phase 3 — Advanced

### Analytics & Inventory
| # | Feature | Status |
|---|---|---|
| 3.1 | Dashboard (open challans, alerts, activity) | 🔲 |
| 3.2 | ABC Analysis | 🔲 |
| 3.3 | XYZ Analysis | 🔲 |
| 3.4 | ABC-XYZ Matrix | 🔲 |
| 3.5 | Safety Stock Calculation | 🔲 |
| 3.6 | Reorder Alerts | 🔲 |
| 3.7 | Challan Aging alerts | 🔲 |
| 3.8 | Dispatch Patterns | 🔲 |

### Deployment
| # | Feature | Status |
|---|---|---|
| 3.9 | Cloudflare Tunnel | 🔲 |
| 3.10 | Tailscale Option | 🔲 |
| 3.11 | System Tray Icon (🟢🔴🟡) | 🔲 |
| 3.12 | Windows Installer (Inno Setup) | 🔲 |
| 3.13 | Auto-Start on Windows boot | 🔲 |

### Nice to Have
| # | Feature | Status |
|---|---|---|
| 3.14 | 2FA (TOTP) | 🔲 |
| 3.15 | WhatsApp Share | 🔲 |
| 3.16 | Bulk Convert to Bill | 🔲 |
| 3.17 | Historical Analytics | 🔲 |
| 3.18 | Challan History by Party | 🔲 |
| 3.19 | Owner Approval Flow | 🔲 |

---

## Screens by Phase

| Screen | Phase | Key Features |
|---|---|---|
| Challan List | P1 | 1.6, 2.1 |
| Create/Edit Challan | P1 | 1.4, 2.2 |
| Effective Stock | P1 | 1.5 |
| Stock Items | P1 | 1.2 |
| Parties/Ledgers | P1 | 1.3 |
| Setup Wizard | P2 | 2.9, 2.14, 2.17 |
| Login | P2 | 2.9, 2.12 |
| Challan Detail | P2 | 2.1, 2.3, 2.4, 2.7 |
| Activity Log | P2 | 2.11 |
| Settings | P2 | 2.16, 2.17 |
| User Management | P2 | 2.10 |
| Analytics Dashboard | P3 | 3.1–3.8 |
