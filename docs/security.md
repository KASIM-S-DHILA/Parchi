# Parchi — Security Tracker

> This file tracks every security-sensitive aspect of the application. Every feature that touches data, authentication, or Tally writes is documented here with its safety status.

---

## Security Principles

1. **Read-heavy, write-careful** — Reading from Tally is free and constant. Writing requires explicit user confirmation.
2. **Single write gateway** — All Tally writes go through ONE function (`tally_write`). No exceptions.
3. **Data stays local** — No business data ever leaves the customer's machine. The SQLite DB and Tally both live on their hardware.
4. **Encrypted at rest** — SQLite database encrypted with SQLCipher (AES-256).
5. **Defense in depth** — Multiple layers, not a single point of trust.

---

## Tally Write Operations

Only 3 operations in the entire app can write to Tally:

| Operation | Voucher Type | Risk Level | Safety Measures | Status |
|---|---|---|---|---|
| Issue Challan | Delivery Note | 🟡 Medium | Confirmation dialog, duplicate check, activity log | 🔲 Not Built |
| Cancel Challan | Delivery Note (cancel) | 🟡 Medium | Owner-only permission, confirmation dialog, reason required | 🔲 Not Built |
| Convert to Bill | Sales Voucher | 🔴 High | Duplicate voucher search before creation, confirmation with preview, activity log, owner approval option | 🔲 Not Built |

### Write Safety Mechanisms
- [ ] Single `tally_write()` function as the ONLY gateway to Tally
- [ ] Every write requires explicit user confirmation (no auto-writes)
- [ ] Duplicate prevention — search for existing voucher before creating
- [ ] Read-only mode toggle in settings (disables ALL writes)
- [ ] Activity log records every write (who, what, when)
- [ ] Owner can require approval for staff-initiated writes

---

## Authentication & Access

| Feature | Implementation | Risk | Status |
|---|---|---|---|
| Login password | bcrypt hashed, stored in SQLite | Low | 🔲 Not Built |
| 2FA (TOTP) | Optional, stored encrypted in SQLite | Low | 🔲 Not Built |
| Session management | JWT tokens with expiry | Low | 🔲 Not Built |
| Session timeout | Auto-logout after inactivity | Low | 🔲 Not Built |
| Rate limiting on login | Block brute force attempts | Low | 🔲 Not Built |
| Role-based access | Owner vs Staff permissions | Low | 🔲 Not Built |

---

## Database Security

| Feature | Implementation | Risk | Status |
|---|---|---|---|
| SQLCipher encryption | AES-256 encryption on entire .db file | Stolen DB is unreadable | 🔲 Not Built |
| Machine-tied key | Encryption key derived from machine ID | Stolen DB can't open on other machine | 🔲 Not Built |
| Recovery phrase | 12-word phrase shown once during setup | Disaster recovery for new machine | 🔲 Not Built |
| NTFS permissions | App folder restricted to current user | Blocks other Windows users | 🔲 Not Built |
| Sensitive field encryption | AES-256 for API keys, secrets within DB | Extra layer on critical fields | 🔲 Not Built |
| Automatic daily backup | .db file copied to backup folder | Data loss prevention | 🔲 Not Built |

---

## Network & Tunnel Security

| Feature | Implementation | Risk | Status |
|---|---|---|---|
| Cloudflare Tunnel (option 1) | HTTPS via Cloudflare, traffic passes through CF servers | CF can theoretically see data (they won't, but transparency needed) | 🔲 Not Built |
| Tailscale (option 2) | WireGuard E2E encryption, no middleman | Zero trust, maximum privacy | 🔲 Not Built |
| No open inbound ports | Both options use outbound-only connections | Firewall-safe | 🔲 Not Built |
| HTTPS only | All remote access over TLS | Encrypted in transit | 🔲 Not Built |

---

## Data Flow Security Map

```
READ operations (safe — never modify Tally):
  GET stock items      → Tally XML API → Parse → Display
  GET ledgers          → Tally XML API → Parse → Display
  GET vouchers         → Tally XML API → Parse → Display
  GET reports          → Tally XML API → Parse → Display
  GET analytics        → SQLite cache  → Compute → Display

WRITE operations (controlled — all go through tally_write()):
  Issue challan        → Confirm dialog → tally_write() → Tally
  Cancel challan       → Confirm dialog → tally_write() → Tally
  Convert to bill      → Dupe check → Confirm dialog → tally_write() → Tally
```

---

## Honest Risk Disclosure

| Risk | Severity | Mitigation | Acceptable? |
|---|---|---|---|
| Tally's own API has zero authentication | Medium | App adds auth layer; Tally only on localhost | ✅ Yes — same as native Tally |
| Cloudflare Tunnel routes through CF servers | Low | Transparent in docs; Tailscale option available | ✅ Yes — user's choice |
| SQLite file on disk (if unencrypted) | Medium | SQLCipher encryption | ✅ Yes — with encryption |
| Machine physical access | High | Not our problem — same risk as Tally itself | ✅ Yes — out of scope |
| Staff misuse (issuing fake challans) | Medium | Activity log, owner approval, audit trail | ✅ Yes — mitigated |

---

## Security Review Checklist (Pre-Launch)

- [ ] All Tally writes go through `tally_write()` — no exceptions
- [ ] No raw SQL — all queries parameterized (SQLAlchemy/ORM)
- [ ] Passwords never stored in plaintext
- [ ] JWT tokens have reasonable expiry
- [ ] Rate limiting active on login endpoint
- [ ] SQLCipher encryption tested with stolen-file scenario
- [ ] Recovery phrase flow tested end-to-end
- [ ] Read-only mode actually blocks all writes
- [ ] Activity log captures every write operation
- [ ] CORS configured correctly (localhost only for local mode)
- [ ] Cloudflare/Tailscale tunnel tested for data integrity
- [ ] README includes honest security disclosure paragraph
