# Parchi — Decisions Log

> Key decisions made and WHY. If a question comes up that's already answered here — point to this file instead of re-discussing.

---

## Decision Format
Each entry records: **What** was decided, **Why**, **Alternatives considered**, and **Date**.

---

## D1: App runs entirely on customer's machine (no cloud)
- **Date:** 2026-05-12
- **Decision:** The app is a downloadable installer. FastAPI + React + SQLite all run on the customer's always-on Windows machine. No cloud server, no VPS.
- **Why:** Customer owns their data completely. Zero hosting cost for us. Simpler architecture. Businesses trust local software more.
- **Alternatives considered:**
  - SaaS with cloud relay + WebSocket agent → too complex, requires VPS cost
  - Cloud-hosted with data sync → contradicts "no data on backend" goal
- **Status:** ✅ Final

## D2: Tally's Delivery Note = Challan
- **Date:** 2026-05-12
- **Decision:** Challans are stored as "Delivery Note" voucher type in Tally, not in a separate database.
- **Why:** Tally already has this voucher type built in. It reduces stock immediately when created. No duplicate data. Tally remains single source of truth.
- **Alternatives considered:**
  - Store challans only in SQLite → Tally stock wouldn't update, defeats the purpose
- **Status:** ✅ Final

## D3: FastAPI as backend (not Flask)
- **Date:** 2026-05-12
- **Decision:** Use FastAPI instead of Flask.
- **Why:** Async support (important for Tally XML calls that can be slow), automatic OpenAPI docs, faster, modern Python.
- **Alternatives considered:**
  - Flask → familiar to Kasim but lacks async, slower
  - Express.js → would need two languages (JS + Python for analytics)
- **Status:** ✅ Final

## D4: React + Vite as frontend
- **Date:** 2026-05-12
- **Decision:** React with Vite for the frontend.
- **Why:** Fast dev server, modern tooling, rich UI capabilities, large ecosystem.
- **Alternatives considered:**
  - Electron → heavier, unnecessary since we serve via browser
  - Next.js → SSR not needed for local app
- **Status:** ✅ Final

## D5: SQLite + SQLCipher for local database
- **Date:** 2026-05-14
- **Decision:** Add a local SQLite database encrypted with SQLCipher.
- **Why:** Tally can't store app-specific data (challan status, user accounts, settings, analytics cache). SQLite is zero-config, single file, encrypted. Bundled with Python.
- **Alternatives considered:**
  - No database at all → can't track challan status, no auth, no settings
  - PostgreSQL → overkill, requires separate install
- **Status:** ✅ Final

## D6: Remote access via Cloudflare Tunnel OR Tailscale (user chooses)
- **Date:** 2026-05-13
- **Decision:** Offer both options during install. Cloudflare for ease, Tailscale for maximum privacy.
- **Why:** Different businesses have different privacy comfort levels. Cloudflare = open in any browser. Tailscale = E2E encrypted, no middleman.
- **Alternatives considered:**
  - Cloudflare only → some businesses uncomfortable with traffic routing through CF
  - Tailscale only → requires app install on every device
  - Port forwarding → too technical for SME users
- **Status:** ✅ Final

## D7: Read-heavy, write-careful design
- **Date:** 2026-05-14
- **Decision:** Only 3 Tally write operations exist (issue challan, cancel challan, convert to bill). All go through single `tally_write()` function. Read-only mode toggle available.
- **Why:** Tally data corruption = business loss. Minimizing writes = minimizing risk. Single write gateway = easy to audit and control.
- **Alternatives considered:**
  - Free read/write → too risky for business data
- **Status:** ✅ Final

## D8: Open source with hosted option later
- **Date:** 2026-05-13
- **Decision:** Code is open source on GitHub. Self-hosting is free. Paid hosted version can come later.
- **Why:** Builds trust (businesses can read agent code). Community contributions. Viral adoption. Competitors charge ₹5K-15K/year for similar tools.
- **Alternatives considered:**
  - Closed source SaaS → less trust, harder adoption for a new product
- **Status:** ✅ Final

## D9: Machine must run 24/7 with Tally open
- **Date:** 2026-05-12
- **Decision:** This is a stated requirement for customers. Their Tally machine must be always-on.
- **Why:** The app needs Tally to be running to serve requests. Most shops already have a PC that stays on.
- **Status:** ✅ Final — documented as product requirement

## D10: Paper to digital — app must be staff-friendly
- **Date:** 2026-05-14
- **Decision:** Current process is handwritten paper challans. The app replaces this entirely. UI must be simple enough for non-technical staff.
- **Why:** Owner + 1-2 staff use the app. Staff adoption is critical. Complex UI = staff won't use it = product fails.
- **Status:** ✅ Final — impacts all UI decisions
