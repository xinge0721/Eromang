"""
Manga models for managing comic/manga collections
Handles manga metadata, reading progress, and related information
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..connection import Base
from .base import BaseModel


class Manga(Base, BaseModel):
    """
    Manga model for storing manga/comic information
    Supports various formats: CBZ, CBR, ZIP, RAR, PDF, image folders
    """

    __tablename__ = "manga"

    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False, index=True)
    path = Column(String(1024), nullable=False, unique=True)
    format = Column(String(20), nullable=False)  # cbz, cbr, zip, rar, pdf, folder
    file_size = Column(Integer, nullable=True)  # Size in bytes
    total_pages = Column(Integer, nullable=False, default=0)
    cover_path = Column(String(1024), nullable=True)  # Path to cover image or thumbnail

    # Metadata
    author = Column(String(255), nullable=True)
    artist = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    series = Column(String(500), nullable=True, index=True)
    volume = Column(String(50), nullable=True)
    chapter = Column(String(50), nullable=True)
    year = Column(Integer, nullable=True)
    language = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags

    # Rating and statistics
    rating = Column(Float, nullable=True)  # User rating 0-5
    read_count = Column(Integer, default=0, nullable=False)
    is_favorite = Column(Integer, default=0, nullable=False)

    # File hash for duplicate detection
    file_hash = Column(String(64), nullable=True, index=True)

    # Relationships
    library = relationship("Library", back_populates="manga_items")
    progress = relationship(
        "MangaProgress",
        back_populates="manga",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Manga(id={self.id}, title={self.title!r}, pages={self.total_pages})"


class MangaProgress(Base, BaseModel):
    """
    Manga reading progress tracking
    Stores current page and reading history
    """

    __tablename__ = "manga_progress"

    manga_id = Column(
        Integer,
        ForeignKey("manga.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    current_page = Column(Integer, default=0, nullable=False)
    last_read_at = Column(String(50), nullable=True)  # ISO format datetime string
    reading_time = Column(Integer, default=0, nullable=False)  # Total reading time in seconds
    is_completed = Column(Integer, default=0, nullable=False)

    # Reading preferences for this manga
    reading_mode = Column(String(20), nullable=True)  # single, double, continuous
    zoom_level = Column(Float, nullable=True)
    scroll_position = Column(Integer, nullable=True)

    # Relationships
    manga = relationship("Manga", back_populates="progress")

    def __repr__(self) -> str:
        return f"MangaProgress(manga_id={self.manga_id}, page={self.current_page})"


class MangaBookmark(Base, BaseModel):
    """
    Bookmarks for manga pages
    Allows users to mark specific pages for quick access
    """

    __tablename__ = "manga_bookmarks"

    manga_id = Column(Integer, ForeignKey("manga.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"MangaBookmark(manga_id={self.manga_id}, page={self.page_number})"
