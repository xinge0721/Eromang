"""
Database models package
Exports all ORM models for easy import
"""

from .base import BaseModel, TimestampMixin
from .document import Document, DocumentAnnotation, DocumentProgress, DocumentTag, SearchIndex
from .library import Favorite, Library, Tag
from .manga import Manga, MangaBookmark, MangaProgress
from .video import Playlist, PlaylistItem, Video, VideoProgress

__all__ = [
    # Base
    "BaseModel",
    "TimestampMixin",
    # Library
    "Library",
    "Tag",
    "Favorite",
    # Manga
    "Manga",
    "MangaProgress",
    "MangaBookmark",
    # Video
    "Video",
    "VideoProgress",
    "Playlist",
    "PlaylistItem",
    # Document
    "Document",
    "DocumentProgress",
    "DocumentTag",
    "DocumentAnnotation",
    "SearchIndex",
]
