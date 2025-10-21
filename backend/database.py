"""
Database connection and session management for pharmacy exam prep application.
"""
import os
from contextlib import contextmanager
from typing import Generator

from database_models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


class Database:
    """Database connection manager."""

    def __init__(self, db_path: str = 'pharma_exam.db'):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=False,  # Set to True for SQL query debugging
            connect_args={'check_same_thread': False}  # Allow multi-threaded access
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self) -> None:
        """Create all tables in the database using Alembic migrations."""
        from alembic.config import Config
        from alembic import command
        import os

        # Get the directory containing this file
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        alembic_cfg = Config(os.path.join(backend_dir, "alembic.ini"))

        # Run migrations to latest version
        command.upgrade(alembic_cfg, "head")
        print(f"✅ Database migrated to latest schema: {self.db_path}")

    def drop_tables(self) -> None:
        """Drop all tables in the database. WARNING: Destroys all data!"""
        Base.metadata.drop_all(bind=self.engine)
        print(f"⚠️  All tables dropped from: {self.db_path}")

    def reset_database(self) -> None:
        """Drop and recreate all tables. WARNING: Destroys all data!"""
        self.drop_tables()
        self.create_tables()
        print(f"🔄 Database reset complete: {self.db_path}")

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.

        Usage:
            with db.session() as session:
                document = Document(file_id='123', ...)
                session.add(document)
                session.commit()
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

    def get_session(self) -> Session:
        """
        Get a new database session. Caller is responsible for closing.

        Returns:
            SQLAlchemy Session object
        """
        return self.SessionLocal()

    def close(self) -> None:
        """Close database connection."""
        self.engine.dispose()
        print(f"🔒 Database connection closed: {self.db_path}")


# Global database instance
_db_instance = None


def get_database(db_path: str = 'pharma_exam.db') -> Database:
    """
    Get or create global database instance.

    Args:
        db_path: Path to SQLite database file

    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
    return _db_instance


def init_database(db_path: str = 'pharma_exam.db', reset: bool = False) -> Database:
    """
    Initialize database with tables.

    Args:
        db_path: Path to SQLite database file
        reset: If True, drop and recreate all tables (WARNING: destroys data!)

    Returns:
        Database instance
    """
    db = get_database(db_path)

    if reset:
        db.reset_database()
    elif not os.path.exists(db_path):
        db.create_tables()
    else:
        print(f"ℹ️  Using existing database: {db_path}")

    return db
