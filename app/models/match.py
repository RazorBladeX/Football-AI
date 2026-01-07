from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class MatchStatus:
    UPCOMING = "upcoming"
    LIVE = "live"
    FINISHED = "finished"


class Match(TimestampMixin, Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    kickoff_utc: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    kickoff_local: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    venue: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), default=MatchStatus.UPCOMING)
    home_score: Mapped[Optional[int]] = mapped_column(default=None)
    away_score: Mapped[Optional[int]] = mapped_column(default=None)
    home_ht_score: Mapped[Optional[int]] = mapped_column(default=None)
    away_ht_score: Mapped[Optional[int]] = mapped_column(default=None)

    league: Mapped["League"] = relationship(back_populates="matches")
    home_team: Mapped["Team"] = relationship(
        back_populates="home_matches", foreign_keys=[home_team_id]
    )
    away_team: Mapped["Team"] = relationship(
        back_populates="away_matches", foreign_keys=[away_team_id]
    )
    stats: Mapped["MatchStats"] = relationship(
        back_populates="match", uselist=False, cascade="all, delete-orphan"
    )
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="match", cascade="all, delete-orphan"
    )

    def description(self) -> str:
        return f"{self.home_team.name} vs {self.away_team.name}"

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Match {self.description()} status={self.status}>"
