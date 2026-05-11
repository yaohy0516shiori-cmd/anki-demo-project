import sqlite3
from ..reviewlogger.review import ReviewLog
from ..reviewlogger.log_repository import ReviewLogRepository
class SqliteReviewLogRepository(ReviewLogRepository):
    def __init__(self,conn:sqlite3.Connection):
        self.__conn=conn

    def __serialize_log(self,review_log:ReviewLog)->dict:
        def __date_to_str(value):
            return value.isoformat() if hasattr(value, "isoformat") else value
        return {
            'card_id':review_log.card_id,
            'user_id':review_log.user_id,
            'deck_id':review_log.deck_id,
            'rating':review_log.rating,
            'old_status':review_log.old_status,
            'new_status':review_log.new_status,
            'old_due':__date_to_str(review_log.old_due),
            'new_due':__date_to_str(review_log.new_due),
            'old_interval':review_log.old_interval,
            'new_interval':review_log.new_interval,
            'old_ease':review_log.old_ease,
            'new_ease':review_log.new_ease,
            'old_lapses':review_log.old_lapses,
            'new_lapses':review_log.new_lapses,
            'old_reps':review_log.old_reps,
            'new_reps':review_log.new_reps,
            'old_step_index':review_log.old_step_index,
            'new_step_index':review_log.new_step_index,
            'hint_used':review_log.hint_used,
            'review_time':review_log.review_time,
        }
    
    def __deserialize_log(self,row:sqlite3.Row)->ReviewLog:
        return ReviewLog(
            review_log_id=row['review_log_id'],
            card_id=row['card_id'],
            user_id=row['user_id'],
            deck_id=row['deck_id'],
            rating=row['rating'],
            old_status=row['old_status'],
            new_status=row['new_status'],
            old_due=row['old_due'],
            new_due=row['new_due'],
            old_interval=row['old_interval'],
            new_interval=row['new_interval'],
            old_ease=row['old_ease'],
            new_ease=row['new_ease'],
            old_lapses=row['old_lapses'],
            new_lapses=row['new_lapses'],
            old_reps=row['old_reps'],
            new_reps=row['new_reps'],
            old_step_index=row['old_step_index'],
            new_step_index=row['new_step_index'],
            hint_used=bool(row['hint_used']),
            review_time=row['review_time'],
        )
    
    def add_log(self, user_id:int, review_log:ReviewLog):
        if review_log.review_log_id is not None:
            raise ValueError("Review log ID must be None")
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        data=self.__serialize_log(review_log)
        cursor=self.__conn.execute(
            """
            INSERT INTO review_log (
            user_id,
            card_id,
            deck_id,
            rating,
            old_status,
            new_status,
            old_due,
            new_due,
            old_interval,
            new_interval,
            old_ease,
            new_ease,
            old_lapses,
            new_lapses,
            old_reps,
            new_reps,
            old_step_index,
            new_step_index,
            hint_used,
            review_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id,
            data['card_id'], 
            data['deck_id'],
            data['rating'], 
            data['old_status'], 
            data['new_status'], 
            data['old_due'], 
            data['new_due'], 
            data['old_interval'], 
            data['new_interval'], 
            data['old_ease'], 
            data['new_ease'], 
            data['old_lapses'], 
            data['new_lapses'], 
            data['old_reps'], 
            data['new_reps'], 
            data['old_step_index'], 
            data['new_step_index'], 
            data['hint_used'],
            data['review_time'])
            )
        log_id=cursor.lastrowid
        return self.get_log(user_id, log_id)
    
    def get_log(self, user_id:int, review_log_id:int)->ReviewLog:
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        if not isinstance(review_log_id,int):
            raise ValueError("Review log ID must be an integer")
        row=self.__conn.execute("SELECT * FROM review_log WHERE review_log_id=? AND user_id=?", (review_log_id,user_id)).fetchone()
        if row:
            return self.__deserialize_log(row)
        else:
            raise ValueError("Review log not found")
    
    def update_log(self, user_id:int, review_log:ReviewLog):
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        if not isinstance(review_log.review_log_id,int):
            raise ValueError("Review log ID must be an integer")
        data=self.__serialize_log(review_log)
        self.__conn.execute("""
        UPDATE review_log SET user_id=?,
        card_id=?,
        deck_id=?,
        rating=?,
        old_status=?,
        new_status=?,
        old_due=?,
        new_due=?,
        old_interval=?,
        new_interval=?,
        old_ease=?,
        new_ease=?,
        old_lapses=?,
        new_lapses=?,
        old_reps=?,
        new_reps=?,
        old_step_index=?,
        new_step_index=?,
        hint_used=?,
        review_time=? 
        WHERE review_log_id=?""", 
        (user_id,
        data['card_id'], 
        data['deck_id'],
        data['rating'], 
        data['old_status'], 
        data['new_status'], 
        data['old_due'], 
        data['new_due'], 
        data['old_interval'], 
        data['new_interval'], 
        data['old_ease'], 
        data['new_ease'], 
        data['old_lapses'], 
        data['new_lapses'], 
        data['old_reps'], 
        data['new_reps'], 
        data['old_step_index'], 
        data['new_step_index'], 
        data['hint_used'],
        data['review_time'],
        review_log.review_log_id))
    
    def delete_log(self, user_id:int, review_log_id:int):
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        if not isinstance(review_log_id,int):
            raise ValueError("Review log ID must be an integer")
        raise NotImplementedError("V1 does not support deleting review logs")

    def get_logs_by_card_id(self, user_id:int, card_id:int)->list[ReviewLog]:
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        if not isinstance(card_id,int):
            raise ValueError("Card ID must be an integer")
        rows=self.__conn.execute("SELECT * FROM review_log WHERE card_id=?", (card_id,)).fetchall()
        return [self.__deserialize_log(row) for row in rows]
    
    def get_all_logs_by_user_id(self, user_id:int)->list[ReviewLog]:
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        rows=self.__conn.execute("SELECT * FROM review_log WHERE user_id=?", (user_id,)).fetchall()
        return [self.__deserialize_log(row) for row in rows]
    
    def count_logs_by_user_id(self, user_id:int)->int:
        if not isinstance(user_id,int):
            raise ValueError("User ID must be an integer")
        row=self.__conn.execute("SELECT COUNT(*) FROM review_log WHERE user_id=?", (user_id,)).fetchone()
        return row[0]
    
    def get_all_logs(self)->list[ReviewLog]:
        rows=self.__conn.execute("SELECT * FROM review_log").fetchall()
        return [self.__deserialize_log(row) for row in rows]
    
    def count_logs(self)->int:
        row=self.__conn.execute("SELECT COUNT(*) FROM review_log").fetchone()
        return row[0]