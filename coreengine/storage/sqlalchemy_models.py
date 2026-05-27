# this file is used to define the sqlalchemy models for the database
# __future__ import annotations is used to allow the use of forward references
from __future__ import annotations
# unique key generator
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, text, Text, JSON, Float, UniqueConstraint, Index, CheckConstraint
# orm is object-relational mapping, it is used to map the database tables to python classes
# Table is class, records are instances of the class, Column is class attribute, mapped_column is class attribute that is mapped to a database column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(255),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    decks: Mapped[list[DeckORM]] = relationship("DeckORM", back_populates="user", cascade="all, delete-orphan")

class DeckORM(Base):
    __tablename__ = "deck"
    __table_args__ = (
        Index("idx_deck_id", "deck_id"),
        Index("idx_deck_user_id", "user_id"),
        Index("idx_deck_is_default", "is_default"),
        Index("idx_one_default_deck_per_user", "user_id", unique=True, postgresql_where=text("is_default = true")),
        UniqueConstraint("user_id", "deck_name", name="uix_user_deck_name"),
    )
    deck_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    deck_name: Mapped[str] = mapped_column(String(255), nullable=False)
    deck_description: Mapped[str | None] = mapped_column(Text, nullable=True, default="")
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    user=relationship("UserORM", back_populates="deck")


class NoteORM(Base):
    __tablename__ = "note"
    __table_args__ = (
        Index("idx_not_use_checksum", "user_id", "note_type_id", "checksum"),
        Index("idx_note_user_id", "user_id", "note_id"),
        UniqueConstraint("user_id", "note_type_id", "checksum", name="uix_user_note_type_checksum"),
    )
    note_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    note_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fields_JSON: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    tags_JSON: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    sort_field: Mapped[str] = mapped_column(String(255), nullable=False)
    checksum: Mapped[str] = mapped_column(String(255), nullable=False)
    hint: Mapped[str] = mapped_column(String(255), nullable=False, default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class CardORM(Base):
    __tablename__ = "card"
    __table_args__ = (
        Index("idx_card_status_due", "user_id", "status", "due"),
        Index("idx_card_user_deck_due", "user_id", "deck_id", "due"),
        Index("idx_card_user_note", "user_id", "note_id"),
        UniqueConstraint("user_id", "note_id", "template_ord", name="uix_user_note_template_ord"),
    )
    card_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("deck.deck_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    note_id: Mapped[int] = mapped_column(
        ForeignKey("note.note_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    template_ord: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="new", nullable=False)
    due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interval: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ease: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lapses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    step_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


class StudySessionORM(Base):
    __tablename__ = "study_session"
    __table_args__ = (
        Index("idx_study_session_deck_id", "deck_id"),
        Index("idx_study_session_today", "today"),
        Index("idx_study_session_user_id", "user_id"),
        CheckConstraint("status IN ('active', 'completed', 'interrupted')", name="ck_status"),
        CheckConstraint("current_hint_used IN (0, 1)", name="ck_current_hint_used"),
        CheckConstraint("current_back_revealed IN (0, 1)", name="ck_current_back_revealed"),
    )
    study_session_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("deck.deck_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    current_card_id: Mapped[int | None] = mapped_column(
        ForeignKey("card.card_id", ondelete="SET NULL"),
        nullable=True,
    )
    current_hint_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    current_back_revealed: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    learning_queue: Mapped[list[int]] = mapped_column(
    JSONB,
    nullable=False,
    default=list,
    server_default=text("'[]'::jsonb"),
    )

    review_queue: Mapped[list[int]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )

    new_queue: Mapped[list[int]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default=text("'[]'::jsonb"),
    )
    today: Mapped[str] = mapped_column(Text, nullable=False, default=lambda: utc_now().date().isoformat())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class ReviewLogORM(Base):
    __tablename__ = "review_log"
    __table_args__ = (
        CheckConstraint("rating IN ('good', 'again')", name="ck_rating"),
        CheckConstraint("old_status IN ('new', 'learning', 'review','relearning')", name="ck_old_status"),
        CheckConstraint("new_status IN ('new', 'learning', 'review','relearning')", name="ck_new_status"),
        Index("idx_review_log_card_time", "user_id", "card_id"),
        Index("idx_review_log_deck_time", "user_id", "deck_id", "review_time"),
        Index("idx_review_log_user_time", "user_id", "review_time"),

    )
    review_log_id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("deck.deck_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    card_id: Mapped[int] = mapped_column(
        ForeignKey("card.card_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    note_id: Mapped[int] = mapped_column(
        ForeignKey("note.note_id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    rating: Mapped[str] = mapped_column(String(30), nullable=False)
    old_status: Mapped[str] = mapped_column(String(30), nullable=False)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)
    old_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    new_due: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    old_interval: Mapped[int] = mapped_column(Integer, nullable=False)
    new_interval: Mapped[int] = mapped_column(Integer, nullable=False)
    old_ease: Mapped[float] = mapped_column(Float, nullable=False)
    new_ease: Mapped[float] = mapped_column(Float, nullable=False)
    old_lapses: Mapped[int] = mapped_column(Integer, nullable=False)
    new_lapses: Mapped[int] = mapped_column(Integer, nullable=False)
    old_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    new_reps: Mapped[int] = mapped_column(Integer, nullable=False)
    old_step_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    new_step_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hint_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    review_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

