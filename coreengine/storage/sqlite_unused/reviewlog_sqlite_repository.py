import sqlite3
import json
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
            'note_id':review_log.note_id,
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
            note_id=row['note_id'],
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
    
    def __format_note_content(self, fields_json: str) -> str:
        try:
            fields = json.loads(fields_json)
        except (TypeError, json.JSONDecodeError):
            return ""

        if not isinstance(fields, list):
            return str(fields)

        cleaned_fields = [
            str(field).strip()
            for field in fields
            if str(field).strip()
        ]

        return " / ".join(cleaned_fields)

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
            note_id,
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id,
            data['card_id'], 
            data['deck_id'],
            data['note_id'],
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
        cursor=self.__conn.execute("""
        UPDATE review_log SET user_id=?,
        card_id=?,
        deck_id=?,
        note_id=?,
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
        WHERE review_log_id=? AND user_id=?""", 
        (user_id,
        data['card_id'], 
        data['deck_id'],
        data['note_id'],
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
        review_log.review_log_id,
        user_id
        ))
        if cursor.rowcount==0:
            raise ValueError("Review log not found")
        return self.get_log(user_id, review_log.review_log_id)
    
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
        rows=self.__conn.execute("SELECT * FROM review_log WHERE card_id=? AND user_id=?", (card_id,user_id)).fetchall()
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
    
    def get_reviewed_deck_summaries(self, user_id: int) -> list[dict]:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        rows = self.__conn.execute(
            """
            SELECT
                d.deck_id AS deck_id,
                d.deck_name AS deck_name,
                d.deck_description AS deck_description,
                COUNT(r.review_log_id) AS review_count,
                MAX(r.review_time) AS latest_review_time
            FROM review_log AS r
            JOIN deck AS d
                ON r.deck_id = d.deck_id
                AND r.user_id = d.user_id
            WHERE r.user_id = ?
                AND r.deck_id IS NOT NULL
            GROUP BY
                d.deck_id,
                d.deck_name,
                d.deck_description
            ORDER BY latest_review_time DESC
            """,
            (user_id,),
        ).fetchall()

        return [dict(row) for row in rows]
    
    def get_latest_note_reviews(self, user_id: int, note_id: int) -> dict | None:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(note_id, int) or note_id <= 0:
            raise ValueError("Note ID must be a positive integer")

        row = self.__conn.execute(
            """
            SELECT
                r.note_id AS note_id,
                n.fields_JSON AS fields_JSON,
                r.new_status AS progress,
                r.review_time AS review_time
            FROM review_log AS r
            JOIN note AS n
                ON r.note_id = n.note_id
                AND r.user_id = n.user_id
            WHERE r.user_id = ?
                AND r.note_id = ?
                AND r.note_id IS NOT NULL
            ORDER BY
                r.review_time DESC,
                r.review_log_id DESC
            LIMIT 1
            """,
            (user_id, note_id),
        ).fetchone()

        if row is None:
            return None

        return {
            "note_id": row["note_id"],
            "content": self.__format_note_content(row["fields_JSON"]),
            "progress": row["progress"],
            "review_time": row["review_time"],
        }
    
    def get_latest_note_reviews_by_deck_id(
        self,
        user_id: int,
        deck_id: int,
    ) -> list[dict]:
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError("User ID must be a positive integer")

        if not isinstance(deck_id, int) or deck_id <= 0:
            raise ValueError("Deck ID must be a positive integer")

        rows = self.__conn.execute(
            """
            WITH ranked_note_reviews AS (
                SELECT
                    r.review_log_id,
                    r.note_id,
                    r.new_status AS progress,
                    r.review_time,
                    ROW_NUMBER() OVER (
                        PARTITION BY r.note_id
                        ORDER BY r.review_time DESC, r.review_log_id DESC
                    ) AS rn
                FROM review_log AS r
                WHERE r.user_id = ?
                    AND r.deck_id = ?
                    AND r.note_id IS NOT NULL
            )
            SELECT
                ranked.note_id AS note_id,
                n.fields_JSON AS fields_JSON,
                ranked.progress AS progress,
                ranked.review_time AS review_time
            FROM ranked_note_reviews AS ranked
            JOIN note AS n
                ON ranked.note_id = n.note_id
                AND n.user_id = ?
            WHERE ranked.rn = 1
            ORDER BY ranked.review_time DESC, ranked.review_log_id DESC
            """,
            (user_id, deck_id, user_id),
        ).fetchall()

        return [
            {
                "note_id": row["note_id"],
                "content": self.__format_note_content(row["fields_JSON"]),
                "progress": row["progress"],
                "review_time": row["review_time"],
            }
            for row in rows
        ]