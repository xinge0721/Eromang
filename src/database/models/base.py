"""
Base models and mixins for database tables
Provides common fields and functionality for all models
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps"""

    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=datetime.utcnow, nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            nullable=False,
        )


class BaseModel(TimestampMixin):
    """Base model with common fields"""

    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True, autoincrement=True)

    def to_dict(self) -> dict:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation of model"""
        class_name = self.__class__.__name__
        attrs = ", ".join(
            f"{key}={value!r}"
            for key, value in self.to_dict().items()
            if key != "id"
        )
        return f"{class_name}(id={self.id}, {attrs})"
