"""
ErrorTag model - lookup table for error taxonomy.
"""
from sqlalchemy import Column, Integer, String
from app.models.base import Base


class ErrorTag(Base):
    """
    Simple lookup table for the error taxonomy.

    Attributes:
        id: Primary key
        name: Unique name of the error tag (e.g., GENDER, CASE, WORD_ORDER)
        description: Optional description of the error type
    """
    __tablename__ = "error_tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<ErrorTag(id={self.id}, name={self.name})>"
