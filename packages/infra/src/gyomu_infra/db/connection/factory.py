import os

from gyomu_schema.error import ConfigError
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError

GYOMU_COMMON_MAINDB_CONNECTION = "GYOMU_COMMON_MAINDB_CONNECTION"


def get_main_db_connection_string() -> str:
    connection_string = os.getenv(GYOMU_COMMON_MAINDB_CONNECTION)

    if connection_string is None:
        raise ConfigError(
            "Database connection string is not configured",
            context="DbConnectionFactory.create_engine",
            details={
                "environment_variable": GYOMU_COMMON_MAINDB_CONNECTION,
            },
        )

    return connection_string


class DbConnectionFactory:
    """Factory for creating SQLAlchemy database engines.

    Gyomu Context:
        The factory resolves the database connection configuration from
        environment variables and creates a SQLAlchemy Engine.

        Session lifecycle and transaction management are intentionally
        outside this factory. Sessions are created by the Composition Root
        or the component responsible for a database operation.
    """

    @classmethod
    def create_engine(cls) -> Engine:
        """Create a SQLAlchemy Engine from the database configuration.

        Returns:
            A configured SQLAlchemy Engine.

        Raises:
            ConfigError: If the database connection configuration is missing
                or invalid.
        """
        connection_string = get_main_db_connection_string()

        try:
            return create_engine(connection_string)
        except SQLAlchemyError as error:
            raise ConfigError(
                "Database connection configuration is invalid",
                context="DbConnectionFactory.create_engine",
            ) from error
