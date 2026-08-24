from unittest.mock import Mock

from sqlalchemy.orm import Session

from gyomu_infra.db.repository.sqlalchemy_market_holiday import (
    SqlAlchemyMarketHolidayRepository,
)
from gyomu_infra.gyomu.date.business_calendar import BusinessCalendarService
from gyomu_infra.gyomu.date.business_calendar_factory import (
    create_business_calendar_service,
)


class TestCreateBusinessCalendarService:
    def test_creates_business_calendar_service(self) -> None:
        session = Mock(spec=Session)

        service = create_business_calendar_service(session)

        assert isinstance(service, BusinessCalendarService)
        assert isinstance(
            service._repository,
            SqlAlchemyMarketHolidayRepository,
        )
