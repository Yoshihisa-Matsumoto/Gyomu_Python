from sqlalchemy import select
from sqlalchemy.orm import Session

from gyomu_infra.db.model.market_holiday import GyomuMarketHoliday
from gyomu_infra.mapper.market_holiday import to_schema
from gyomu_schema.market_holiday import MarketHoliday

from returns.result import Result, safe
from sqlalchemy.exc import SQLAlchemyError

from gyomu_schema.error import DatabaseError
from gyomu_schema.market_holiday import MarketHoliday

@safe(exceptions=(SQLAlchemyError,))
class SqlAlchemyMarketHolidayRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_market(
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
