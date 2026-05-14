# Parchi

Delivery Challan Management & Inventory Optimization on top of TallyPrime.

## Quick Start

### 1. Backend
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173

### Requirements
- TallyPrime running with server mode enabled (port 9000)
- Python 3.11+
- Node.js 18+

## Docs
See `/docs` folder for architecture, features, decisions, security, and session handoff.