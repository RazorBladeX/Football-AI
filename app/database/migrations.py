import logging

from app.database.db import engine
from app.models.base import Base

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    """Simple auto migration that ensures tables exist."""
    logger.info("Applying database migrations (auto-create tables)")
    Base.metadata.create_all(bind=engine)
