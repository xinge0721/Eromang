"""
Video models for managing video collections
Handles video metadata, playback progress, and playlists
"""

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..connection import Base
from .base import BaseModel


class Video(Base, BaseModel):
    """
    Video model for storing video information
    Supports various formats: MP4, MKV, AVI, FLV, MOV, etc.
    """

    __tablename__ = "videos"

    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(500), nullable=False, index=True)
    path = Column(String(1024), nullable=False, unique=True)
    format = Column(String(20), nullable=False)  # mp4, mkv, avi, flv, etc.
    file_size = Column(Integer, nullable=True)  # Size in bytes
    duration = Column(Integer, nullable=True)  # Duration in seconds
    thumbnail_path = Column(String(1024), nullable=True)

    # Video metadata
    resolution = Column(String(20), nullable=True)  # e.g., 1920x1080
    fps = Column(Float, nullable=True)  # Frames per second
    bitrate = Column(Integer, nullable=True)  # Bitrate in kbps
    codec = Column(String(50), nullable=True)  # Video codec
    audio_codec = Column(String(50), nullable=True)  # Audio codec

    # Content metadata
    series = Column(String(500), nullable=True, index=True)
    season = Column(Integer, nullable=True)
    episode = Column(Integer, nullable=True)
    year = Column(Integer, nullable=True)
    director = Column(String(255), nullable=True)
    actors = Column(Text, nullable=True)  # Comma-separated
    genre = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # Comma-separated tags

    # Rating and statistics
    rating = Column(Float, nullable=True)  # User rating 0-5
    play_count = Column(Integer, default=0, nullable=False)
    is_favorite = Column(Integer, default=0, nullable=False)

    # File hash for duplicate detection
    file_hash = Column(String(64), nullable=True, index=True)

    # Relationships
    library = relationship("Library", back_populates="video_items")
    progress = relationship(
        "VideoProgress",
        back_populates="video",
        uselist=False,
        cascade="all, delete-orphan",
    )
    playlist_items = relationship(
        "PlaylistItem",
        back_populates="video",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"Video(id={self.id}, title={self.title!r}, duration={self.duration}s)"


class VideoProgress(Base, BaseModel):
    """
    Video playback progress tracking
    Stores current position and playback history
    """

    __tablename__ = "video_progress"

    video_id = Column(
        Integer,
        ForeignKey("videos.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    position = Column(Integer, default=0, nullable=False)  # Position in seconds
    last_played_at = Column(String(50), nullable=True)  # ISO format datetime string
    watch_time = Column(Integer, default=0, nullable=False)  # Total watch time in seconds
    is_completed = Column(Integer, default=0, nullable=False)

    # Playback preferences for this video
    volume = Column(Integer, nullable=True)  # Volume level 0-100
    playback_speed = Column(Float, nullable=True)  # Playback speed multiplier
    subtitle_track = Column(Integer, nullable=True)  # Selected subtitle track index
    audio_track = Column(Integer, nullable=True)  # Selected audio track index

    # Relationships
    video = relationship("Video", back_populates="progress")

    def __repr__(self) -> str:
        return f"VideoProgress(video_id={self.video_id}, position={self.position}s)"


class Playlist(Base, BaseModel):
    """
    Playlist model for organizing videos
    Users can create custom playlists
    """

    __tablename__ = "playlists"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    thumbnail_path = Column(String(1024), nullable=True)
    is_auto = Column(Integer, default=0, nullable=False)  # Auto-generated playlist
    sort_order = Column(Integer, default=0, nullable=False)

    # Relationships
    items = relationship(
        "PlaylistItem",
        back_populates="playlist",
        cascade="all, delete-orphan",
        order_by="PlaylistItem.position",
    )

    def __repr__(self) -> str:
        return f"Playlist(id={self.id}, name={self.name!r})"


class PlaylistItem(Base, BaseModel):
    """
    Playlist item linking videos to playlists
    Maintains order of videos in playlist
    """

    __tablename__ = "playlist_items"

    playlist_id = Column(Integer, ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False)
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)  # Order in playlist

    # Relationships
    playlist = relationship("Playlist", back_populates="items")
    video = relationship("Video", back_populates="playlist_items")

    def __repr__(self) -> str:
        return f"PlaylistItem(playlist_id={self.playlist_id}, video_id={self.video_id})"
