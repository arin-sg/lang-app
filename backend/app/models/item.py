"""
Item model - represents learnable linguistic items (words, phrases, patterns).
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base


class Item(Base):
    """
    Stores core learnable units.

    Attributes:
        id: Primary key
        type: Type of item (word, phrase, pattern)
        canonical_form: The base or dictionary form of the item
        metadata_json: JSON blob for rich metadata (gender, plural, POS, CEFR level, etc.)
        created_at: Timestamp when the item was created
        updated_at: Timestamp when the item was last updated
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)  # word, chunk, pattern
    canonical_form = Column(Text, nullable=False, index=True)
    metadata_json = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    edges_as_source = relationship("Edge", foreign_keys="Edge.source_id", back_populates="source_item")
    edges_as_target = relationship("Edge", foreign_keys="Edge.target_id", back_populates="target_item")
    encounters = relationship("Encounter", foreign_keys="Encounter.item_id", back_populates="item")

    def __repr__(self):
        return f"<Item(id={self.id}, type={self.type}, canonical_form={self.canonical_form})>"
