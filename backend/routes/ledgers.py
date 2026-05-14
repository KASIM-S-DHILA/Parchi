"""
routes/ledgers.py
-----------------
GET /api/ledgers          — All parties (Sundry Debtors by default)
GET /api/ledgers/all      — Every ledger in Tally
GET /api/ledgers/{name}   — Single ledger by name
"""

from fastapi import APIRouter, HTTPException, Query
from tally.client import tally_request
from tally.xml_builder import build_ledgers_xml
from tally.xml_parser import parse_ledgers

router = APIRouter()


@router.get("/ledgers")
def get_ledgers(group: str = Query(default="Sundry Debtors", description="Ledger group to filter by")):
    """
    Fetch ledgers/parties from Tally.
    Default: Sundry Debtors (your customers).
    Pass ?group=Sundry+Creditors for suppliers.
    Pass ?group= to get all ledgers.
    READ ONLY.
    """
    try:
        xml = build_ledgers_xml(group_filter=group)
        raw = tally_request(xml)
        ledgers = parse_ledgers(raw)
        return {
            "success": True,
            "count": len(ledgers),
            "group_filter": group or "All",
            "ledgers": ledgers,
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ledgers: {str(e)}")


@router.get("/ledgers/{ledger_name}")
def get_ledger(ledger_name: str):
    """
    Get a single ledger by name.
    READ ONLY.
    """
    try:
        xml = build_ledgers_xml(group_filter="")  # Search all ledgers
        raw = tally_request(xml)
        ledgers = parse_ledgers(raw)
        matched = [l for l in ledgers if l["name"].lower() == ledger_name.lower()]
        if not matched:
            raise HTTPException(status_code=404, detail=f"Ledger '{ledger_name}' not found")
        return {"success": True, "ledger": matched[0]}
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching ledger: {str(e)}")
