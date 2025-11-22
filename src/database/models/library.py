"""
Library models for managing media collections
Defines the structure for organizing manga, videos, and documents
"""

from sqlalchemy import Column, Enum, Integer, String, Text
from sqlalchemy.orm import relationship

from ..connection import Base
from .base import BaseModel


class MediaType(str, Enum):
    """Enum for media types"""

    MANGA = "manga"
    VIDEO = "video"
    DOCUMENT = "document"


class Library(Base, BaseModel):
    """
    Library model for organizing media collections
    Each library represents a collection of media items of a specific type
    """

    __tablename__ = "libraries"

    name = Column(String(255), nullable=False, index=True)
    path = Column(String(1024), nullable=False, unique=True)
    media_type = Column(String(20), nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Integer, default=1, nullable=False)  # SQLite doesn't have boolean
    scan_subdirectories = Column(Integer, default=1, nullable=False)
    auto_scan = Column(Integer, default=1, nullable=False)
    last_scan_at = Column(String(50), nullable=True)  # ISO format datetime string

    # Relationships
    manga_items = relationship(
        "Manga",
        back_populates="library",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    video_items = relationship(
        "Video",
        back_populates="library",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    document_items = relationship(
        "Document",
        back_populates="library",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"Library(id={self.id}, name={self.name!r}, type={self.media_type!r})"


class Tag(Base, BaseModel):
    """
    Tag model for categorizing media items
    Tags can be applied to any media type
    """

    __tablename__ = "tags"

    name = Column(String(100), nullable=False, unique=True, index=True)
    color = Column(String(7), nullable=True)  # Hex color code, e.g., #FF5733
    description = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name={self.name!r})"


class Favorite(Base, BaseModel):
    """
    Favorite model for marking items as favorites
    Generic model that can reference any media type
    """

    __tablename__ = "favorites"

    item_type = Column(String(20), nullable=False, index=True)  # manga, video, document
    item_id = Column(Integer, nullable=False, index=True)
    notes = Column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"Favorite(id={self.id}, type={self.item_type!r}, item_id={self.item_id})"
