from contextlib import contextmanager
from sqlalchemy.orm import Session

class SqlAlchemyTransactionManager:
    def __init__(self, session: Session):
        self._connection=session
        self._depth=0
    
    # contextmanager is a decorator that makes the transaction method a context manager
    # context manager is a way to manage the transaction
    @contextmanager
    def transaction(self):
        # if the commit count is greater than 0, then we are already in a transaction
        # so we just need to increment the commit count and yield to the caller
        if self._depth>0:
            self._depth+=1
            try:
                yield
            except Exception as e:
                self._connection.rollback()
                raise e
            finally:
                self._depth-=1
            return
        self._depth=1
        try:
            # stop, yield to the caller
            yield
            # start a transaction
            self._connection.commit()
        except Exception as e:
            # if an error occurs, rollback the transaction
            self._connection.rollback()
            raise e
        finally:
            # if the transaction is successful, commit the transaction
            self._depth=0