from datetime import date, timedelta

from gyomu_schema.error import GyomuIOError
from gyomu_schema.gyomu.holiday.business_calendar import BusinessCalendar
from gyomu_schema.market_holiday import MarketHoliday
from returns.result import Result, Success

from gyomu_infra.db.repository.market_holiday import MarketHolidayRepository


class BusinessCalendarImpl:
    def __init__(self, holidays: list[date]) -> None:
        self._holidays = holidays
        self._holiday_set = set(holidays)

    def is_business_day(self, target_date: date) -> bool:
        if target_date.isoweekday() > 5:
            return False

        return target_date not in self._holiday_set

    def business_day(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
        if day_offset == 0:
            return self._get_next_business_day(
                self._get_previous_business_day(target_date, 1),
                1,
            )

        if day_offset > 0:
            return self._get_next_business_day(
                target_date,
                day_offset,
            )

        return self._get_previous_business_day(
            target_date,
            -day_offset,
        )

    def get_holidays(
        self,
        start_date: date,
        end_date: date,
    ) -> list[date]:
        return [
            holiday
            for holiday in self._holidays
            if start_date <= holiday <= end_date
        ]

    def _get_next_business_day(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
        business_day = target_date

        while day_offset > 0:
            business_day += timedelta(days=1)

            if self.is_business_day(business_day):
                day_offset -= 1

        return business_day

    def _get_previous_business_day(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
      business_day = target_date

      while day_offset > 0:
          business_day -= timedelta(days=1)

          if self.is_business_day(business_day):
              day_offset -= 1

      return business_day

    def business_day_of_beginning_month_with_offset(
        self,
        target_date: date,
        day_offset: int = 1,
    ) -> date:
      business_day = target_date.replace(day=1)

      if self.is_business_day(business_day):
          if day_offset > 1:
              return self.business_day(
                  business_day,
                  day_offset - 1,
              )

          return business_day

      return self.business_day(
          business_day,
          day_offset,
      )


    def business_day_of_beginning_of_next_month_with_offset(
        self,
        target_date: date,
        day_offset: int = 1,
    ) -> date:
      if target_date.month == 12:
          business_day = date(
              target_date.year + 1,
              1,
              1,
          )
      else:
          business_day = date(
              target_date.year,
              target_date.month + 1,
              1,
          )

      if day_offset == 0:
          day_offset = 1

      if self.is_business_day(business_day):
          if day_offset > 1:
              return self.business_day(
                  business_day,
                  day_offset - 1,
              )

          return business_day

      return self.business_day(
          business_day,
          day_offset,
      )

class BusinessCalendarService:
    def __init__(
        self,
        repository: MarketHolidayRepository,
    ) -> None:
        self._repository = repository
        self._cache: dict[str, BusinessCalendar] = {}

    def get(
        self,
        market: str,
    ) -> Result[BusinessCalendar, GyomuIOError]:
        cached = self._cache.get(market)

        if cached is not None:
            return Success(cached)

        return self._repository.find_by_market(market).map(
            lambda holidays: self._create_calendar(market, holidays),
        )

    def _create_calendar(
        self,
        market: str,
        holidays: list[MarketHoliday],
    ) -> BusinessCalendar:
        calendar = BusinessCalendarImpl(
            [holiday.holiday for holiday in holidays],
        )

        self._cache[market] = calendar

        return calendar

