"""
Configuration manager for handling application settings
Supports loading, saving, and updating configuration from YAML files
"""

import os
from pathlib import Path
from typing import Any

import yaml
from loguru import logger

from ..constants import settings


class ConfigManager:
    """Manages application configuration"""

    def __init__(self, config_path: str | Path | None = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to configuration file. If None, uses default location.
        """
        if config_path is None:
            config_path = settings.DEFAULT_CONFIG_FILE

        self.config_path = Path(config_path)
        self.config: dict[str, Any] = {}
        self._load_defaults()

        # Create config directory if it doesn't exist
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new one
        if self.config_path.exists():
            self.load()
        else:
            self.save()

    def _load_defaults(self):
        """Load default configuration values"""
        self.config = {
            "app": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "theme": settings.DEFAULT_THEME,
                "language": settings.DEFAULT_LANGUAGE,
            },
            "window": {
                "width": settings.DEFAULT_WINDOW_WIDTH,
                "height": settings.DEFAULT_WINDOW_HEIGHT,
                "min_width": settings.WINDOW_MIN_WIDTH,
                "min_height": settings.WINDOW_MIN_HEIGHT,
                "maximized": False,
                "position_x": None,
                "position_y": None,
            },
            "paths": {
                "database": str(settings.DEFAULT_DB_PATH),
                "cache": str(settings.DEFAULT_CACHE_DIR),
                "thumbnails": str(settings.DEFAULT_THUMBNAIL_DIR),
                "temp": str(settings.DEFAULT_TEMP_DIR),
                "logs": str(settings.DEFAULT_LOG_DIR),
            },
            "modules": {
                "manga": {
                    "enabled": True,
                    "formats": settings.MANGA_FORMATS,
                    "reading_mode": settings.DEFAULT_MANGA_READING_MODE,
                    "zoom_mode": settings.DEFAULT_MANGA_ZOOM_MODE,
                    "background_color": settings.DEFAULT_MANGA_BACKGROUND,
                    "preload_count": settings.IMAGE_PRELOAD_COUNT,
                },
                "video": {
                    "enabled": True,
                    "formats": settings.VIDEO_FORMATS,
                    "volume": settings.DEFAULT_VIDEO_VOLUME,
                    "playback_speed": settings.DEFAULT_VIDEO_PLAYBACK_SPEED,
                    "subtitle_enabled": settings.DEFAULT_VIDEO_SUBTITLE_ENABLED,
                    "autoplay": settings.DEFAULT_VIDEO_AUTOPLAY,
                },
                "document": {
                    "enabled": True,
                    "formats": settings.DOCUMENT_FORMATS,
                    "font_size": settings.DEFAULT_DOCUMENT_FONT_SIZE,
                    "font_family": settings.DEFAULT_DOCUMENT_FONT_FAMILY,
                    "line_spacing": settings.DEFAULT_DOCUMENT_LINE_SPACING,
                    "theme": settings.DEFAULT_DOCUMENT_THEME,
                },
            },
            "network": {
                "api_enabled": settings.API_ENABLED,
                "api_host": settings.API_HOST,
                "api_port": settings.API_PORT,
                "websocket_enabled": settings.WEBSOCKET_ENABLED,
                "websocket_port": settings.WEBSOCKET_PORT,
                "timeout": settings.NETWORK_TIMEOUT,
            },
            "scanning": {
                "scan_subdirectories": settings.SCAN_SUBDIRECTORIES,
                "auto_scan_on_startup": settings.AUTO_SCAN_ON_STARTUP,
                "scan_interval_minutes": settings.SCAN_INTERVAL_MINUTES,
                "max_file_size_mb": settings.MAX_FILE_SIZE_MB,
            },
            "cache": {
                "size_mb": settings.CACHE_SIZE_MB,
                "thumbnail_size": list(settings.THUMBNAIL_SIZE),
                "thumbnail_quality": settings.THUMBNAIL_QUALITY,
            },
            "performance": {
                "thread_pool_size": settings.THREAD_POOL_SIZE,
                "max_concurrent_scans": settings.MAX_CONCURRENT_SCANS,
                "hardware_acceleration": settings.ENABLE_HARDWARE_ACCELERATION,
            },
            "logging": {
                "level": settings.LOG_LEVEL,
                "max_size_mb": settings.LOG_MAX_SIZE_MB,
                "backup_count": settings.LOG_BACKUP_COUNT,
            },
            "search": {
                "max_results": settings.SEARCH_MAX_RESULTS,
                "min_query_length": settings.SEARCH_MIN_QUERY_LENGTH,
                "fuzzy_search": settings.ENABLE_FUZZY_SEARCH,
            },
            "backup": {
                "auto_backup": settings.AUTO_BACKUP_ENABLED,
                "interval_days": settings.BACKUP_INTERVAL_DAYS,
                "max_count": settings.MAX_BACKUP_COUNT,
            },
        }

    def load(self) -> bool:
        """
        Load configuration from file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f)

            if loaded_config:
                # Merge loaded config with defaults (preserves new default keys)
                self._merge_config(self.config, loaded_config)
                logger.info(f"Configuration loaded from {self.config_path}")
                return True
            else:
                logger.warning(f"Empty configuration file: {self.config_path}")
                return False

        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}")
            return False
        except yaml.YAMLError as e:
            logger.error(f"Error parsing configuration file: {e}")
            return False
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False

    def save(self) -> bool:
        """
        Save configuration to file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            logger.info(f"Configuration saved to {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

    def _merge_config(self, base: dict, update: dict):
        """
        Recursively merge update dict into base dict

        Args:
            base: Base dictionary to merge into
            update: Dictionary with updates
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key path

        Args:
            key_path: Dot-separated path to config value (e.g., "app.theme")
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split(".")
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def set(self, key_path: str, value: Any, save: bool = True) -> bool:
        """
        Set configuration value by dot-separated key path

        Args:
            key_path: Dot-separated path to config value (e.g., "app.theme")
            value: Value to set
            save: Whether to save config to file immediately

        Returns:
            True if successful, False otherwise
        """
        keys = key_path.split(".")
        config = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

        if save:
            return self.save()

        return True

    def reset(self, save: bool = True) -> bool:
        """
        Reset configuration to defaults

        Args:
            save: Whether to save config to file immediately

        Returns:
            True if successful, False otherwise
        """
        self._load_defaults()

        if save:
            return self.save()

        return True

    def get_all(self) -> dict:
        """
        Get entire configuration dictionary

        Returns:
            Configuration dictionary
        """
        return self.config.copy()

    def update(self, updates: dict, save: bool = True) -> bool:
        """
        Update multiple configuration values

        Args:
            updates: Dictionary with configuration updates
            save: Whether to save config to file immediately

        Returns:
            True if successful, False otherwise
        """
        self._merge_config(self.config, updates)

        if save:
            return self.save()

        return True

    def export(self, export_path: str | Path) -> bool:
        """
        Export configuration to a different file

        Args:
            export_path: Path to export file

        Returns:
            True if successful, False otherwise
        """
        try:
            export_path = Path(export_path)
            export_path.parent.mkdir(parents=True, exist_ok=True)

            with open(export_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.config,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
            logger.info(f"Configuration exported to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting configuration: {e}")
            return False

    def import_config(self, import_path: str | Path) -> bool:
        """
        Import configuration from a file

        Args:
            import_path: Path to import file

        Returns:
            True if successful, False otherwise
        """
        try:
            import_path = Path(import_path)

            with open(import_path, "r", encoding="utf-8") as f:
                imported_config = yaml.safe_load(f)

            if imported_config:
                self._merge_config(self.config, imported_config)
                self.save()
                logger.info(f"Configuration imported from {import_path}")
                return True
            else:
                logger.warning(f"Empty configuration file: {import_path}")
                return False

        except Exception as e:
            logger.error(f"Error importing configuration: {e}")
            return False


# Global configuration manager instance
_config_manager: ConfigManager | None = None


def get_config_manager(config_path: str | Path | None = None) -> ConfigManager:
    """
    Get or create global configuration manager instance

    Args:
        config_path: Path to configuration file (only used on first call)

    Returns:
        ConfigManager instance
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager


def get_config(key_path: str, default: Any = None) -> Any:
    """
    Get configuration value using global manager

    Args:
        key_path: Dot-separated path to config value
        default: Default value if key not found

    Returns:
        Configuration value or default
    """
    return get_config_manager().get(key_path, default)


def set_config(key_path: str, value: Any, save: bool = True) -> bool:
    """
    Set configuration value using global manager

    Args:
        key_path: Dot-separated path to config value
        value: Value to set
        save: Whether to save immediately

    Returns:
        True if successful, False otherwise
    """
    return get_config_manager().set(key_path, value, save)
