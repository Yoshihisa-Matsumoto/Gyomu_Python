from gyomu_schema.error import DatabaseError
from sqlalchemy.exc import SQLAlchemyError


def to_database_error(error: SQLAlchemyError) -> DatabaseError:
    return DatabaseError(str(error))
