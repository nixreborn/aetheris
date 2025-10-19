"""
Database initialization and session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import logging

from .models import Base
from config.settings import get_settings

logger = logging.getLogger(__name__)

# Global engine and session factory
_engine = None
_SessionFactory = None


def init_database(connection_string: str = None) -> None:
    """
    Initialize the database engine and create all tables.

    Args:
        connection_string: Database connection string. If None, uses settings.
    """
    global _engine, _SessionFactory

    settings = get_settings()
    if connection_string is None:
        connection_string = settings.database_connection_string

    logger.info(f"Initializing database: {connection_string}")

    _engine = create_engine(
        connection_string,
        echo=settings.debug_mode,
        pool_pre_ping=True
    )

    _SessionFactory = sessionmaker(bind=_engine)

    # Create all tables
    Base.metadata.create_all(_engine)
    logger.info("Database initialized successfully")


def get_engine():
    """Get the global database engine."""
    if _engine is None:
        init_database()
    return _engine


def get_session_factory():
    """Get the global session factory."""
    if _SessionFactory is None:
        init_database()
    return _SessionFactory


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Usage:
        with get_db_session() as session:
            # Use session
            pass
    """
    if _SessionFactory is None:
        init_database()

    session = _SessionFactory()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()


def reset_database() -> None:
    """Drop all tables and recreate them. WARNING: Destroys all data!"""
    if _engine is None:
        init_database()

    logger.warning("Resetting database - all data will be lost!")
    Base.metadata.drop_all(_engine)
    Base.metadata.create_all(_engine)
    logger.info("Database reset complete")
