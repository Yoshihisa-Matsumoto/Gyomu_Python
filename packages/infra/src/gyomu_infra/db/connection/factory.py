from gyomu_schema.config.config_loader_option import EnvironmentLoaderOption
from gyomu_schema.db.config import DbConfig
from gyomu_schema.error import ConfigError
from returns.result import Failure
from sqlalchemy import Engine, create_engine
from sqlalchemy.exc import SQLAlchemyError

from gyomu_infra.config.loader import ConfigLoader

GYOMU_COMMON_MAINDB_CONNECTION = "GYOMU_COMMON_MAINDB_CONNECTION"


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
    def create_engine(cls, option: EnvironmentLoaderOption) -> Engine:
        """Create a SQLAlchemy Engine from the database configuration.

        Returns:
            A configured SQLAlchemy Engine.

        Raises:
            ConfigError: If the database connection configuration is missing
                or invalid.
        """
        config = ConfigLoader.load(DbConfig, option)
        if isinstance(config, Failure):
            raise config.failure()

        try:
            return create_engine(config.unwrap().connection_string)
        except SQLAlchemyError as error:
            raise ConfigError(
                "Database connection configuration is invalid",
                schema=DbConfig,
                context="DbConnectionFactory.create_engine",
                source="env",
                phase="validate",
            ).chain(error)
