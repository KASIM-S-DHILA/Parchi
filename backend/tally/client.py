"""
tally/client.py
---------------
The ONLY module that communicates with Tally Prime XML API.

Two functions:
- tally_request()  → READ operations (safe, no side effects)
- tally_write()    → WRITE operations (controlled, logged, used sparingly)

All XML envelopes are built here. All responses are parsed here.
"""

import requests
import xmltodict
import xml.etree.ElementTree as ET
from typing import Optional
import os
import re
from dotenv import load_dotenv

load_dotenv()

TALLY_HOST = os.getenv("TALLY_HOST", "localhost")
TALLY_PORT = os.getenv("TALLY_PORT", "9000")
TALLY_URL = f"http://{TALLY_HOST}:{TALLY_PORT}"

# Regex for invalid XML characters (including entities like &#4;)
INVALID_XML_RE = re.compile(r'&#(?!(?:10|13|9|32|38|34|39|60|62);)\d+;|[\x00-\x08\x0b\x0c\x0e-\x1f]')


def sanitize_xml(xml_string: str) -> str:
    """
    Remove invalid XML characters that Tally sometimes sends.
    Tally may include control characters like &#4; which break the parser.
    """
    if not xml_string:
        return xml_string
    return INVALID_XML_RE.sub('', xml_string)


# ---------------------------------------------------------------------------
# READ  — safe, no side effects on Tally
# ---------------------------------------------------------------------------

def tally_request(xml_body: str, timeout: int = 10) -> dict:
    """
    Send a read request to Tally and return parsed response as dict.
    Used for: fetching stock items, ledgers, vouchers, reports.

    Args:
        xml_body: Complete XML envelope string to POST to Tally
        timeout:  Seconds to wait before giving up

    Returns:
        Parsed response dict (from XML)

    Raises:
        ConnectionError: If Tally is not reachable
        ValueError:      If Tally returns an error response
    """
    try:
        response = requests.post(
            TALLY_URL,
            data=xml_body.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
            timeout=timeout,
        )
        response.raise_for_status()
        
        # Sanitize before parsing
        sanitized = sanitize_xml(response.text)
        
        # xmltodict converts XML → Python dict
        return xmltodict.parse(sanitized)
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Cannot reach Tally at {TALLY_URL}. "
            "Make sure Tally Prime is open and server mode is enabled."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError("Tally did not respond in time. Is it busy?")


# ---------------------------------------------------------------------------
# WRITE — controlled, must log, used only in 3 places in the entire app
# ---------------------------------------------------------------------------

def tally_write(xml_body: str, operation: str, timeout: int = 15) -> dict:
    """
    Send a write request to Tally (import voucher/master).
    This is the SINGLE GATEWAY for all Tally writes.

    Only called from:
    1. routes/challans.py  → create_challan()
    2. routes/challans.py  → cancel_challan()
    3. routes/challans.py  → convert_to_bill()

    Args:
        xml_body:  Complete XML envelope string to POST to Tally
        operation: Human-readable description for logging ("create_challan", etc.)
        timeout:   Seconds to wait before giving up

    Returns:
        Parsed response dict from Tally

    Raises:
        ConnectionError: If Tally is not reachable
        ValueError:      If Tally returns an error
    """
    print(f"[TALLY WRITE] Operation: {operation}")  # Will be replaced with proper logging later

    try:
        response = requests.post(
            TALLY_URL,
            data=xml_body.encode("utf-8"),
            headers={"Content-Type": "application/xml"},
            timeout=timeout,
        )
        response.raise_for_status()
        
        # Sanitize before parsing
        sanitized = sanitize_xml(response.text)
        result = xmltodict.parse(sanitized)

        # Check for Tally-level errors in the response
        _check_for_tally_error(result, operation)

        print(f"[TALLY WRITE] Success: {operation}")
        return result

    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            f"Cannot reach Tally at {TALLY_URL}. "
            "Make sure Tally Prime is open and server mode is enabled."
        )
    except requests.exceptions.Timeout:
        raise TimeoutError("Tally did not respond in time. Is it busy?")


def _check_for_tally_error(response: dict, operation: str):
    """
    Inspect Tally's response for error indicators.
    Tally doesn't use HTTP error codes for business errors — it embeds them in XML.
    """
    try:
        envelope = response.get("ENVELOPE", {})
        # Tally often returns <LINEERROR> or status 0 on failure
        body = envelope.get("BODY", {})
        if isinstance(body, dict):
            data = body.get("DATA", {})
            if isinstance(data, dict):
                line_error = data.get("LINEERROR")
                if line_error:
                    raise ValueError(f"Tally error during '{operation}': {line_error}")
    except (AttributeError, TypeError):
        pass  # If we can't parse it, let the caller handle it


# ---------------------------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------------------------

def check_tally_connection() -> dict:
    """
    Ping Tally with a minimal request to verify it's alive.
    Returns status info.
    """
    xml = """<ENVELOPE>
  <HEADER>
    <VERSION>1</VERSION>
    <TALLYREQUEST>Export</TALLYREQUEST>
    <TYPE>Collection</TYPE>
    <ID>List of Companies</ID>
  </HEADER>
  <BODY>
    <DESC>
      <STATICVARIABLES>
        <SVEXPORTFORMAT>$$SysName:XML</SVEXPORTFORMAT>
      </STATICVARIABLES>
      <TDL>
        <TDLMESSAGE>
          <COLLECTION NAME="List of Companies">
            <TYPE>Company</TYPE>
            <FETCH>Name</FETCH>
          </COLLECTION>
        </TDLMESSAGE>
      </TDL>
    </DESC>
  </BODY>
</ENVELOPE>"""

    try:
        result = tally_request(xml, timeout=5)
        # Extract company names from response
        companies = []
        try:
            collection = result.get("ENVELOPE", {}).get("BODY", {})
            if collection:
                company_data = collection.get("DATA", {}).get("COLLECTION", {}).get("COMPANY", [])
                if isinstance(company_data, dict):
                    company_data = [company_data]
                companies = [c.get("NAME", "") for c in (company_data or [])]
        except (AttributeError, TypeError):
            pass

        return {
            "connected": True,
            "tally_url": TALLY_URL,
            "companies": companies,
            "message": "Tally is reachable",
        }
    except (ConnectionError, TimeoutError) as e:
        return {
            "connected": False,
            "tally_url": TALLY_URL,
            "companies": [],
            "message": str(e),
        }
