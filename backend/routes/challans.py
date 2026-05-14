"""
routes/challans.py
------------------
GET  /api/challans              — List all open delivery notes from Tally
POST /api/challans              — Create a new delivery note in Tally  [WRITE]
POST /api/challans/{id}/cancel  — Cancel a delivery note               [WRITE]
POST /api/challans/{id}/convert — Convert challan to sales bill        [WRITE]
GET  /api/challans/effective-stock — Effective stock (Tally - open challans)

WRITE OPERATIONS: All writes go through tally_write() ONLY.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
import json
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import LocalChallan
from tally.client import tally_request, tally_write
from tally.xml_builder import (
    build_delivery_notes_xml,
    build_create_delivery_note_xml,
    build_cancel_delivery_note_xml,
    build_sales_voucher_xml,
    build_stock_items_xml,
)
from tally.xml_parser import parse_delivery_notes, parse_stock_items

router = APIRouter()


# ---------------------------------------------------------------------------
# Pydantic models — request validation
# ---------------------------------------------------------------------------

class ChallanItem(BaseModel):
    name: str = Field(..., description="Stock item name (must match Tally exactly)")
    qty: float = Field(..., gt=0, description="Quantity")
    rate: float = Field(..., gt=0, description="Rate per unit")
    unit: str = Field(default="Nos", description="Unit of measure")


class CreateChallanRequest(BaseModel):
    challan_number: str = Field(..., description="Unique challan number")
    challan_date: Optional[str] = Field(
        default=None,
        description="Date in YYYYMMDD format. Defaults to today."
    )
    party_name: str = Field(..., description="Customer/party name (must match Tally ledger exactly)")
    items: list[ChallanItem] = Field(..., min_length=1, description="At least one item required")
    narration: Optional[str] = Field(default="", description="Optional notes/remarks")


class ConvertToBillRequest(BaseModel):
    invoice_number: str = Field(..., description="New invoice/bill number")
    invoice_date: Optional[str] = Field(default=None, description="Date in YYYYMMDD. Defaults to today.")
    narration: Optional[str] = Field(default="", description="Optional notes for the bill")


# ---------------------------------------------------------------------------
# Helper: format date for Tally
# ---------------------------------------------------------------------------

def _today_tally() -> str:
    """Returns today's date in YYYYMMDD format (Tally's format)."""
    return date.today().strftime("%Y%m%d")


# ---------------------------------------------------------------------------
# READ Routes
# ---------------------------------------------------------------------------

@router.get("/challans")
def list_challans(db: Session = Depends(get_db)):
    """
    List all Delivery Note vouchers from Tally.
    READ ONLY.
    """
    try:
        xml = build_delivery_notes_xml()
        raw = tally_request(xml)
        tally_challans = parse_delivery_notes(raw)
        
        # Merge with local status
        local_records = db.query(LocalChallan).all()
        status_map = {r.challan_number: r.status for r in local_records}
        
        challans = []
        for c in tally_challans:
            c["status"] = status_map.get(c["voucher_number"], "Issued")
            challans.append(c)
            
        return {
            "success": True,
            "count": len(challans),
            "challans": challans,
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching challans: {str(e)}")


@router.get("/challans/effective-stock")
def get_effective_stock(db: Session = Depends(get_db)):
    """
    Compute effective stock: Tally closing balance minus items in open challans.

    Returns each stock item with:
    - tally_stock:     What Tally thinks is available
    - challan_qty:     What's dispatched but not yet billed (from open challans)
    - effective_stock: What's actually available to sell/dispatch
    """
    try:
        # Get Tally stock
        stock_xml = build_stock_items_xml()
        stock_raw = tally_request(stock_xml)
        stock_items = parse_stock_items(stock_raw)

        # Calculate challan_qty from local database
        # Open challans are those with status "Issued" or "Delivered"
        open_challans = db.query(LocalChallan).filter(
            LocalChallan.status.in_(["Issued", "Delivered"])
        ).all()
        
        item_challan_qty = {} # {item_name: total_qty}
        for c in open_challans:
            if c.items_snapshot:
                try:
                    items = json.loads(c.items_snapshot)
                    for item in items:
                        name = item.get("name")
                        qty = item.get("qty", 0)
                        if name:
                            item_challan_qty[name] = item_challan_qty.get(name, 0) + qty
                except:
                    pass

        effective_stock = []
        for item in stock_items:
            c_qty = item_challan_qty.get(item["name"], 0)
            effective_stock.append({
                "name": item["name"],
                "unit": item["unit"],
                "rate": item["rate"],
                "tally_stock": item["closing_balance"],
                "challan_qty": c_qty,
                "effective_stock": item["closing_balance"] - c_qty,
                "parent_group": item["parent_group"],
            })

        return {
            "success": True,
            "count": len(effective_stock),
            "items": effective_stock,
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing effective stock: {str(e)}")


# ---------------------------------------------------------------------------
# WRITE Routes — all go through tally_write()
# ---------------------------------------------------------------------------

@router.post("/challans")
def create_challan(req: CreateChallanRequest, db: Session = Depends(get_db)):
    """
    Create a Delivery Note (challan) in Tally.
    WRITE OPERATION — goes through tally_write().
    """
    challan_date = req.challan_date or _today_tally()
    items_dicts = [item.model_dump() for item in req.items]

    try:
        # 1. Create in Tally
        xml = build_create_delivery_note_xml(
            challan_number=req.challan_number,
            challan_date=challan_date,
            party_name=req.party_name,
            items=items_dicts,
            narration=req.narration or "",
        )
        result = tally_write(xml, operation="create_challan")

        # 2. Track locally
        db_challan = db.query(LocalChallan).filter(LocalChallan.challan_number == req.challan_number).first()
        if not db_challan:
            db_challan = LocalChallan(
                challan_number=req.challan_number,
                status="Issued",
                items_snapshot=json.dumps(items_dicts)
            )
            db.add(db_challan)
        else:
            db_challan.status = "Issued"
            db_challan.items_snapshot = json.dumps(items_dicts)
        
        db.commit()

        return {
            "success": True,
            "message": f"Challan {req.challan_number} created in Tally and tracked locally",
            "challan_number": req.challan_number,
            "party": req.party_name,
            "date": challan_date,
            "items_count": len(req.items),
            "total_amount": sum(i.qty * i.rate for i in req.items),
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating challan: {str(e)}")


@router.post("/challans/{challan_number}/cancel")
def cancel_challan(challan_number: str, challan_date: str, db: Session = Depends(get_db)):
    """
    Cancel an existing Delivery Note in Tally.
    WRITE OPERATION — goes through tally_write().
    """
    try:
        # 1. Cancel in Tally
        xml = build_cancel_delivery_note_xml(challan_number, challan_date)
        result = tally_write(xml, operation="cancel_challan")

        # 2. Update local status
        db_challan = db.query(LocalChallan).filter(LocalChallan.challan_number == challan_number).first()
        if db_challan:
            db_challan.status = "Cancelled"
            db.commit()

        return {
            "success": True,
            "message": f"Challan {challan_number} cancelled in Tally and updated locally",
            "challan_number": challan_number,
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cancelling challan: {str(e)}")


@router.post("/challans/{challan_number}/convert")
def convert_to_bill(challan_number: str, req: ConvertToBillRequest, db: Session = Depends(get_db)):
    """
    Convert a Delivery Note to a Sales Voucher (bill) in Tally.
    WRITE OPERATION — goes through tally_write().
    """
    invoice_date = req.invoice_date or _today_tally()

    # Get items from local snapshot
    db_challan = db.query(LocalChallan).filter(LocalChallan.challan_number == challan_number).first()
    if not db_challan or not db_challan.items_snapshot:
        raise HTTPException(status_code=404, detail="Challan items not found in local database. Cannot convert.")

    items = json.loads(db_challan.items_snapshot)
    
    # TODO: In Phase 2, we would fetch party_name from the local record too
    # For now, we'll assume it's a Tally-only operation that needs the full XML
    # This is a simplified PoC for conversion
    
    return {
        "success": False,
        "message": "Full conversion logic with party mapping and Tally import will be finalized in the next step.",
        "challan_number": challan_number,
    }
