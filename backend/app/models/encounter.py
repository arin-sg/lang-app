"""
Encounter model - learning telemetry log.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Encounter(Base):
    """
    Learning telemetry log - the most critical table for personalization.

    Attributes:
        id: Primary key
        item_id: Foreign key to items.id - the item being practiced
        mode: Context of interaction (review, drill, chat)
        correct: Outcome of the interaction (True/False)
        prompt: Question or prompt presented to the user
        actual_answer: User's submitted answer
        expected_answer: The correct answer
        context_sentence: Full sentence from which the item/drill was derived
        error_type: Classified error type from taxonomy
        confusion_target_id: Foreign key to items.id - if confusable error, points to confused item
        response_time_ms: Time in milliseconds taken to respond
        timestamp: When the event occurred
    """
    __tablename__ = "encounters"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False, index=True)
    mode = Column(String(50), nullable=False, index=True)  # review, drill, chat
    correct = Column(Boolean, nullable=False, index=True)
    prompt = Column(Text, nullable=True)
    actual_answer = Column(Text, nullable=True)
    expected_answer = Column(Text, nullable=True)
    context_sentence = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True, index=True)
    confusion_target_id = Column(Integer, ForeignKey("items.id"), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    item = relationship("Item", foreign_keys=[item_id], back_populates="encounters")
    confusion_target = relationship("Item", foreign_keys=[confusion_target_id])

    def __repr__(self):
        return f"<Encounter(id={self.id}, item_id={self.item_id}, mode={self.mode}, correct={self.correct})>"
