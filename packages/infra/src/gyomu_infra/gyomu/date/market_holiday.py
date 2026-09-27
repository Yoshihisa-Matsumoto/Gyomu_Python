from gyomu_schema.error.database import DatabaseError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Result

from gyomu_infra.db.repository.market_holiday import MarketHolidayRepository


class MarketHolidayService:
    """Provides service operations for querying market holidays and supported
    markets.
    """

    def __init__(
        self,
        repository: MarketHolidayRepository,
    ) -> None:
        self._repository = repository

    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], DatabaseError]:
        """Finds market holidays for a given market.

        Args:
            market (str): The market identifier

        Returns:
            Result[list[MarketHoliday], DatabaseError]: Result containing a list of
                market holidays or a database error
        """
        return self._repository.find_by_market(market)

    def get_supported_market(self) -> Result[list[str], DatabaseError]:
        """Retrieves the list of supported markets.

        Returns:
            Result[list[str], DatabaseError]: Result containing a list of supported
                market identifiers or a database error
        """
        return self._repository.get_supported_market()
