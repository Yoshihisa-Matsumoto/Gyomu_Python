from sqlalchemy.exc import SQLAlchemyError

from gyomu_schema.error import DatabaseError


def to_database_error(error: SQLAlchemyError) -> DatabaseError:
    return DatabaseError(str(error))
