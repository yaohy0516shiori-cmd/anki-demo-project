import sqlite3
from ..reviewlogger.review import ReviewLog

class SqliteReviewLogRepository:
    def __init__(self,conn:sqlite3.Connection):
        self.__conn=conn

    def __serialize_review_log(self,review_log:ReviewLog)->dict:
        return {
            'card_id':review_log.card_id,
            'rating':review_log.rating,
            'old_status':review_log.old_status,
            'new_status':review_log.new_status,
            'old_due':review_log.old_due,
            'new_due':review_log.new_due,
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
            'review_time':review_log.review_time,
        }
    
    def __deserialize_review_log(self,row:sqlite3.Row)->ReviewLog:
        return ReviewLog(
            review_log_id=row['review_log_id'],
            card_id=row['card_id'],
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
            review_time=row['review_time'],
        )
    
    def add_review_log(self,review_log:ReviewLog):
        if review_log.review_log_id is not None:
            raise ValueError("Review log ID must be None")
        data=self.__serialize_review_log(review_log)
        cursor=self.__conn.execute(
            """
            INSERT INTO review_log (
            card_id,
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
            review_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (data['card_id'], 
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
            data['review_time'])
            )
        self.__conn.commit()
        return cursor.lastrowid
    
    def get_review_log(self,review_log_id:int)->ReviewLog:
        row=self.__conn.execute("SELECT * FROM review_log WHERE review_log_id=?", (review_log_id,)).fetchone()
        if row:
            return self.__deserialize_review_log(row)
        else:
            raise ValueError("Review log not found")
    
    def update_review_log(self,review_log:ReviewLog):
        data=self.__serialize_review_log(review_log)
        self.__conn.execute("""
        UPDATE review_log SET card_id=?,
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
        review_time=? 
        WHERE review_log_id=?""", 
        (data['card_id'], 
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
        data['review_time'],
        review_log.review_log_id))
        self.__conn.commit()
    
    def delete_review_log(self,review_log_id:int):
        pass

    def get_review_logs_by_card_id(self,card_id:int)->list[ReviewLog]:
        rows=self.__conn.execute("SELECT * FROM review_log WHERE card_id=?", (card_id,)).fetchall()
        self.__conn.commit()
        return [self.__deserialize_review_log(row) for row in rows]
    
    def get_all_review_logs(self)->list[ReviewLog]:
        rows=self.__conn.execute("SELECT * FROM review_log").fetchall()
        self.__conn.commit()
        return [self.__deserialize_review_log(row) for row in rows]
    
    def count_review_logs(self)->int:
        row=self.__conn.execute("SELECT COUNT(*) FROM review_log").fetchone()
        self.__conn.commit()
        return row[0]