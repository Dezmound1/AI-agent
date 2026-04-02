"""Модели пользователей и комментариев."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CommentCharacter(str, enum.Enum):
    """Характер / стиль высказывания (как сформулирован комментарий)."""

    FORMAL = "formal"
    CASUAL = "casual"
    EMOTIONAL = "emotional"
    SARCASTIC = "sarcastic"
    TECHNICAL = "technical"


class CommentSentiment(str, enum.Enum):
    """Настроение / оценочная тональность."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    comments: Mapped[list[Comment]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    body: Mapped[str] = mapped_column(Text())
    character: Mapped[CommentCharacter] = mapped_column(
        SAEnum(CommentCharacter, name="comment_character", native_enum=True),
    )
    sentiment: Mapped[CommentSentiment] = mapped_column(
        SAEnum(CommentSentiment, name="comment_sentiment", native_enum=True),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped[User] = relationship(back_populates="comments")
