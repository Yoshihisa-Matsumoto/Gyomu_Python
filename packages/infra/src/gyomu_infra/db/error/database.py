from gyomu_schema.error import DatabaseError
from sqlalchemy.exc import SQLAlchemyError


def to_database_error(error: SQLAlchemyError) -> DatabaseError:
    """Convert a SQLAlchemy error to a database error.

    Args:
        error (SQLAlchemyError): The SQLAlchemy error to convert.

    Returns:
        DatabaseError: The converted database error.
    """
    return DatabaseError(str(error))
