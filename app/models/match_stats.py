from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class MatchStats(TimestampMixin, Base):
    __tablename__ = "match_stats"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), unique=True)
    possession_home: Mapped[int | None] = mapped_column(Integer)
    possession_away: Mapped[int | None] = mapped_column(Integer)
    corners_home: Mapped[int | None] = mapped_column(Integer)
    corners_away: Mapped[int | None] = mapped_column(Integer)
    cards_home: Mapped[int | None] = mapped_column(Integer)
    cards_away: Mapped[int | None] = mapped_column(Integer)

    match: Mapped["Match"] = relationship(back_populates="stats")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<MatchStats match_id={self.match_id}>"
