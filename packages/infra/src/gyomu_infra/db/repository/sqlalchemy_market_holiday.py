from gyomu_schema.error import GyomuIOError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Result, safe
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from gyomu_infra.db.error.database import to_database_error
from gyomu_infra.db.mapper.market_holiday import to_schema
from gyomu_infra.db.model.market_holiday import GyomuMarketHoliday


class SqlAlchemyMarketHolidayRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], GyomuIOError]:
        return self._find_by_market(market).alt(
            to_database_error,
        )

    @safe(exceptions=(SQLAlchemyError,))
    def _find_by_market(
        self,
        market: str,
    ) -> list[MarketHoliday]:
        statement = (
            select(GyomuMarketHoliday)
            .where(GyomuMarketHoliday.market == market)
            .order_by(GyomuMarketHoliday.holiday)
        )

        models = self._session.scalars(statement).all()

        return [to_schema(model) for model in models]
 