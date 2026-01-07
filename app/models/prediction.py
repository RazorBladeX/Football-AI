from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), nullable=False)
    model_used: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float | None] = mapped_column()
    final_score_home: Mapped[int | None] = mapped_column()
    final_score_away: Mapped[int | None] = mapped_column()
    first_half_goals: Mapped[int | None] = mapped_column()
    second_half_goals: Mapped[int | None] = mapped_column()
    total_corners: Mapped[int | None] = mapped_column()
    total_cards: Mapped[int | None] = mapped_column()
    raw_response: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(DateTime(), default=datetime.utcnow)

    match: Mapped["Match"] = relationship(back_populates="predictions")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Prediction match_id={self.match_id} model={self.model_used}>"
