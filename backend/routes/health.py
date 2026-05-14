"""
routes/health.py
----------------
GET /api/health — Check if Tally is reachable.
The first thing the frontend calls on startup.
"""

from fastapi import APIRouter
from tally.client import check_tally_connection

router = APIRouter()


@router.get("/health")
def health_check():
    """
    Check Tally connection status.
    Returns connected status, Tally URL, and active company names.
    """
    result = check_tally_connection()
    return result
