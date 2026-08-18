from datetime import date
from typing import Protocol


class BusinessCalendar(Protocol):
    def is_business_day(
        self,
        target_date: date,
    ) -> bool:
        ...

    def business_day(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
        ...

    def get_holidays(
        self,
        start_date: date,
        end_date: date,
    ) -> list[date]: 
        ...

    def business_day_of_beginning_month_with_offset(
        self,
        target_date: date,
        day_offset: int = 1,
    ) -> date:
        ...

    def business_day_of_beginning_of_next_month_with_offset(
        self,
        target_date: date,
        day_offset: int = 1,
    ) -> date:
        ...

    def business_day_of_beginning_of_previous_month_with_offset(
        self,
        target_date: date,
        day_offset: int = 1,
    ) -> date:
        ...
    def business_day_of_end_month_with_offset(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
        ...

    def business_day_of_end_of_next_month_with_offset(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
        ...

    def business_day_of_end_of_previous_month_with_offset(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
        ...

    def business_day_of_beginning_of_year(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
        ...


    def business_day_of_end_of_year(
        self,
        target_date: date,
        day_offset: int,
    ) -> date:
        ...
