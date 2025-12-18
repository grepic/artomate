"""Database connection and session management."""

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from artomate.core.config import get_config
from artomate.db.models import Base


class Database:
    """Database connection manager."""

    def __init__(self, database_url: str | None = None):
        """Initialize database connection.

        Args:
            database_url: Database URL. If None, uses config.
        """
        if database_url is None:
            config = get_config()
            database_url = config.database_url

        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=False,
            connect_args={"check_same_thread": False} if database_url.startswith("sqlite") else {},
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self) -> None:
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope for database operations.

        Usage:
            with db.session_scope() as session:
                job = Job(...)
                session.add(job)
                # Automatically commits on success, rolls back on exception
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database instance
_db: Database | None = None


def get_db() -> Database:
    """Get or create global database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db


def init_db() -> None:
    """Initialize database (create tables)."""
    db = get_db()
    db.create_tables()
    print(f"✓ Database initialized: {db.database_url}")


def reset_db() -> None:
    """Reset database (drop and recreate tables)."""
    db = get_db()
    db.drop_tables()
    db.create_tables()
    print(f"✓ Database reset: {db.database_url}")
