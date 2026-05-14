from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="staff") # "owner" or "staff"
    is_active = Column(Boolean, default=True)

class LocalChallan(Base):
    """
    Stores metadata that Tally doesn't.
    """
    __tablename__ = "local_challans"

    id = Column(Integer, primary_key=True, index=True)
    challan_number = Column(String, unique=True, index=True)
    status = Column(String, default="Issued") # Draft, Issued, Delivered, Converted, Cancelled
    items_snapshot = Column(Text, nullable=True) # JSON snapshot for Drafts
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class AppSetting(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(String)
