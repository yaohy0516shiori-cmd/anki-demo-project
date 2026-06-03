from __future__ import annotations
from datetime import date, datetime, time, timedelta, timezone
from math import ceil
from typing import Any
from sqlalchemy import Date, Text, and_, case, cast, func, or_, select
from sqlalchemy.orm import Session as DbSession
from coreengine.storage.sqlalchemy_models import CardORM, DeckORM, NoteORM, ReviewLogORM

VALID_CARD_STATUSES = {"new", "learning", "review", "relearning"}
VALID_CARD_SORTS = {
    "due_asc",
    "due_desc",
    "created_asc",
    "created_desc",
    "reps_desc",
    "lapses_desc",
}

class DashboardQueryRepository:
    """
    Read-only query repository for dashboard/search pages.
    Business writes still go through core services. This class only builds
    UI-friendly read models: pagination, filtering, search, and aggregation.
    """

    def __init__(self, db: DbSession):
        self.__db = db

    def list_deck_cards(
        self,
        user_id: int,
        deck_id: int,
        *,
        page: int = 1,
        page_size: int = 20,
        q: str | None = None,
        status: str | None = None,
        due_before: date | None = None,
        due_after: date | None = None,
        sort: str = "due_asc",
    ) -> dict[str, Any]:
        self.__validate_deck(user_id, deck_id)
        page, page_size = self.__normalize_page(page, page_size)

        if status is not None and status not in VALID_CARD_STATUSES:
            raise ValueError("Invalid card status")
        if sort not in VALID_CARD_SORTS:
            raise ValueError("Invalid card sort")

        filters = [
            CardORM.user_id == user_id,
            CardORM.deck_id == deck_id,
        ]

        if status:
            filters.append(CardORM.status == status)
        if due_before:
            filters.append(CardORM.due <= due_before)
        if due_after:
            filters.append(CardORM.due >= due_after)

        cleaned_q = q.strip() if q else ""
        if cleaned_q:
            pattern = f"%{cleaned_q}%"
            filters.append(
                or_(
                    NoteORM.sort_field.ilike(pattern),
                    cast(NoteORM.fields_json, Text).ilike(pattern),
                    cast(NoteORM.tags_json, Text).ilike(pattern),
                    cast(NoteORM.hint, Text).ilike(pattern),
                )
            )

        join_condition = and_(
            CardORM.note_id == NoteORM.note_id,
            CardORM.user_id == NoteORM.user_id,
        )

        count_stmt = (
            select(func.count())
            .select_from(CardORM)
            .join(NoteORM, join_condition)
            .where(*filters)
        )
        total = self.__db.execute(count_stmt).scalar_one()

        order_by = self.__card_order_by(sort)
        rows_stmt = (
            select(CardORM, NoteORM)
            .join(NoteORM, join_condition)
            .where(*filters)
            .order_by(*order_by)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        rows = self.__db.execute(rows_stmt).all()
        items = [self.__card_row_to_dict(card, note) for card, note in rows]

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
        }

    def search_cards(
        self,
        user_id: int,
        *,
        q: str,
        page: int = 1,
        page_size: int = 20,
        deck_id: int | None = None,
        status: str | None = None,
        due_before: date | None = None,
        due_after: date | None = None,
        sort: str = "due_asc",
    ) -> dict[str, Any]:
        page, page_size = self.__normalize_page(page, page_size)

        cleaned_q = q.strip()
        if not cleaned_q:
            raise ValueError("Search keyword is required")

        if deck_id is not None:
            self.__validate_deck(user_id, deck_id)

        if status is not None and status not in VALID_CARD_STATUSES:
            raise ValueError("Invalid card status")

        if sort not in VALID_CARD_SORTS:
            raise ValueError("Invalid card sort")

        pattern = f"%{cleaned_q}%"

        filters = [
            CardORM.user_id == user_id,
            or_(
                NoteORM.sort_field.ilike(pattern),
                NoteORM.hint.ilike(pattern),
                cast(NoteORM.fields_json, Text).ilike(pattern),
                cast(NoteORM.tags_json, Text).ilike(pattern),
            ),
        ]

        if deck_id is not None:
            filters.append(CardORM.deck_id == deck_id)

        if status:
            filters.append(CardORM.status == status)

        if due_before:
            filters.append(CardORM.due <= due_before)

        if due_after:
            filters.append(CardORM.due >= due_after)

        join_condition = and_(
            CardORM.note_id == NoteORM.note_id,
            CardORM.user_id == NoteORM.user_id,
        )

        count_stmt = (
            select(func.count())
            .select_from(CardORM)
            .join(NoteORM, join_condition)
            .where(*filters)
        )
        total = self.__db.execute(count_stmt).scalar_one()

        rows_stmt = (
            select(CardORM, NoteORM)
            .join(NoteORM, join_condition)
            .where(*filters)
            .order_by(*self.__card_order_by(sort))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        rows = self.__db.execute(rows_stmt).all()
        items = [self.__card_row_to_dict(card, note) for card, note in rows]

        return {
            "items": items,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": ceil(total / page_size) if total else 0,
        }

    def get_summary_stats(self, user_id: int, today: date) -> dict[str, Any]:
        status_counts = self.__card_status_counts(user_id)
        rating_counts = self.__rating_counts(user_id)
        today_rating_counts = self.__rating_counts_on_day(user_id, today)

        total_reviews = sum(rating_counts.values())
        good_reviews = rating_counts.get("good", 0)
        again_reviews = rating_counts.get("again", 0)
        today_good_reviews = today_rating_counts.get("good", 0)
        today_again_reviews = today_rating_counts.get("again", 0)
        today_reviews = today_good_reviews + today_again_reviews
        good_rate = round(good_reviews / total_reviews, 4) if total_reviews else 0.0

        latest_review_time = self.__db.execute(
            select(func.max(ReviewLogORM.review_time)).where(ReviewLogORM.user_id == user_id)
        ).scalar_one()

        return {
            "total_decks": self.__count(DeckORM, DeckORM.user_id == user_id),
            "total_notes": self.__count(NoteORM, NoteORM.user_id == user_id),
            "total_cards": self.__count(CardORM, CardORM.user_id == user_id),
            "due_today_cards": self.__count(
                CardORM,
                CardORM.user_id == user_id,
                CardORM.due <= today,
            ),
            "new_cards": status_counts.get("new", 0),
            "learning_cards": status_counts.get("learning", 0),
            "review_cards": status_counts.get("review", 0),
            "relearning_cards": status_counts.get("relearning", 0),
            "total_reviews": total_reviews,
            "today_reviews": today_reviews,
            "today_good_reviews": today_good_reviews,
            "today_again_reviews": today_again_reviews,
            "good_reviews": good_reviews,
            "again_reviews": again_reviews,
            "good_rate": good_rate,
            "latest_review_time": latest_review_time.isoformat() if latest_review_time else None,
        }

    def get_decks_stats(self, user_id: int, today: date) -> list[dict[str, Any]]:
        decks = self.__db.execute(
            select(DeckORM).where(DeckORM.user_id == user_id).order_by(DeckORM.deck_id)
        ).scalars().all()

        status_rows = self.__db.execute(
            select(CardORM.deck_id, CardORM.status, func.count())
            .where(CardORM.user_id == user_id)
            .group_by(CardORM.deck_id, CardORM.status)
        ).all()
        status_by_deck: dict[int, dict[str, int]] = {}
        for deck_id, status, count in status_rows:
            status_by_deck.setdefault(deck_id, {})[status] = count

        due_rows = self.__db.execute(
            select(CardORM.deck_id, func.count())
            .where(CardORM.user_id == user_id, CardORM.due <= today)
            .group_by(CardORM.deck_id)
        ).all()
        due_by_deck = {deck_id: count for deck_id, count in due_rows}

        review_rows = self.__db.execute(
            select(
                ReviewLogORM.deck_id,
                func.count(ReviewLogORM.review_log_id),
                func.sum(case((ReviewLogORM.rating == "good", 1), else_=0)),
                func.sum(case((ReviewLogORM.rating == "again", 1), else_=0)),
                func.max(ReviewLogORM.review_time),
            )
            .where(
                ReviewLogORM.user_id == user_id,
                ReviewLogORM.deck_id.is_not(None),
            )
            .group_by(ReviewLogORM.deck_id)
        ).all()

        reviews_by_deck: dict[int, dict[str, Any]] = {}
        for deck_id, review_count, good_count, again_count, latest_review_time in review_rows:
            reviews_by_deck[deck_id] = {
                "review_log_count": review_count or 0,
                "good_count": good_count or 0,
                "again_count": again_count or 0,
                "latest_review_time": latest_review_time.isoformat() if latest_review_time else None,
            }

        result = []
        for deck in decks:
            deck_status_counts = status_by_deck.get(deck.deck_id, {})
            review_stats = reviews_by_deck.get(deck.deck_id, {})
            result.append(
                {
                    "deck_id": deck.deck_id,
                    "deck_name": deck.deck_name,
                    "deck_description": deck.deck_description or "",
                    "is_default": deck.is_default,
                    "card_count": sum(deck_status_counts.values()),
                    "due_today_count": due_by_deck.get(deck.deck_id, 0),
                    "new_count": deck_status_counts.get("new", 0),
                    "learning_count": deck_status_counts.get("learning", 0),
                    "review_count": deck_status_counts.get("review", 0),
                    "relearning_count": deck_status_counts.get("relearning", 0),
                    "review_log_count": review_stats.get("review_log_count", 0),
                    "good_count": review_stats.get("good_count", 0),
                    "again_count": review_stats.get("again_count", 0),
                    "latest_review_time": review_stats.get("latest_review_time"),
                }
            )

        return result

    def get_daily_review_stats(
        self,
        user_id: int,
        *,
        today: date,
        days: int = 14,
        deck_id: int | None = None,
    ) -> list[dict[str, Any]]:
        if days < 1 or days > 365:
            raise ValueError("days must be between 1 and 365")

        if deck_id is not None:
            self.__validate_deck(user_id, deck_id)

        start_day = today - timedelta(days=days - 1)
        start_dt = datetime.combine(start_day, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(today + timedelta(days=1), time.min, tzinfo=timezone.utc)

        filters = [
            ReviewLogORM.user_id == user_id,
            ReviewLogORM.review_time >= start_dt,
            ReviewLogORM.review_time < end_dt,
        ]
        if deck_id is not None:
            filters.append(ReviewLogORM.deck_id == deck_id)

        rows = self.__db.execute(
            select(
                cast(ReviewLogORM.review_time, Date).label("day"),
                func.count(ReviewLogORM.review_log_id),
                func.sum(case((ReviewLogORM.rating == "good", 1), else_=0)),
                func.sum(case((ReviewLogORM.rating == "again", 1), else_=0)),
            )
            .where(*filters)
            .group_by("day")
            .order_by("day")
        ).all()

        by_day = {
            self._coerce_date(day).isoformat(): {
                "review_count": review_count or 0,
                "good_count": good_count or 0,
                "again_count": again_count or 0,
            }
            for day, review_count, good_count, again_count in rows
        }

        result = []
        for offset in range(days):
            current = start_day + timedelta(days=offset)
            key = current.isoformat()
            counts = by_day.get(key, {"review_count": 0, "good_count": 0, "again_count": 0})
            result.append({"date": key, **counts})

        return result


    def get_due_forecast_stats(self,user_id:int,*,today:date,days:int=7,deck_id:int|None=None) -> list[dict[str,Any]]:
        if days < 1 or days > 31:
            raise ValueError("days must be between 1 and 31")
        if deck_id is not None:
            self.__validate_deck(user_id, deck_id)
        end_day = today + timedelta(days=days-1)
        filters = [
            CardORM.user_id == user_id,
            CardORM.due >= today,
            CardORM.due <= end_day,
        ]
        if deck_id is not None:
            filters.append(CardORM.deck_id == deck_id)
        rows = self.__db.execute(
            select(CardORM.due, func.count(CardORM.card_id)).where(*filters).group_by(CardORM.due).order_by(CardORM.due)
        )
        by_day = {
            self._coerce_date(day).isoformat(): count for day, count in rows
        }
        return [{
            "date":(today + timedelta(days=offset)).isoformat(),
            "due_count": by_day.get((today + timedelta(days=offset)).isoformat(), 0),
        } for offset in range(days)]
    
    def get_monthly_review_stats(self,user_id:int,*,year:int,month:int,deck_id:int|None=None) -> list[dict[str,Any]]:
        if year < 1970 or year > 3000:
            raise ValueError("Invalid year")
        if month < 1 or month > 12:
            raise ValueError("month must be between 1 and 12")
        if deck_id is not None:
            self.__validate_deck(user_id, deck_id)
        start_day = date(year, month, 1)
        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)
        start_dt = datetime.combine(start_day, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(next_month, time.min, tzinfo=timezone.utc)
        rows= self.__db.execute(
            select(ReviewLogORM.rating, cast(ReviewLogORM.review_time, Date).label("day"))
            .where(ReviewLogORM.user_id == user_id, ReviewLogORM.review_time >= start_dt, ReviewLogORM.review_time < end_dt)
            .group_by("day", "rating")
        ).all()
        by_day: dict[str, dict[str, int]] = {}
        current=start_day
        while current < next_month:
            by_day[current.isoformat()] = {
                "review_count": 0,
                "good_count": 0,
                "again_count": 0,
            }
            current += timedelta(days=1)
        for rating, review_time in rows:
            day_key = self._coerce_date(review_time).date()
            if day_key not in by_day:
                continue
            by_day[day_key]["review_count"] += 1
            if rating == "good":
                by_day[day_key]["good_count"] += 1
            elif rating == "again":
                by_day[day_key]["again_count"] += 1
        return [{"period": key, **counts} for key, counts in by_day.items()]

    def get_yearly_review_stats(
        self,
        user_id: int,
        *,
        year: int,
        deck_id: int | None = None,
    ) -> list[dict[str, Any]]:
        if year < 1970 or year > 3000:
            raise ValueError("Invalid year")
        if deck_id is not None:
            self.__validate_deck(user_id, deck_id)

        start_day = date(year, 1, 1)
        next_year = date(year + 1, 1, 1)
        start_dt = datetime.combine(start_day, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(next_year, time.min, tzinfo=timezone.utc)
        rows = self.__db.execute(
            select(ReviewLogORM.rating, cast(ReviewLogORM.review_time, Date).label("month"))
            .where(ReviewLogORM.user_id == user_id, ReviewLogORM.review_time >= start_dt, ReviewLogORM.review_time < end_dt)
            .group_by("month", "rating")
        ).all()

        by_month = {
            f"{year}-{month:02d}": {
                "review_count": 0,
                "good_count": 0,
                "again_count": 0,
            }
            for month in range(1, 13)
        }

        for rating, review_time in rows:
            dt = self._coerce_date(review_time).date()
            month_key = f"{dt.year}-{dt.month:02d}"
            if month_key not in by_month:
                continue
            by_month[month_key]["review_count"] += 1
            if rating == "good":
                by_month[month_key]["good_count"] += 1
            elif rating == "again":
                by_month[month_key]["again_count"] += 1

        return [{"period": key, **counts} for key, counts in by_month.items()]

    def _validate_deck(self, user_id: int, deck_id: int) -> None:
        exists = self.__db.execute(
            select(DeckORM.deck_id).where(
                DeckORM.user_id == user_id,
                DeckORM.deck_id == deck_id,
            )
        ).scalar_one_or_none()
        if exists is None:
            raise ValueError("Deck not found")

    def _normalize_page(self, page: int, page_size: int) -> tuple[int, int]:
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")
        return page, page_size

    def _card_order_by(self, sort: str):
        if sort == "due_desc":
            return [CardORM.due.desc(), CardORM.card_id.desc()]
        if sort == "created_asc":
            return [CardORM.created_at.asc(), CardORM.card_id.asc()]
        if sort == "created_desc":
            return [CardORM.created_at.desc(), CardORM.card_id.desc()]
        if sort == "reps_desc":
            return [CardORM.reps.desc(), CardORM.card_id.asc()]
        if sort == "lapses_desc":
            return [CardORM.lapses.desc(), CardORM.card_id.asc()]
        return [CardORM.due.asc(), CardORM.card_id.asc()]

    def _card_row_to_dict(self, card: CardORM, note: NoteORM) -> dict[str, Any]:
        return {
            "card_id": card.card_id,
            "note_id": card.note_id,
            "deck_id": card.deck_id,
            "template_ord": card.template_ord,
            "status": card.status,
            "due": card.due.isoformat(),
            "interval": card.interval,
            "ease": card.ease,
            "reps": card.reps,
            "lapses": card.lapses,
            "step_index": card.step_index,
            "note_type_id": note.note_type_id,
            "content": self._format_note_content(note.fields_json),
            "tags": list(note.tags_json or []),
            "hint": note.hint or "",
            "created_at": card.created_at.isoformat() if card.created_at else "",
            "updated_at": card.updated_at.isoformat() if card.updated_at else "",
        }

    def _format_note_content(self, fields_json) -> str:
        if fields_json is None:
            return ""
        fields = fields_json if isinstance(fields_json, list) else [fields_json]
        return " / ".join(str(field).strip() for field in fields if str(field).strip())

    def __card_status_counts(self, user_id: int) -> dict[str, int]:
        rows = self.__db.execute(
            select(CardORM.status, func.count())
            .where(CardORM.user_id == user_id)
            .group_by(CardORM.status)
        ).all()
        return {status: count for status, count in rows}

    def _rating_counts(self, user_id: int) -> dict[str, int]:
        rows = self.__db.execute(
            select(ReviewLogORM.rating, func.count())
            .where(ReviewLogORM.user_id == user_id)
            .group_by(ReviewLogORM.rating)
        ).all()
        return {rating: count for rating, count in rows}

    def _today_review_count(self, user_id: int, today: date) -> int:
        start_dt = datetime.combine(today, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(today + timedelta(days=1), time.min, tzinfo=timezone.utc)
        return self.__count(
            ReviewLogORM,
            ReviewLogORM.user_id == user_id,
            ReviewLogORM.review_time >= start_dt,
            ReviewLogORM.review_time < end_dt,
        )

    def _count(self, model, *filters) -> int:
        return self.__db.execute(select(func.count()).select_from(model).where(*filters)).scalar_one()

    def _coerce_date(self, value) -> date:
        if isinstance(value, date):
            return value
        return datetime.fromisoformat(str(value)).date()
