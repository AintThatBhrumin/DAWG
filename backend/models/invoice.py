# backend/models/invoice.py
"""
SQLAlchemy models for Invoice and Item.
"""

from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(128), index=True, nullable=True)
    vendor_name = Column(String(256), nullable=True)
    buyer_name = Column(String(256), nullable=True)
    date = Column(String(50), nullable=True)  # flexible format
    subtotal = Column(Float, nullable=True)
    tax = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    currency = Column(String(16), nullable=True)
    raw_text = Column(Text, nullable=True)

    items = relationship("Item", back_populates="invoice", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number={self.invoice_number})>"


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(512), nullable=True)
    quantity = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)

    invoice = relationship("Invoice", back_populates="items")

    def __repr__(self):
        return f"<Item(id={self.id}, name={self.name})>"
