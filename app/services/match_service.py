from datetime import date, datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.db import get_session
from app.models.league import League
from app.models.match import Match, MatchStatus
from app.models.match_stats import MatchStats
from app.models.team import Team
from app.utils.datetime_utils import to_local


class MatchService:
    def ensure_league(self, name: str, tier: int = 1, session=None) -> League:
        own_session = session is None
        ctx = get_session() if own_session else None
        sess = ctx.__enter__() if ctx else session
        try:
            league = sess.execute(select(League).where(League.name == name)).scalar_one_or_none()
            if not league:
                league = League(name=name, tier=tier)
                sess.add(league)
                sess.flush()
            sess.refresh(league)
            sess.expunge(league)
            return league
        finally:
            if ctx:
                ctx.__exit__(None, None, None)

    def ensure_team(self, name: str, league: League, session=None) -> Team:
        own_session = session is None
        ctx = get_session() if own_session else None
        sess = ctx.__enter__() if ctx else session
        try:
            team = sess.execute(select(Team).where(Team.name == name)).scalar_one_or_none()
            if not team:
                team = Team(name=name, league_id=league.id)
                sess.add(team)
                sess.flush()
            sess.refresh(team)
            sess.expunge(team)
            return team
        finally:
            if ctx:
                ctx.__exit__(None, None, None)

    def upsert_match(
        self,
        league: League,
        home_team: Team,
        away_team: Team,
        kickoff: datetime | None,
        status: str,
        home_score: int | None,
        away_score: int | None,
        venue: str | None = None,
    ) -> Match:
        with get_session() as session:
            match = (
                session.execute(
                    select(Match).where(
                        Match.home_team_id == home_team.id,
                        Match.away_team_id == away_team.id,
                        Match.kickoff_utc == kickoff,
                    )
                ).scalar_one_or_none()
            )
            if not match:
                match = Match(
                    league_id=league.id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    kickoff_utc=kickoff,
                    kickoff_local=to_local(kickoff) if kickoff else None,
                    venue=venue,
                    status=status,
                    home_score=home_score,
                    away_score=away_score,
                )
                session.add(match)
            else:
                match.status = status
                match.home_score = home_score
                match.away_score = away_score
                match.venue = venue
                match.kickoff_utc = kickoff
                match.kickoff_local = to_local(kickoff) if kickoff else None
            session.flush()
            session.refresh(match)
            session.expunge(match)
            return match

    def list_matches_for_date(self, target_date: date) -> List[Match]:
        start = datetime.combine(target_date, datetime.min.time())
        end = datetime.combine(target_date, datetime.max.time())
        with get_session() as session:
            base_query = (
                select(Match)
                .options(selectinload(Match.home_team), selectinload(Match.away_team))
                .where(Match.kickoff_utc >= start, Match.kickoff_utc <= end)
            )
            matches = session.execute(base_query).scalars().all()
            matches += (
                session.execute(
                    select(Match)
                    .options(selectinload(Match.home_team), selectinload(Match.away_team))
                    .where(Match.kickoff_utc.is_(None))
                )
                .scalars()
                .all()
            )
            for match in matches:
                session.expunge(match)
            return matches

    def get_match(self, match_id: int) -> Match | None:
        """Return a detached Match with teams eagerly loaded, or None if missing."""
        with get_session() as session:
            match = session.get(
                Match,
                match_id,
                options=[selectinload(Match.home_team), selectinload(Match.away_team)],
            )
            if match:
                session.expunge(match)
            return match

    def live_matches(self) -> List[Match]:
        with get_session() as session:
            return session.execute(select(Match).where(Match.status == MatchStatus.LIVE)).scalars().all()

    def save_stats(
        self,
        match: Match,
        corners_home: int | None = None,
        corners_away: int | None = None,
        cards_home: int | None = None,
        cards_away: int | None = None,
        possession_home: int | None = None,
        possession_away: int | None = None,
    ) -> MatchStats:
        with get_session() as session:
            stats = session.execute(select(MatchStats).where(MatchStats.match_id == match.id)).scalar_one_or_none()
            if not stats:
                stats = MatchStats(match_id=match.id)
                session.add(stats)
            stats.corners_home = corners_home
            stats.corners_away = corners_away
            stats.cards_home = cards_home
            stats.cards_away = cards_away
            stats.possession_home = possession_home
            stats.possession_away = possession_away
            session.flush()
            return stats
