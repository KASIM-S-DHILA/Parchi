import pytest
from tally.xml_builder import (
    build_stock_items_xml,
    build_ledgers_xml,
    build_delivery_notes_xml,
    build_create_delivery_note_xml,
    build_cancel_delivery_note_xml,
)

def test_build_stock_items_xml():
    xml = build_stock_items_xml()
    assert "<ID>Stock Items</ID>" in xml
    assert "<TYPE>Stock Item</TYPE>" in xml
    assert "<FETCH>Name, ClosingBalance, ClosingRate, BaseUnits, Parent</FETCH>" in xml

def test_build_ledgers_xml_default():
    xml = build_ledgers_xml()
    assert "<ID>Ledgers</ID>" in xml
    assert '$Parent = "Sundry Debtors"' in xml

def test_build_ledgers_xml_custom():
    xml = build_ledgers_xml(group_filter="Sundry Creditors")
    assert '$Parent = "Sundry Creditors"' in xml

def test_build_ledgers_xml_no_filter():
    xml = build_ledgers_xml(group_filter="")
    assert "<FILTER>GroupFilter</FILTER>" not in xml

def test_build_delivery_notes_xml_no_date():
    xml = build_delivery_notes_xml()
    assert "<ID>Delivery Notes</ID>" in xml
    assert "<SVFROMDATE>" not in xml

def test_build_delivery_notes_xml_with_date():
    xml = build_delivery_notes_xml(from_date="20240101", to_date="20240131")
    assert "<SVFROMDATE>20240101</SVFROMDATE>" in xml
    assert "<SVTODATE>20240131</SVTODATE>" in xml

def test_build_create_delivery_note_xml():
    items = [
        {"name": "Item A", "qty": 10, "rate": 500.0, "unit": "Nos"},
    ]
    xml = build_create_delivery_note_xml(
        challan_number="CH-001",
        challan_date="20240514",
        party_name="Acme Corp",
        items=items,
        narration="Test Narration"
    )
    assert "<VOUCHERNUMBER>CH-001</VOUCHERNUMBER>" in xml
    assert "<DATE>20240514</DATE>" in xml
    assert "<PARTYLEDGERNAME>Acme Corp</PARTYLEDGERNAME>" in xml
    assert "<STOCKITEMNAME>Item A</STOCKITEMNAME>" in xml
    assert "<RATE>500.0 per Nos</RATE>" in xml
    assert "<AMOUNT>-5000.0</AMOUNT>" in xml

def test_build_cancel_delivery_note_xml():
    xml = build_cancel_delivery_note_xml("CH-001", "20240514")
    assert 'ACTION="Cancel"' in xml
    assert "<VOUCHERNUMBER>CH-001</VOUCHERNUMBER>" in xml
    assert "<DATE>20240514</DATE>" in xml
