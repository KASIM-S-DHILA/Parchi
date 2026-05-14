"""
tally/xml_builder.py
--------------------
Builds XML envelopes for every Tally request.

READ envelopes (collections, objects, reports) — used by tally_request()
WRITE envelopes (voucher imports) — used by tally_write()

Rule: No XML is constructed outside this file.
"""

from datetime import date


# ---------------------------------------------------------------------------
# READ — Stock
# ---------------------------------------------------------------------------

def build_stock_items_xml() -> str:
    """
    Fetch all stock items with closing balance, rate, and unit.
    """
    return """<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>Stock Items</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="Stock Items">
            <TYPE>Stock Item</TYPE>
            <FETCH>Name, ClosingBalance, ClosingRate, BaseUnits, Parent</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""


# ---------------------------------------------------------------------------
# READ — Ledgers / Parties
# ---------------------------------------------------------------------------

def build_ledgers_xml(group_filter: str = "Sundry Debtors") -> str:
    """
    Fetch ledgers (parties/customers) filtered by group.
    Default: Sundry Debtors (customers you sell to on credit).
    Pass "Sundry Creditors" to get suppliers.
    Pass "" to get all ledgers.
    """
    filter_xml = ""
    if group_filter:
        filter_xml = f"<FILTER>GroupFilter</FILTER>"
        filter_def = f"""
          <SYSTEM TYPE="Formulae" NAME="GroupFilter">
            $Parent = "{group_filter}"
          </SYSTEM>"""
    else:
        filter_def = ""

    return f"""<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>Ledgers</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="Ledgers">
            <TYPE>Ledger</TYPE>
            <FETCH>Name, Parent, Address, PINCode, CountryName, StateName, GSTRegistrationType, PartyGSTIN, MobileNo</FETCH>
            {filter_xml}
          </COLLECTION>{filter_def}
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""


# ---------------------------------------------------------------------------
# READ — Delivery Notes (existing challans from Tally)
# ---------------------------------------------------------------------------

def build_delivery_notes_xml(from_date: str = "", to_date: str = "") -> str:
    """
    Fetch existing Delivery Note vouchers from Tally.
    from_date / to_date format: "YYYYMMDD" (Tally format)
    """
    date_filter = ""
    if from_date and to_date:
        date_filter = f"""
      <STATICVARIABLES>
        <SVFROMDATE>{from_date}</SVFROMDATE>
        <SVTODATE>{to_date}</SVTODATE>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>"""
    else:
        date_filter = """
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>"""

    return f"""<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>Delivery Notes</ID>
  </HEADER>
  <BODY>
    <DESC>
      {date_filter}
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="Delivery Notes">
            <TYPE>Voucher</TYPE>
            <FETCH>VoucherNumber, Date, PartyLedgerName, Narration, VoucherTypeName</FETCH>
            <FILTER>DeliveryNoteFilter</FILTER>
          </COLLECTION>
          <SYSTEM TYPE="Formulae" NAME="DeliveryNoteFilter">
            $VoucherTypeName = "Delivery Note"
          </SYSTEM>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""


# ---------------------------------------------------------------------------
# WRITE — Create Delivery Note (Challan)
# ---------------------------------------------------------------------------

def build_create_delivery_note_xml(
    challan_number: str,
    challan_date: str,          # "YYYYMMDD"
    party_name: str,
    items: list[dict],          # [{"name": str, "qty": float, "rate": float, "unit": str}]
    narration: str = "",
) -> str:
    """
    Build XML to create a Delivery Note voucher in Tally.
    This is a WRITE operation — used only via tally_write().

    items format:
        [
            {"name": "Item A", "qty": 10, "rate": 500.0, "unit": "Nos"},
            {"name": "Item B", "qty": 5,  "rate": 200.0, "unit": "Kg"},
        ]
    """
    # Build inventory entries (one per item)
    inventory_entries = ""
    for item in items:
        amount = item["qty"] * item["rate"]
        inventory_entries += f"""
      <ALLINVENTORYENTRIES.LIST>
        <STOCKITEMNAME>{item['name']}</STOCKITEMNAME>
        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
        <RATE>{item['rate']} per {item['unit']}</RATE>
        <AMOUNT>-{amount}</AMOUNT>
        <ACTUALQTY>{item['qty']} {item['unit']}</ACTUALQTY>
        <BILLEDQTY>{item['qty']} {item['unit']}</BILLEDQTY>
      </ALLINVENTORYENTRIES.LIST>"""

    total_amount = sum(item["qty"] * item["rate"] for item in items)

    return f"""<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Import</TALLYREQUEST>
    <TYPE>Vouchers</TYPE>
  </HEADER>
  <BODY>
    <DESC/>
    <DATA>
      <TALLYMESSAGE xmlns:UDF="TallyUDF">
        <VOUCHER REMOTEID="{challan_number}" VCHTYPE="Delivery Note" ACTION="Create">
          <DATE>{challan_date}</DATE>
          <NARRATION>{narration or f'Challan No: {challan_number}'}</NARRATION>
          <VOUCHERTYPENAME>Delivery Note</VOUCHERTYPENAME>
          <VOUCHERNUMBER>{challan_number}</VOUCHERNUMBER>
          <PARTYLEDGERNAME>{party_name}</PARTYLEDGERNAME>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>{party_name}</LEDGERNAME>
            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
            <AMOUNT>-{total_amount}</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
          {inventory_entries}
        </VOUCHER>
      </TALLYMESSAGE>
    </DATA>
  </BODY>
</ENVELOPE>"""


# ---------------------------------------------------------------------------
# WRITE — Cancel Delivery Note
# ---------------------------------------------------------------------------

def build_cancel_delivery_note_xml(voucher_number: str, voucher_date: str) -> str:
    """
    Cancel an existing Delivery Note in Tally.
    This is a WRITE operation — used only via tally_write().
    """
    return f"""<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Import</TALLYREQUEST>
    <TYPE>Vouchers</TYPE>
  </HEADER>
  <BODY>
    <DESC/>
    <DATA>
      <TALLYMESSAGE xmlns:UDF="TallyUDF">
        <VOUCHER REMOTEID="{voucher_number}" VCHTYPE="Delivery Note" ACTION="Cancel">
          <DATE>{voucher_date}</DATE>
          <VOUCHERTYPENAME>Delivery Note</VOUCHERTYPENAME>
          <VOUCHERNUMBER>{voucher_number}</VOUCHERNUMBER>
        </VOUCHER>
      </TALLYMESSAGE>
    </DATA>
  </BODY>
</ENVELOPE>"""


# ---------------------------------------------------------------------------
# WRITE — Convert to Sales Bill
# ---------------------------------------------------------------------------

def build_sales_voucher_xml(
    invoice_number: str,
    invoice_date: str,          # "YYYYMMDD"
    party_name: str,
    items: list[dict],          # [{"name": str, "qty": float, "rate": float, "unit": str}]
    narration: str = "",
    ref_challan_number: str = "",
) -> str:
    """
    Build XML to create a Sales voucher in Tally (challan → bill conversion).
    This is a WRITE operation — used only via tally_write().
    """
    inventory_entries = ""
    for item in items:
        amount = item["qty"] * item["rate"]
        inventory_entries += f"""
      <ALLINVENTORYENTRIES.LIST>
        <STOCKITEMNAME>{item['name']}</STOCKITEMNAME>
        <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>
        <RATE>{item['rate']} per {item['unit']}</RATE>
        <AMOUNT>-{amount}</AMOUNT>
        <ACTUALQTY>{item['qty']} {item['unit']}</ACTUALQTY>
        <BILLEDQTY>{item['qty']} {item['unit']}</BILLEDQTY>
      </ALLINVENTORYENTRIES.LIST>"""

    total_amount = sum(item["qty"] * item["rate"] for item in items)
    ref_narration = f"Against Challan: {ref_challan_number}. " if ref_challan_number else ""

    return f"""<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Import</TALLYREQUEST>
    <TYPE>Vouchers</TYPE>
  </HEADER>
  <BODY>
    <DESC/>
    <DATA>
      <TALLYMESSAGE xmlns:UDF="TallyUDF">
        <VOUCHER REMOTEID="{invoice_number}" VCHTYPE="Sales" ACTION="Create">
          <DATE>{invoice_date}</DATE>
          <NARRATION>{ref_narration}{narration}</NARRATION>
          <VOUCHERTYPENAME>Sales</VOUCHERTYPENAME>
          <VOUCHERNUMBER>{invoice_number}</VOUCHERNUMBER>
          <PARTYLEDGERNAME>{party_name}</PARTYLEDGERNAME>
          <ALLLEDGERENTRIES.LIST>
            <LEDGERNAME>{party_name}</LEDGERNAME>
            <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>
            <AMOUNT>-{total_amount}</AMOUNT>
          </ALLLEDGERENTRIES.LIST>
          {inventory_entries}
        </VOUCHER>
      </TALLYMESSAGE>
    </DATA>
  </BODY>
</ENVELOPE>"""
