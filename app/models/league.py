from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin


class League(TimestampMixin, Base):
    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    tier: Mapped[int] = mapped_column(nullable=False)
    country: Mapped[str] = mapped_column(String(50), default="England")

    teams: Mapped[List["Team"]] = relationship(back_populates="league", cascade="all, delete-orphan")
    matches: Mapped[List["Match"]] = relationship(back_populates="league", cascade="all, delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover - representation helper
        return f"<League {self.name} (tier {self.tier})>"
