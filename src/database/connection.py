"""
Database connection management module
Handles SQLite database connections and session management
"""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

# Base class for all ORM models
Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions"""

    def __init__(self, db_path: str | Path | None = None):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Default database location in user's app data directory
            app_data_dir = Path.home() / ".eromang"
            app_data_dir.mkdir(parents=True, exist_ok=True)
            db_path = app_data_dir / "eromang.db"

        self.db_path = Path(db_path)
        self.db_url = f"sqlite:///{self.db_path}"

        # Create engine with optimizations for SQLite
        self.engine = create_engine(
            self.db_url,
            echo=False,  # Set to True for SQL query logging
            connect_args={
                "check_same_thread": False,  # Allow multi-threading
                "timeout": 30,  # Connection timeout in seconds
            },
            poolclass=StaticPool,  # Use static pool for SQLite
        )

        # Enable foreign key constraints for SQLite
        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for better concurrency
            cursor.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
            cursor.execute("PRAGMA temp_store=MEMORY")  # Store temp tables in memory
            cursor.close()

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )

    def create_all_tables(self):
        """Create all tables defined in models"""
        Base.metadata.create_all(bind=self.engine)

    def drop_all_tables(self):
        """Drop all tables (use with caution!)"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """
        Get a new database session

        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations

        Usage:
            with db_manager.session_scope() as session:
                session.add(obj)
                # Changes are automatically committed

        Yields:
            SQLAlchemy Session object
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

    def close(self):
        """Close database connection"""
        self.engine.dispose()

    def backup(self, backup_path: str | Path):
        """
        Create a backup of the database

        Args:
            backup_path: Path where backup will be saved
        """
        import shutil

        backup_path = Path(backup_path)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Close all connections before backup
        self.engine.dispose()

        # Copy database file
        shutil.copy2(self.db_path, backup_path)

        # Recreate engine
        self.engine = create_engine(
            self.db_url,
            echo=False,
            connect_args={"check_same_thread": False, "timeout": 30},
            poolclass=StaticPool,
        )

    def get_database_size(self) -> int:
        """
        Get database file size in bytes

        Returns:
            Size in bytes
        """
        if self.db_path.exists():
            return self.db_path.stat().st_size
        return 0

    def vacuum(self):
        """
        Optimize database by reclaiming unused space
        Should be called periodically to maintain performance
        """
        with self.engine.connect() as conn:
            conn.execute("VACUUM")


# Global database manager instance
_db_manager: DatabaseManager | None = None


def get_db_manager(db_path: str | Path | None = None) -> DatabaseManager:
    """
    Get or create global database manager instance

    Args:
        db_path: Path to database file (only used on first call)

    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager


def init_database(db_path: str | Path | None = None):
    """
    Initialize database and create all tables

    Args:
        db_path: Path to database file
    """
    db_manager = get_db_manager(db_path)
    db_manager.create_all_tables()


def get_session() -> Session:
    """
    Get a new database session from global manager

    Returns:
        SQLAlchemy Session object
    """
    return get_db_manager().get_session()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional scope using global database manager

    Yields:
        SQLAlchemy Session object
    """
    with get_db_manager().session_scope() as session:
        yield session
