"""
Document models for managing document collections
Handles document metadata, reading progress, and tags
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..connection import Base
from .base import BaseModel


class Document(Base, BaseModel):
    """
    Document model for storing document information
    Supports various formats: PDF, TXT, MD, DOCX, EPUB, etc.
    """

    __tablename__ = "documents"

    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False, index=True)
    path = Column(String(1024), nullable=False, unique=True)
    format = Column(String(20), nullable=False)  # pdf, txt, md, docx, epub, etc.
    file_size = Column(Integer, nullable=True)  # Size in bytes
    page_count = Column(Integer, nullable=True)  # Total pages (for paginated documents)
    thumbnail_path = Column(String(1024), nullable=True)

    # Document metadata
    author = Column(String(255), nullable=True)
    publisher = Column(String(255), nullable=True)
    year = Column(Integer, nullable=True)
    language = Column(String(50), nullable=True)
    isbn = Column(String(20), nullable=True)
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)

    # Content indexing
    word_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=True)
    has_toc = Column(Integer, default=0, nullable=False)  # Has table of contents

    # Rating and statistics
    rating = Column(Float, nullable=True)  # User rating 0-5
    read_count = Column(Integer, default=0, nullable=False)
    is_favorite = Column(Integer, default=0, nullable=False)

    # File hash for duplicate detection
    file_hash = Column(String(64), nullable=True, index=True)

    # Relationships
    library = relationship("Library", back_populates="document_items")
    progress = relationship(
        "DocumentProgress",
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
    )
    tags = relationship(
        "DocumentTag",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    annotations = relationship(
        "DocumentAnnotation",
        back_populates="document",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Document(id={self.id}, title={self.title!r}, format={self.format!r})"


class DocumentProgress(Base, BaseModel):
    """
    Document reading progress tracking
    Stores current position and reading history
    """

    __tablename__ = "document_progress"

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    current_page = Column(Integer, default=0, nullable=False)
    current_position = Column(Integer, default=0, nullable=False)  # Character/byte position
    last_read_at = Column(String(50), nullable=True)  # ISO format datetime string
    reading_time = Column(Integer, default=0, nullable=False)  # Total reading time in seconds
    is_completed = Column(Integer, default=0, nullable=False)

    # Reading preferences for this document
    font_size = Column(Integer, nullable=True)
    font_family = Column(String(100), nullable=True)
    line_spacing = Column(Float, nullable=True)
    theme = Column(String(20), nullable=True)  # light, dark, sepia

    # Relationships
    document = relationship("Document", back_populates="progress")

    def __repr__(self) -> str:
        return f"DocumentProgress(document_id={self.document_id}, page={self.current_page})"


class DocumentTag(Base, BaseModel):
    """
    Tags for documents
    Many-to-many relationship between documents and tags
    """

    __tablename__ = "document_tags"

    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    tag_name = Column(String(100), nullable=False, index=True)

    # Relationships
    document = relationship("Document", back_populates="tags")

    def __repr__(self) -> str:
        return f"DocumentTag(document_id={self.document_id}, tag={self.tag_name!r})"


class DocumentAnnotation(Base, BaseModel):
    """
    Annotations and highlights for documents
    Allows users to add notes and highlights to specific locations
    """

    __tablename__ = "document_annotations"

    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number = Column(Integer, nullable=True)  # For paginated documents
    position_start = Column(Integer, nullable=True)  # Character/byte position
    position_end = Column(Integer, nullable=True)
    annotation_type = Column(String(20), nullable=False)  # highlight, note, bookmark
    content = Column(Text, nullable=True)  # Selected text or note content
    color = Column(String(7), nullable=True)  # Hex color for highlights
    notes = Column(Text, nullable=True)  # User notes

    # Relationships
    document = relationship("Document", back_populates="annotations")

    def __repr__(self) -> str:
        return f"DocumentAnnotation(document_id={self.document_id}, type={self.annotation_type!r})"


class SearchIndex(Base, BaseModel):
    """
    Full-text search index for documents
    Stores searchable content for fast retrieval
    """

    __tablename__ = "search_index"

    item_type = Column(String(20), nullable=False, index=True)  # manga, video, document
    item_id = Column(Integer, nullable=False, index=True)
    content = Column(Text, nullable=False)  # Searchable text content
    metadata = Column(Text, nullable=True)  # JSON metadata for search results

    def __repr__(self) -> str:
        return f"SearchIndex(type={self.item_type!r}, item_id={self.item_id})"
