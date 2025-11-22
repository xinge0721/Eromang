"""
Default settings and constants for the application
Defines default configuration values
"""

from pathlib import Path

# Application information
APP_NAME = "Eromang"
APP_VERSION = "0.1.0"
APP_AUTHOR = "Eromang Team"

# Default paths
DEFAULT_APP_DIR = Path.home() / ".eromang"
DEFAULT_DB_PATH = DEFAULT_APP_DIR / "eromang.db"
DEFAULT_CACHE_DIR = DEFAULT_APP_DIR / "cache"
DEFAULT_THUMBNAIL_DIR = DEFAULT_CACHE_DIR / "thumbnails"
DEFAULT_TEMP_DIR = DEFAULT_CACHE_DIR / "temp"
DEFAULT_LOG_DIR = DEFAULT_APP_DIR / "logs"
DEFAULT_CONFIG_FILE = DEFAULT_APP_DIR / "config.yaml"

# Database settings
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30

# Cache settings
CACHE_SIZE_MB = 512
THUMBNAIL_SIZE = (200, 300)  # Width x Height
THUMBNAIL_QUALITY = 85
IMAGE_PRELOAD_COUNT = 3  # Number of pages to preload ahead

# UI settings
DEFAULT_THEME = "dark"
DEFAULT_LANGUAGE = "zh_CN"
WINDOW_MIN_WIDTH = 1024
WINDOW_MIN_HEIGHT = 768
DEFAULT_WINDOW_WIDTH = 1280
DEFAULT_WINDOW_HEIGHT = 900

# Manga reader settings
DEFAULT_MANGA_READING_MODE = "single"  # single, double, continuous
DEFAULT_MANGA_ZOOM_MODE = "fit_width"  # fit_width, fit_height, original, custom
DEFAULT_MANGA_BACKGROUND = "#2b2b2b"

# Video player settings
DEFAULT_VIDEO_VOLUME = 80
DEFAULT_VIDEO_PLAYBACK_SPEED = 1.0
DEFAULT_VIDEO_SUBTITLE_ENABLED = True
DEFAULT_VIDEO_AUTOPLAY = False

# Document viewer settings
DEFAULT_DOCUMENT_FONT_SIZE = 14
DEFAULT_DOCUMENT_FONT_FAMILY = "Arial"
DEFAULT_DOCUMENT_LINE_SPACING = 1.5
DEFAULT_DOCUMENT_THEME = "light"  # light, dark, sepia

# Network settings
API_ENABLED = False
API_HOST = "127.0.0.1"
API_PORT = 8080
WEBSOCKET_ENABLED = False
WEBSOCKET_PORT = 8081
NETWORK_TIMEOUT = 30

# File scanning settings
SCAN_SUBDIRECTORIES = True
AUTO_SCAN_ON_STARTUP = False
SCAN_INTERVAL_MINUTES = 60
MAX_FILE_SIZE_MB = 5000  # Maximum file size to process

# Supported formats
MANGA_FORMATS = [".cbz", ".cbr", ".zip", ".rar", ".pdf"]
VIDEO_FORMATS = [".mp4", ".mkv", ".avi", ".flv", ".mov", ".wmv", ".webm", ".m4v"]
DOCUMENT_FORMATS = [".txt", ".pdf", ".md", ".epub"]  # More formats can be added later
IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]

# Performance settings
THREAD_POOL_SIZE = 4
MAX_CONCURRENT_SCANS = 2
ENABLE_HARDWARE_ACCELERATION = True

# Logging settings
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_MAX_SIZE_MB = 10
LOG_BACKUP_COUNT = 5
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"

# Search settings
SEARCH_MAX_RESULTS = 100
SEARCH_MIN_QUERY_LENGTH = 2
ENABLE_FUZZY_SEARCH = True

# Backup settings
AUTO_BACKUP_ENABLED = False
BACKUP_INTERVAL_DAYS = 7
MAX_BACKUP_COUNT = 5
