"""
Migration script to create app_settings table.
Run this to add the app_settings table to an existing database.
"""
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from database_models import AppSettings
from database import Database
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Create app_settings table and insert default timezone."""
    logger.info("=" * 80)
    logger.info("App Settings Table Migration")
    logger.info("=" * 80)

    # Initialize database
    db = Database()

    # Create app_settings table
    logger.info("Creating app_settings table...")
    with db.engine.begin() as conn:
        AppSettings.__table__.create(conn, checkfirst=True)

    logger.info("✅ app_settings table created successfully")

    # Insert default timezone setting
    with db.session() as session:
        setting = session.query(AppSettings).filter_by(setting_key='timezone').first()
        if not setting:
            setting = AppSettings(
                setting_key='timezone',
                setting_value='America/Puerto_Rico',  # Default to AST
                updated_at=datetime.now().isoformat()
            )
            session.add(setting)
            session.commit()
            logger.info("✅ Default timezone (America/Puerto_Rico - AST) inserted")
        else:
            logger.info(f"Timezone setting already exists: {setting.setting_value}")

    logger.info("=" * 80)
    logger.info("Migration complete!")
    logger.info("=" * 80)


if __name__ == "__main__":
    migrate()
