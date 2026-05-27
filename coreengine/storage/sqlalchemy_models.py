# this file is used to define the sqlalchemy models for the database
# __future__ import annotations is used to allow the use of forward references
from __future__ import annotations
# unique key generator
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, Column, Text, JSON
# orm is object-relational mapping, it is used to map the database tables to python classes
# Table is class, records are instances of the class, Column is class attribute, mapped_column is class attribute that is mapped to a database column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

def utc_now() -> str:
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
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    decks: Mapped[list[DeckORM]] = relationship("DeckORM", back_populates="user", cascade="all, delete-orphan")

class DeckORM(Base):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    user: Mapped[UserORM] = relationship(back_populates="decks")
    notes: Mapped[list[NoteORM]] = relationship(
        back_populates="deck",
        cascade="all, delete-orphan",
    )
    cards: Mapped[list[CardORM]] = relationship(
        back_populates="deck",
        cascade="all, delete-orphan",
    )


class NoteORM(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("decks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    note_type: Mapped[str] = mapped_column(String(50), default="basic", nullable=False)
    fields: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    deck: Mapped[DeckORM] = relationship(back_populates="notes")
    cards: Mapped[list[CardORM]] = relationship(
        back_populates="note",
        cascade="all, delete-orphan",
    )


class CardORM(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("decks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    note_id: Mapped[int] = mapped_column(
        ForeignKey("notes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    card_type: Mapped[str] = mapped_column(String(50), default="basic", nullable=False)
    front: Mapped[str] = mapped_column(Text, nullable=False)
    back: Mapped[str] = mapped_column(Text, nullable=False)

    state: Mapped[str] = mapped_column(String(30), default="new", nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interval_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ease_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lapses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    deck: Mapped[DeckORM] = relationship(back_populates="cards")
    note: Mapped[NoteORM] = relationship(back_populates="cards")
    review_logs: Mapped[list[ReviewLogORM]] = relationship(
        back_populates="card",
        cascade="all, delete-orphan",
    )


class StudySessionORM(Base):
    __tablename__ = "study_sessions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("decks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(String(30), default="active", nullable=False)
    current_card_id: Mapped[int | None] = mapped_column(
        ForeignKey("cards.id", ondelete="SET NULL"),
        nullable=True,
    )

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ReviewLogORM(Base):
    __tablename__ = "review_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("decks.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    card_id: Mapped[int] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    session_id: Mapped[str | None] = mapped_column(
        ForeignKey("study_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )

    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    previous_state: Mapped[str | None] = mapped_column(String(30), nullable=True)
    next_state: Mapped[str | None] = mapped_column(String(30), nullable=True)

    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    card: Mapped[CardORM] = relationship(back_populates="review_logs")


