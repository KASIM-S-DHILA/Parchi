# Parchi — Architecture

> This file documents the finalized architecture. These decisions are SETTLED — do not re-discuss unless a concrete technical problem requires it.

---

## Product Summary

**Parchi** is a downloadable desktop application that adds a delivery challan management layer on top of TallyPrime. It solves the "physical stock ≠ Tally stock" gap that exists between issuing a challan and converting it to a bill.

**Target Users:** Indian SME businesses using TallyPrime Gold or Silver who issue delivery challans.

---

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│              Customer's Always-On Machine            │
│                                                     │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │ React (Vite) │◄──►│   FastAPI Backend         │   │
│  │  Frontend    │    │   (JSON ↔ XML translator) │   │
│  │  localhost:   │    │   localhost:8000           │   │
│  │  5173        │    │                            │   │
│  └──────────────┘    └─────────┬────────────────┘   │
│                                │                     │
│                     ┌──────────▼──────────┐          │
│                     │  TallyPrime Server  │          │
│                     │  localhost:9000     │          │
│                     │  (Source of Truth)  │          │
│                     └────────────────────┘          │
│                                                     │
│  ┌──────────────┐    ┌──────────────────────────┐   │
│  │  SQLite DB   │    │  Cloudflare Tunnel OR    │   │
│  │  (SQLCipher) │    │  Tailscale (remote       │   │
│  │  Local only  │    │  access, user's choice)  │   │
│  └──────────────┘    └──────────────────────────┘   │
│                                                     │
│  ┌──────────────┐                                   │
│  │ System Tray  │  ← Status: 🟢 Tally connected    │
│  │ Icon         │            🔴 Tally offline       │
│  └──────────────┘            🟡 Reconnecting        │
└─────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **Frontend** | React + Vite | Fast, modern, rich UI capability |
| **Backend** | FastAPI (Python) | Async, fast, great for XML↔JSON translation |
| **Database** | SQLite + SQLCipher | Zero config, single file, encrypted, bundled with Python |
| **Tally API** | XML over HTTP POST to localhost:9000 | Tally's native integration protocol |
| **Remote Access** | Cloudflare Tunnel OR Tailscale | User chooses during install |
| **System Tray** | pystray (Python) | Lightweight status indicator |
| **Installer** | Inno Setup | Industry standard Windows installer |
| **Packaging** | PyInstaller (for .exe) | Bundles Python + FastAPI into single executable |

---

## Data Architecture

### What Lives WHERE

| Data | Storage | Why |
|---|---|---|
| Stock quantities & balances | **Tally** (live read) | Source of truth, always fresh |
| Ledgers / Parties | **Tally** (live read) | Source of truth |
| Vouchers (bills, payments) | **Tally** (live read) | Source of truth |
| Delivery Notes (challans in Tally) | **Tally** (read + write) | Created by app, stored in Tally |
| Challan status (Draft/Issued/Delivered/Converted) | **SQLite** | Tally has no status concept |
| App settings, tunnel config | **SQLite** | App-specific |
| User credentials (hashed), 2FA | **SQLite** | Security layer |
| Analytics cache / snapshots | **SQLite** | Performance — avoids repeated Tally calls |
| Activity log | **SQLite** | Audit trail |
| Alert thresholds, notifications | **SQLite** | App-specific |

### Effective Stock Formula
```
Effective Stock = Tally Closing Balance − Open Challan Quantity (from SQLite)
```
This is the core value proposition. Tally knows the "book stock." SQLite knows the "dispatched but not billed" stock. The app shows the real available stock.

---

## Key API Flow

### Reading from Tally (safe, no side effects)
```
React → GET /api/stock-items → FastAPI → XML request → Tally:9000 → XML response → JSON → React
```

### Writing to Tally (controlled, single gateway)
```
React → POST /api/challan → FastAPI → Confirmation check → Duplicate check →
  tally_write() → XML import → Tally:9000 → Response → Log to SQLite → JSON → React
```

---

## Deployment Model

**Self-hosted on customer's own hardware.** No cloud, no VPS, no monthly cost from us.

1. Customer downloads one `.exe` installer
2. Installs on their always-on Windows machine (same machine or network as Tally)
3. Chooses Cloudflare Tunnel or Tailscale for remote access
4. Opens browser on any device → accesses their Parchi instance
5. Everything runs locally — data never leaves their machine

---

## Folder Structure (Planned)

```
Parchi/
├── backend/                  # FastAPI application
│   ├── main.py               # FastAPI app entry point
│   ├── tally/                # Tally XML integration
│   │   ├── client.py         # tally_request() and tally_write()
│   │   ├── xml_builder.py    # XML envelope construction
│   │   └── xml_parser.py     # XML response parsing
│   ├── routes/               # API route handlers
│   │   ├── health.py         # Tally connection check
│   │   ├── stock.py          # Stock items endpoints
│   │   ├── ledgers.py        # Ledger/party endpoints
│   │   ├── challans.py       # Challan CRUD
│   │   └── analytics.py      # Analytics endpoints
│   ├── db/                   # SQLite database layer
│   │   ├── database.py       # SQLCipher connection
│   │   ├── models.py         # Table definitions
│   │   └── migrations/       # Schema migrations
│   └── requirements.txt
├── frontend/                 # React + Vite application
│   ├── src/
│   │   ├── pages/            # Screen components
│   │   ├── components/       # Reusable UI components
│   │   ├── api/              # API client functions
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
├── installer/                # Inno Setup scripts
├── docs/                     # Documentation
│   ├── handoff.md
│   ├── security.md
│   ├── ARCHITECTURE.md
│   ├── FEATURES.md
│   └── DECISIONS.md
├── Challan.json              # Original product discussion
└── tally.xml                 # Tally API reference
```
