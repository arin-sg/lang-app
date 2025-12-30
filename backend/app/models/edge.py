"""
Edge model - represents relationships between items.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import Base


class Edge(Base):
    """
    Stores relationships between items.

    Attributes:
        id: Primary key
        source_id: Foreign key to items.id
        target_id: Foreign key to items.id
        relation_type: Type of relationship (collocates_with, confusable_with, governs_case, etc.)
        weight: Optional weight for the relationship strength (0.0 - 1.0)
    """
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    target_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    relation_type = Column(String(100), nullable=False, index=True)
    weight = Column(Float, nullable=True)  # Optional relationship strength

    # Relationships
    source_item = relationship("Item", foreign_keys=[source_id], back_populates="edges_as_source")
    target_item = relationship("Item", foreign_keys=[target_id], back_populates="edges_as_target")

    def __repr__(self):
        return f"<Edge(id={self.id}, source_id={self.source_id}, target_id={self.target_id}, relation={self.relation_type})>"
