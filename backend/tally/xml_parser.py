"""
tally/xml_parser.py
-------------------
Parses raw Tally XML responses (already converted to dicts by xmltodict)
into clean Python dicts that the API routes can return as JSON.

Rule: All messy XML → clean JSON transformation lives here.
"""

from typing import Optional, Any
import re


def parse_stock_items(raw: dict) -> list[dict]:
    """
    Parse the stock items collection response from Tally.

    Returns list of:
    {
        "name": str,
        "closing_balance": float,
        "unit": str,
        "rate": float,
        "parent_group": str,
    }
    """
    items = []
    try:
        collection = (
            raw.get("ENVELOPE", {})
               .get("BODY", {})
               .get("DATA", {})
               .get("COLLECTION", {})
               .get("STOCKITEM", [])
        )
        if isinstance(collection, dict):
            collection = [collection]  # Single item comes as dict, not list

        for item in (collection or []):
            name = _get_text(item.get("NAME") or item.get("@NAME", ""))
            closing_raw = _get_text(item.get("CLOSINGBALANCE", "0 Nos"))
            qty, unit = _parse_qty_unit(closing_raw)
            rate_raw = _get_text(item.get("CLOSINGRATE", "0 per Nos"))
            rate = _parse_rate(rate_raw)

            items.append({
                "name": name,
                "closing_balance": qty,
                "unit": unit,
                "rate": rate,
                "parent_group": _get_text(item.get("PARENT", "")),
            })
    except (AttributeError, TypeError, KeyError):
        pass

    return items


def parse_ledgers(raw: dict) -> list[dict]:
    """
    Parse the ledgers collection response from Tally.

    Returns list of:
    {
        "name": str,
        "group": str,
        "address": list[str],
        "gstin": str,
        "mobile": str,
        "state": str,
    }
    """
    ledgers = []
    try:
        collection = (
            raw.get("ENVELOPE", {})
               .get("BODY", {})
               .get("DATA", {})
               .get("COLLECTION", {})
               .get("LEDGER", [])
        )
        if isinstance(collection, dict):
            collection = [collection]

        for led in (collection or []):
            name = _get_text(led.get("NAME") or led.get("@NAME", ""))
            # Address can be a string or a list
            address_raw = led.get("ADDRESS", {})
            addr_list = []
            if isinstance(address_raw, dict):
                addr_list = address_raw.get("ADDRESS.LIST", [])
                if isinstance(addr_list, str):
                    addr_list = [addr_list]
                elif isinstance(addr_list, list):
                    addr_list = [_get_text(a) for a in addr_list]
            elif isinstance(address_raw, str):
                addr_list = [address_raw]
            elif isinstance(address_raw, list):
                addr_list = [_get_text(a) for a in address_raw]

            ledgers.append({
                "name": name,
                "group": _get_text(led.get("PARENT", "")),
                "address": addr_list,
                "gstin": _get_text(led.get("PARTYGSTIN", "")),
                "mobile": _get_text(led.get("MOBILENO", "")),
                "state": _get_text(led.get("STATENAME", "")),
                "pin": _get_text(led.get("PINCODE", "")),
            })
    except (AttributeError, TypeError, KeyError):
        pass

    return ledgers


def parse_delivery_notes(raw: dict) -> list[dict]:
    """
    Parse existing Delivery Notes from Tally.

    Returns list of:
    {
        "voucher_number": str,
        "date": str,
        "party": str,
        "narration": str,
    }
    """
    notes = []
    try:
        collection = (
            raw.get("ENVELOPE", {})
               .get("BODY", {})
               .get("DATA", {})
               .get("COLLECTION", {})
               .get("VOUCHER", [])
        )
        if isinstance(collection, dict):
            collection = [collection]

        for v in (collection or []):
            vnum = _get_text(v.get("VOUCHERNUMBER") or v.get("@VOUCHERNUMBER", ""))
            notes.append({
                "voucher_number": vnum,
                "date": _get_text(v.get("DATE", "")),
                "party": _get_text(v.get("PARTYLEDGERNAME", "")),
                "narration": _get_text(v.get("NARRATION", "")),
            })
    except (AttributeError, TypeError, KeyError):
        pass

    return notes


def parse_companies(raw: dict) -> list[str]:
    """
    Parse company list from Tally (used for health check).
    """
    companies = []
    try:
        collection = (
            raw.get("ENVELOPE", {})
               .get("BODY", {})
               .get("DATA", {})
               .get("COLLECTION", {})
               .get("COMPANY", [])
        )
        if isinstance(collection, dict):
            collection = [collection]
        for c in (collection or []):
            name = _get_text(c.get("NAME") or c.get("@NAME", ""))
            if name:
                companies.append(name)
    except (AttributeError, TypeError, KeyError):
        pass
    return companies


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_text(value: Any) -> str:
    """
    Extract text value from Tally's xmltodict structure.
    Tally sometimes returns a string, sometimes a dict with '#text'.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return str(value.get("#text", "")).strip()
    return str(value).strip()


def _parse_qty_unit(raw: str) -> tuple[float, str]:
    """
    Parse Tally quantity strings like "10.00 Nos" or "5.50 Kg".
    Returns (quantity_float, unit_string)
    """
    try:
        parts = str(raw).strip().split()
        if not parts:
            return 0.0, "Nos"
        qty = float(parts[0].replace(",", ""))
        unit = parts[1] if len(parts) > 1 else "Nos"
        return qty, unit
    except (ValueError, IndexError):
        return 0.0, "Nos"


def _parse_rate(raw: str) -> float:
    """
    Parse Tally rate strings like "500.00 per Nos" or "500.00/nos".
    Returns the rate as a float.
    """
    try:
        raw_str = str(raw).strip()
        if not raw_str:
            return 0.0
        parts = re.split(r'[\s/]', raw_str)
        return float(parts[0].replace(",", ""))
    except (ValueError, IndexError):
        return 0.0
