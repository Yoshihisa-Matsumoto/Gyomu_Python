from sqlalchemy.orm import Session

from gyomu_infra.db.repository.sqlalchemy_market_holiday import (
    SqlAlchemyMarketHolidayRepository,
)
from gyomu_infra.gyomu.date.business_calendar import BusinessCalendarService


def create_business_calendar_service(
    session: Session,
) -> BusinessCalendarService:
    repository = SqlAlchemyMarketHolidayRepository(session)
    return BusinessCalendarService(repository)
