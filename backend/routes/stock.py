"""
routes/stock.py
---------------
GET /api/stock        — All stock items from Tally with closing balance
GET /api/stock/{name} — Single stock item by name
"""

from fastapi import APIRouter, HTTPException
from tally.client import tally_request
from tally.xml_builder import build_stock_items_xml
from tally.xml_parser import parse_stock_items

router = APIRouter()


@router.get("/stock")
def get_stock_items():
    """
    Fetch all stock items from Tally with closing balances.
    READ ONLY — no Tally state is modified.
    """
    try:
        xml = build_stock_items_xml()
        raw = tally_request(xml)
        items = parse_stock_items(raw)
        return {
            "success": True,
            "count": len(items),
            "items": items,
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock: {str(e)}")


@router.get("/stock/{item_name}")
def get_stock_item(item_name: str):
    """
    Get a single stock item by name.
    Fetches all items and filters — Tally's XML API doesn't support single-item fetch cleanly.
    READ ONLY.
    """
    try:
        xml = build_stock_items_xml()
        raw = tally_request(xml)
        items = parse_stock_items(raw)
        matched = [i for i in items if i["name"].lower() == item_name.lower()]
        if not matched:
            raise HTTPException(status_code=404, detail=f"Stock item '{item_name}' not found")
        return {"success": True, "item": matched[0]}
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stock item: {str(e)}")
