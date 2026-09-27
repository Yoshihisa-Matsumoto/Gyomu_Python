from sqlalchemy.orm import Session

from gyomu_infra.db.repository.sqlalchemy_market_holiday import (
    SqlAlchemyMarketHolidayRepository,
)
from gyomu_infra.gyomu.date.business_calendar import BusinessCalendarService


def create_business_calendar_service(
    session: Session,
) -> BusinessCalendarService:
    """Create a business calendar service.

    Creates and returns a business calendar service instance using a SQLAlchemy market
    holiday repository.

    Args:
        session (Session): Database session to use for repository initialization

    Returns:
        BusinessCalendarService: Initialized business calendar service
    """
    repository = SqlAlchemyMarketHolidayRepository(session)
    return BusinessCalendarService(repository)
