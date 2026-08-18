from datetime import date
from uuid import uuid4

from gyomu_infra.db.repository.market_holiday import MarketHolidayRepository
from gyomu_infra.gyomu.date.business_calendar import (
    BusinessCalendarService,
)
from gyomu_schema.error import GyomuIOError
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Failure, Result, Success


class DummyMarketHolidayRepository:
    def __init__(
        self,
        result: Result[list[MarketHoliday], GyomuIOError],
    ) -> None:
        self._result = result
        self.call_count = 0

    def find_by_market(
        self,
        market: str,
    ) -> Result[list[MarketHoliday], GyomuIOError]:
        self.call_count += 1
        return self._result


class TestBusinessCalendarService:
  def test_get_returns_business_calendar(self):
      holiday = MarketHoliday(
          id=uuid4(),
          market="JPX",
          holiday=date(2026, 8, 18),
      )

      repository = DummyMarketHolidayRepository(
          Success([holiday]),
      )

      service = BusinessCalendarService(repository)

      result = service.get("JPX")

      assert isinstance(result, Success)

      calendar = result.unwrap()

      assert not calendar.is_business_day(
          date(2026, 8, 18),
      )


  def test_get_propagates_repository_failure(self):
      error = GyomuIOError('invalid io')

      repository = DummyMarketHolidayRepository(
          Failure(error),
      )

      service = BusinessCalendarService(repository)

      result = service.get("JPX")

      assert isinstance(result, Failure)
      assert result.failure() is error


  def test_get_uses_cache(self):
      repository = DummyMarketHolidayRepository(
          Success([]),
      )

      service = BusinessCalendarService(repository)

      first = service.get("JPX")
      second = service.get("JPX")

      assert isinstance(first, Success)
      assert isinstance(second, Success)

      assert first.unwrap() is second.unwrap()
      assert repository.call_count == 1
