import pytest
from tally.xml_parser import (
    parse_stock_items,
    parse_ledgers,
    parse_delivery_notes,
    _parse_qty_unit,
    _parse_rate,
)

def test_parse_qty_unit():
    assert _parse_qty_unit("10.00 Nos") == (10.0, "Nos")
    assert _parse_qty_unit(" 5.50 Kg ") == (5.5, "Kg")
    assert _parse_qty_unit("invalid") == (0.0, "Nos")

def test_parse_rate():
    assert _parse_rate("500.00 per Nos") == 500.0
    assert _parse_rate("1,200.50 per Kg") == 1200.5
    assert _parse_rate("invalid") == 0.0

def test_parse_stock_items():
    raw = {
        "ENVELOPE": {
            "BODY": {
                "DATA": {
                    "COLLECTION": {
                        "STOCKITEM": [
                            {
                                "NAME": "Item A",
                                "CLOSINGBALANCE": "10 Nos",
                                "CLOSINGRATE": "500 per Nos",
                                "PARENT": "Electronics"
                            },
                            {
                                "NAME": "Item B",
                                "CLOSINGBALANCE": "5 Kg",
                                "CLOSINGRATE": "200 per Kg",
                                "PARENT": "Raw Materials"
                            }
                        ]
                    }
                }
            }
        }
    }
    items = parse_stock_items(raw)
    assert len(items) == 2
    assert items[0]["name"] == "Item A"
    assert items[0]["closing_balance"] == 10.0
    assert items[0]["unit"] == "Nos"
    assert items[1]["name"] == "Item B"
    assert items[1]["parent_group"] == "Raw Materials"

def test_parse_stock_items_single():
    raw = {
        "ENVELOPE": {
            "BODY": {
                "DATA": {
                    "COLLECTION": {
                        "STOCKITEM": {
                            "NAME": "Item A",
                            "CLOSINGBALANCE": "10 Nos",
                            "CLOSINGRATE": "500 per Nos",
                            "PARENT": "Electronics"
                        }
                    }
                }
            }
        }
    }
    items = parse_stock_items(raw)
    assert len(items) == 1
    assert items[0]["name"] == "Item A"

def test_parse_ledgers():
    raw = {
        "ENVELOPE": {
            "BODY": {
                "DATA": {
                    "COLLECTION": {
                        "LEDGER": [
                            {
                                "NAME": "Acme Corp",
                                "PARENT": "Sundry Debtors",
                                "ADDRESS": {"ADDRESS.LIST": ["123 Street", "City"]},
                                "PARTYGSTIN": "27AAACA1234A1Z1",
                                "STATENAME": "Maharashtra"
                            }
                        ]
                    }
                }
            }
        }
    }
    ledgers = parse_ledgers(raw)
    assert len(ledgers) == 1
    assert ledgers[0]["name"] == "Acme Corp"
    assert ledgers[0]["address"] == ["123 Street", "City"]
    assert ledgers[0]["gstin"] == "27AAACA1234A1Z1"

def test_parse_delivery_notes():
    raw = {
        "ENVELOPE": {
            "BODY": {
                "DATA": {
                    "COLLECTION": {
                        "VOUCHER": [
                            {
                                "VOUCHERNUMBER": "CH-001",
                                "DATE": "20240514",
                                "PARTYLEDGERNAME": "Acme Corp",
                                "NARRATION": "Test"
                            }
                        ]
                    }
                }
            }
        }
    }
    notes = parse_delivery_notes(raw)
    assert len(notes) == 1
    assert notes[0]["voucher_number"] == "CH-001"
    assert notes[0]["party"] == "Acme Corp"
