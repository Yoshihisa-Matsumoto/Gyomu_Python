from returns.result import Result, safe
from sqlalchemy.exc import SQLAlchemyError

from gyomu_schema.error import DatabaseError
from gyomu_infra.error.database import to_database_error


@safe(exceptions=(SQLAlchemyError,))
def database_operation() -> str:
    raise SQLAlchemyError("database connection failed")


def find_data() -> Result[str, DatabaseError]:
    return database_operation().alt(to_database_error)
