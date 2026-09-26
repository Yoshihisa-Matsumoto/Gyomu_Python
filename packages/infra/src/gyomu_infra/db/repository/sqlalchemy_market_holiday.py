from gyomu_schema.error.database import DatabaseError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Result, safe
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from gyomu_infra.db.error.database import to_database_error
from gyomu_infra.db.mapper.market_holiday import to_schema
from gyomu_infra.db.model.generated.models import GyomuMarketHoliday


class SqlAlchemyMarketHolidayRepository:
    """SQLAlchemy implementation of the market holiday repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], DatabaseError]:
        """Finds market holidays by market identifier.

        Args:
            market (str): Market identifier

        Returns:
            Result[list[MarketHoliday], DatabaseError]: Result containing a list of
                market holidays or a database error.
        """
        return self._find_by_market(market).alt(
            to_database_error,
        )

    @safe(exceptions=(SQLAlchemyError,))
    def _find_by_market(
        self,
        market: str,
    ) -> list[MarketHoliday]:
        """Internal method to find market holidays by market identifier.

        Args:
            market (str): Market identifier

        Returns:
            list[MarketHoliday]: List of market holidays.
        """
        statement = (
            select(GyomuMarketHoliday)
            .where(GyomuMarketHoliday.market == market)
            .order_by(GyomuMarketHoliday.holiday)
        )

        models = self._session.scalars(statement).all()

        return [to_schema(model) for model in models]

    def get_supported_market(self) -> Result[list[str], DatabaseError]:
        """Retrieves a list of supported markets.

        Returns:
            Result[list[str], DatabaseError]: Result containing a list of supported
                market identifiers or a database error.
        """
        return self._get_supported_market().alt(
            to_database_error,
        )

    @safe(exceptions=(SQLAlchemyError,))
    def _get_supported_market(
        self,
    ) -> list[str]:
        """Internal method to retrieve a list of supported markets.

        Returns:
            list[str]: List of supported market identifiers.
        """
        statement = select(GyomuMarketHoliday.market).distinct()

        return list(self._session.scalars(statement).all())
