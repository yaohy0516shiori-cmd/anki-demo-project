# this file is used to define the sqlalchemy models for the database
# __future__ import annotations is used to allow the use of forward references
from __future__ import annotations
# unique key generator
from datetime import datetime, timezone, date
from sqlalchemy import (
    DateTime, ForeignKey, Integer, 
    String, Boolean, text, Text, 
    Float, UniqueConstraint, 
    Index, CheckConstraint,Date)
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
    __table_args__ = (
        UniqueConstraint("email", name="uix_user_email"),
        UniqueConstraint("username", name="uix_user_username"),
    )
    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(255),nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now,nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now,nullable=False)

    decks: Mapped[list["DeckORM"]] = relationship("DeckORM", back_populates="user", cascade="all, delete-orphan")

class DeckORM(Base):
    __tablename__ = "deck"
    __table_args__ = (
        Index("idx_one_default_deck_per_user", "user_id", unique=True, postgresql_where=text("is_default = true")),
        UniqueConstraint("user_id", "deck_name", name="uix_user_deck_name"),
        Index("idx_user_id", "user_id"),
    )
    deck_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    deck_name: Mapped[str] = mapped_column(String(255), nullable=False)
    deck_description: Mapped[str | None] = mapped_column(Text, nullable=True, default="", server_default="")
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    user: Mapped["UserORM"] = relationship("UserORM", back_populates="decks")


class NoteORM(Base):
    __tablename__ = "note"
    __table_args__ = (
        Index("idx_note_user_checksum", "user_id", "note_type_id", "checksum"),
        Index("idx_note_user_id", "user_id", "note_id"),
        UniqueConstraint("user_id", "note_type_id", "checksum", name="uix_user_note_type_checksum"),
    )
    note_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    note_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    fields_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    tags_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False,default=list,server_default=text("'[]'::jsonb"))
    sort_field: Mapped[str] = mapped_column(String(255), nullable=False)
    checksum: Mapped[str] = mapped_column(String(255), nullable=False)
    hint: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class CardORM(Base):
    __tablename__ = "card"
    __table_args__ = (
        UniqueConstraint("user_id", "note_id", "template_ord", name="uix_user_note_template_ord"),
        CheckConstraint("status IN ('new', 'learning', 'review', 'relearning')", name="ck_card_status"),
        CheckConstraint("template_ord >= 0", name="ck_card_template_ord_non_negative"),
        CheckConstraint("interval >= 0", name="ck_card_interval_non_negative"),
        CheckConstraint("ease > 0", name="ck_card_ease_positive"),
        CheckConstraint("reps >= 0", name="ck_card_reps_non_negative"),
        CheckConstraint("lapses >= 0", name="ck_card_lapses_non_negative"),
        Index("idx_card_status_due", "user_id", "status", "due"),
        Index("idx_card_user_deck_due", "user_id", "deck_id", "due"),
        Index("idx_card_user_note", "user_id", "note_id"),
    )
    card_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        ForeignKey("deck.deck_id", ondelete="CASCADE"),
        nullable=False,
    )
    note_id: Mapped[int] = mapped_column(
        ForeignKey("note.note_id", ondelete="CASCADE"),
        nullable=False,
    )

    template_ord: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="new", server_default="new", nullable=False)

    due: Mapped[date] = mapped_column(Date, nullable=False)

    interval: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    ease: Mapped[float] = mapped_column(Float, default=2.5, server_default="2.5", nullable=False)
    reps: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    lapses: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
    step_index: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class StudySessionORM(Base):
    __tablename__ = "study_session"

    __table_args__ = (
        UniqueConstraint("session_id", name="uix_study_session_session_id"),
        CheckConstraint("status = 'active'", name="ck_study_session_status"),
        Index("idx_study_session_user_id", "user_id"),
        Index("idx_study_session_user_deck_today", "user_id", "deck_id", "today"),
        Index("idx_study_session_user_session_id", "user_id", "session_id"),
    )

    study_session_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    session_id: Mapped[str] = mapped_column(String(36), nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    deck_id: Mapped[int] = mapped_column(
        ForeignKey("deck.deck_id", ondelete="CASCADE"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        server_default="active",
        nullable=False,
    )

    current_card_id: Mapped[int | None] = mapped_column(
        ForeignKey("card.card_id", ondelete="SET NULL"),
        nullable=True,
    )

    current_hint_used: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    current_back_revealed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

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

    today: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=lambda: utc_now().date(),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class ReviewLogORM(Base):
    __tablename__ = "review_log"

    __table_args__ = (
        CheckConstraint("rating IN ('good', 'again')", name="ck_review_log_rating"),
        CheckConstraint("old_status IN ('new', 'learning', 'review', 'relearning')", name="ck_review_log_old_status"),
        CheckConstraint("new_status IN ('new', 'learning', 'review', 'relearning')", name="ck_review_log_new_status"),
        CheckConstraint("old_interval >= 0", name="ck_review_log_old_interval_non_negative"),
        CheckConstraint("new_interval >= 0", name="ck_review_log_new_interval_non_negative"),
        CheckConstraint("old_ease > 0", name="ck_review_log_old_ease_positive"),
        CheckConstraint("new_ease > 0", name="ck_review_log_new_ease_positive"),
        CheckConstraint("old_lapses >= 0", name="ck_review_log_old_lapses_non_negative"),
        CheckConstraint("new_lapses >= 0", name="ck_review_log_new_lapses_non_negative"),
        CheckConstraint("old_reps >= 0", name="ck_review_log_old_reps_non_negative"),
        CheckConstraint("new_reps >= 0", name="ck_review_log_new_reps_non_negative"),
        Index("idx_review_log_card_time", "user_id", "card_id"),
        Index("idx_review_log_deck_time", "user_id", "deck_id", "review_time"),
        Index("idx_review_log_user_time", "user_id", "review_time"),
    )

    review_log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    deck_id: Mapped[int | None] = mapped_column(
        ForeignKey("deck.deck_id", ondelete="SET NULL"),
        nullable=True,
    )

    card_id: Mapped[int | None] = mapped_column(
        ForeignKey("card.card_id", ondelete="SET NULL"),
        nullable=True,
    )

    note_id: Mapped[int | None] = mapped_column(
        ForeignKey("note.note_id", ondelete="SET NULL"),
        nullable=True,
    )

    rating: Mapped[str] = mapped_column(String(30), nullable=False)
    old_status: Mapped[str] = mapped_column(String(30), nullable=False)
    new_status: Mapped[str] = mapped_column(String(30), nullable=False)

    old_due: Mapped[date | None] = mapped_column(Date, nullable=True)
    new_due: Mapped[date | None] = mapped_column(Date, nullable=True)

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

    hint_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")

    review_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

class AICardDraftBatchORM(Base):
    __tablename__ = "ai_card_draft_batch"

    __table_args__=(
        CheckConstraint(
            "status IN ('pending', 'confirmed', 'discarded')",
            name="ck_ai_card_draft_batch_status",
        ),
        Index("idx_ai_card_draft_batch_user_status", "user_id", "status"),
        Index("idx_ai_card_draft_batch_user_created", "user_id", "created_at"),
    )

    batch_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    deck_id: Mapped[int] = mapped_column(ForeignKey("deck.deck_id", ondelete="SET NULL"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False, default = 'text', server_default = 'text')
    source_text: Mapped[str] = mapped_column(Text, nullable=False)
    user_prompt: Mapped[str] = mapped_column(Text, nullable=False, default = '', server_default = '')
    status: Mapped[str] = mapped_column(String(30), nullable=False, default = 'pending', server_default = 'pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

class AICardDraftItemORM(Base):
    __tablename__ = "ai_card_draft_item"

    __table_args__=(
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'created', 'failed')",
            name="ck_ai_card_draft_item_status",
        ),
        Index("idx_ai_card_draft_item_user_batch","user_id", "batch_id"),
    )
    item_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("ai_card_draft_batch.batch_id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    note_type_id: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default = 'pending', server_default = 'pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    created_note_id: Mapped[int] = mapped_column(ForeignKey("note.note_id", ondelete="SET NULL"), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default = '', server_default = '')

class AICardDraftVersionORM(Base):
    __tablename__ = "ai_card_draft_version"

    __table_args__ = (
        UniqueConstraint("item_id", "version_no", name="uix_ai_card_draft_item_version"),
        Index("idx_ai_card_draft_version_item", "item_id"),
    )

    version_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    item_id: Mapped[int] = mapped_column(
        ForeignKey("ai_card_draft_item.item_id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    version_no: Mapped[int] = mapped_column(Integer, nullable=False)

    fields_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    tags_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list, server_default=text("'[]'::jsonb"))
    hint: Mapped[str] = mapped_column(String(255), nullable=False, default="", server_default="")
    reason: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    user_instruction: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    created_by: Mapped[str] = mapped_column(String(30), nullable=False, default="ai", server_default="ai")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)