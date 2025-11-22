"""
Eromang - Multi-functional Media Management Software
Main entry point for the application
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from loguru import logger

from .database.connection import init_database, get_db_manager
from .managers.config_manager import get_config_manager
from .ui.main_window import MainWindow
from .constants import settings


def setup_logging():
    """Configure logging system"""
    config_manager = get_config_manager()

    # Create logs directory
    log_dir = Path(config_manager.get("paths.logs", settings.DEFAULT_LOG_DIR))
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure loguru
    log_level = config_manager.get("logging.level", "INFO")
    log_file = log_dir / "eromang.log"

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format=settings.LOG_FORMAT,
        level=log_level,
        colorize=True,
    )

    # Add file handler with rotation
    logger.add(
        log_file,
        format=settings.LOG_FORMAT,
        level=log_level,
        rotation=f"{config_manager.get('logging.max_size_mb', 10)} MB",
        retention=config_manager.get('logging.backup_count', 5),
        compression="zip",
        encoding="utf-8",
    )

    logger.info("Logging system initialized")


def setup_directories():
    """Create necessary application directories"""
    config_manager = get_config_manager()

    directories = [
        config_manager.get("paths.cache", settings.DEFAULT_CACHE_DIR),
        config_manager.get("paths.thumbnails", settings.DEFAULT_THUMBNAIL_DIR),
        config_manager.get("paths.temp", settings.DEFAULT_TEMP_DIR),
        config_manager.get("paths.logs", settings.DEFAULT_LOG_DIR),
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    logger.info("Application directories created")


def initialize_database():
    """Initialize database and create tables"""
    config_manager = get_config_manager()
    db_path = config_manager.get("paths.database", settings.DEFAULT_DB_PATH)

    try:
        init_database(db_path)
        logger.info(f"Database initialized at: {db_path}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def main():
    """Main application entry point"""
    try:
        # Initialize configuration
        config_manager = get_config_manager()
        logger.info(f"Starting {config_manager.get('app.name', 'Eromang')} v{config_manager.get('app.version', '0.1.0')}")

        # Setup logging
        setup_logging()

        # Create necessary directories
        setup_directories()

        # Initialize database
        initialize_database()

        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName(config_manager.get("app.name", "Eromang"))
        app.setApplicationVersion(config_manager.get("app.version", "0.1.0"))
        app.setOrganizationName(settings.APP_AUTHOR)

        # Create and show main window
        main_window = MainWindow()
        main_window.show()

        logger.info("Application started successfully")

        # Run application event loop
        exit_code = app.exec()

        # Cleanup
        logger.info("Application shutting down")
        db_manager = get_db_manager()
        db_manager.close()

        return exit_code

    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
