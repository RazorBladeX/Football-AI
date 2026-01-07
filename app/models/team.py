from typing import List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class Team(TimestampMixin, Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    venue: Mapped[str | None] = mapped_column(String(120))
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)

    league: Mapped["League"] = relationship(back_populates="teams")
    home_matches: Mapped[List["Match"]] = relationship(
        back_populates="home_team", foreign_keys="Match.home_team_id"
    )
    away_matches: Mapped[List["Match"]] = relationship(
        back_populates="away_team", foreign_keys="Match.away_team_id"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Team {self.name}>"
