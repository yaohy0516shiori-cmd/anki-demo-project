from sqlalchemy import func, select
from sqlalchemy.orm import Session as DbSession

from coreengine.reviewlogger.log_repository import ReviewLogRepository
from coreengine.reviewlogger.review import ReviewLog
from coreengine.storage.sqlalchemy_models import ReviewLogORM


class SqlAlchemyReviewLogRepository(ReviewLogRepository):
    def __init__(self, db: DbSession):
        self.__db = db

    def __to_domain(self, orm: ReviewLogORM) -> ReviewLog:
        return ReviewLog(
            review_log_id=orm.review_log_id,
            user_id=orm.user_id,
            card_id=orm.card_id,
            deck_id=orm.deck_id,
            note_id=orm.note_id,
            rating=orm.rating,
            old_status=orm.old_status,
            new_status=orm.new_status,
            old_due=orm.old_due,
            new_due=orm.new_due,
            old_interval=orm.old_interval,
            new_interval=orm.new_interval,
            old_ease=orm.old_ease,
            new_ease=orm.new_ease,
            old_lapses=orm.old_lapses,
            new_lapses=orm.new_lapses,
            old_reps=orm.old_reps,
            new_reps=orm.new_reps,
            old_step_index=orm.old_step_index,
            new_step_index=orm.new_step_index,
            hint_used=orm.hint_used,
            review_time=orm.review_time.isoformat() if orm.review_time else None,
        )

    def add_log(self, user_id: int, log: ReviewLog) -> ReviewLog:
        if log.review_log_id is not None:
            raise ValueError("Review log ID must be None")
        if log.user_id != user_id:
            raise ValueError("User ID does not match")

        orm = ReviewLogORM(
            user_id=user_id,
            card_id=log.card_id,
            deck_id=log.deck_id,
            note_id=log.note_id,
            rating=log.rating,
            old_status=log.old_status,
            new_status=log.new_status,
            old_due=log.old_due,
            new_due=log.new_due,
            old_interval=log.old_interval,
            new_interval=log.new_interval,
            old_ease=log.old_ease,
            new_ease=log.new_ease,
            old_lapses=log.old_lapses,
            new_lapses=log.new_lapses,
            old_reps=log.old_reps,
            new_reps=log.new_reps,
            old_step_index=log.old_step_index,
            new_step_index=log.new_step_index,
            hint_used=log.hint_used,
            review_time=log.review_time,
        )

        self.__db.add(orm)
        self.__db.flush()
        return self.get_log(user_id, orm.review_log_id)

    def get_log(self, user_id: int, review_log_id: int) -> ReviewLog:
        stmt = select(ReviewLogORM).where(
            ReviewLogORM.user_id == user_id,
            ReviewLogORM.review_log_id == review_log_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Review log not found")
        return self.__to_domain(orm)

    def update_log(self, user_id: int, log: ReviewLog) -> ReviewLog:
        stmt = select(ReviewLogORM).where(
            ReviewLogORM.user_id == user_id,
            ReviewLogORM.review_log_id == log.review_log_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Review log not found")

        orm.rating = log.rating
        orm.old_status = log.old_status
        orm.new_status = log.new_status
        orm.old_due = log.old_due
        orm.new_due = log.new_due
        orm.old_interval = log.old_interval
        orm.new_interval = log.new_interval
        orm.old_ease = log.old_ease
        orm.new_ease = log.new_ease
        orm.old_lapses = log.old_lapses
        orm.new_lapses = log.new_lapses
        orm.old_reps = log.old_reps
        orm.new_reps = log.new_reps
        orm.old_step_index = log.old_step_index
        orm.new_step_index = log.new_step_index
        orm.hint_used = log.hint_used
        orm.review_time = log.review_time

        self.__db.flush()
        return self.get_log(user_id, log.review_log_id)

    def delete_log(self, user_id: int, review_log_id: int) -> None:
        stmt = select(ReviewLogORM).where(
            ReviewLogORM.user_id == user_id,
            ReviewLogORM.review_log_id == review_log_id,
        )
        orm = self.__db.execute(stmt).scalar_one_or_none()
        if orm is None:
            raise ValueError("Review log not found")

        self.__db.delete(orm)
        self.__db.flush()

    def get_logs_by_card_id(self, user_id: int, card_id: int) -> list[ReviewLog]:
        stmt = (
            select(ReviewLogORM)
            .where(
                ReviewLogORM.user_id == user_id,
                ReviewLogORM.card_id == card_id,
            )
            .order_by(ReviewLogORM.review_time)
        )
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    def get_all_logs_by_user_id(self, user_id: int) -> list[ReviewLog]:
        stmt = (
            select(ReviewLogORM)
            .where(ReviewLogORM.user_id == user_id)
            .order_by(ReviewLogORM.review_time)
        )
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    def count_logs_by_user_id(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(ReviewLogORM).where(
            ReviewLogORM.user_id == user_id
        )
        return self.__db.execute(stmt).scalar_one()

    def get_all_logs(self) -> list[ReviewLog]:
        stmt = select(ReviewLogORM).order_by(ReviewLogORM.review_time)
        rows = self.__db.execute(stmt).scalars().all()
        return [self.__to_domain(row) for row in rows]

    def count_logs(self) -> int:
        stmt = select(func.count()).select_from(ReviewLogORM)
        return self.__db.execute(stmt).scalar_one()