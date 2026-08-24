from datetime import date

from gyomu_infra.gyomu.date.business_calendar import BusinessCalendarImpl


class TestIsBusinessDay:
    def test_returns_true_for_weekday(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.is_business_day(date(2026, 8, 18))

    def test_returns_false_for_saturday(self):
        calendar = BusinessCalendarImpl([])

        assert not calendar.is_business_day(date(2026, 8, 22))

    def test_returns_false_for_sunday(self):
        calendar = BusinessCalendarImpl([])

        assert not calendar.is_business_day(date(2026, 8, 23))

    def test_returns_false_for_holiday(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 8, 18)],
        )

        assert not calendar.is_business_day(date(2026, 8, 18))


class TestBusinessDay:
    def test_returns_next_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day(
            date(2026, 8, 18),
            1,
        ) == date(2026, 8, 19)

    def test_skips_weekend(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day(
            date(2026, 8, 21),
            1,
        ) == date(2026, 8, 24)

    def test_returns_previous_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day(
            date(2026, 8, 18),
            -1,
        ) == date(2026, 8, 17)

    def test_skips_holiday(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 8, 19)],
        )

        assert calendar.business_day(
            date(2026, 8, 18),
            1,
        ) == date(2026, 8, 20)


class TestGetHolidays:
    def test_returns_holidays_in_range(self):
        calendar = BusinessCalendarImpl(
            [
                date(2026, 8, 10),
                date(2026, 8, 18),
                date(2026, 8, 25),
            ],
        )

        assert calendar.get_holidays(
            date(2026, 8, 11),
            date(2026, 8, 20),
        ) == [
            date(2026, 8, 18),
        ]

    def test_includes_start_and_end(self):
        calendar = BusinessCalendarImpl(
            [
                date(2026, 8, 10),
                date(2026, 8, 20),
            ],
        )

        assert calendar.get_holidays(
            date(2026, 8, 10),
            date(2026, 8, 20),
        ) == [
            date(2026, 8, 10),
            date(2026, 8, 20),
        ]


class TestBusinessDayOfBeginningMonthWithOffset:
    def test_returns_first_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_month_with_offset(
            date(2026, 8, 18),
        ) == date(2026, 8, 3)

    def test_returns_first_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_month_with_offset(
            date(2026, 7, 15),
        ) == date(2026, 7, 1)

    def test_returns_second_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_month_with_offset(
            date(2026, 7, 15),
            2,
        ) == date(2026, 7, 2)

    def test_skips_holiday(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 7, 1)],
        )

        assert calendar.business_day_of_beginning_month_with_offset(
            date(2026, 7, 15),
        ) == date(2026, 7, 2)

    def test_skips_holiday_for_second_day(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 7, 1)],
        )

        assert calendar.business_day_of_beginning_month_with_offset(
            date(2026, 7, 15),
            2,
        ) == date(2026, 7, 3)

    def test_zero_returns_first_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_month_with_offset(
            date(2026, 7, 15),
            0,
        ) == date(2026, 7, 1)

    def test_zero_skips_non_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_month_with_offset(
            date(2026, 8, 18),
            0,
        ) == date(2026, 8, 3)


class TestBusinessDayOfBeginningOfNextMonthWithOffset:
    def test_returns_first_business_day_when_next_month_start_is_weekend(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_next_month_with_offset(
            date(2026, 7, 15),
        ) == date(2026, 8, 3)

    def test_returns_first_day_when_next_month_start_is_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_next_month_with_offset(
            date(2026, 6, 15),
        ) == date(2026, 7, 1)

    def test_returns_first_business_day_when_next_month_start_is_holiday(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 8, 3)],
        )

        assert calendar.business_day_of_beginning_of_next_month_with_offset(
            date(2026, 7, 15),
        ) == date(2026, 8, 4)

    def test_returns_second_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_next_month_with_offset(
            date(2026, 7, 15),
            2,
        ) == date(2026, 8, 4)

    def test_returns_second_business_day_when_month_start_is_holiday(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 8, 3)],
        )

        assert calendar.business_day_of_beginning_of_next_month_with_offset(
            date(2026, 7, 15),
            2,
        ) == date(2026, 8, 5)

    def test_offset_zero_returns_first_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_next_month_with_offset(
            date(2026, 7, 15),
            0,
        ) == date(2026, 8, 3)

    def test_moves_to_january_when_target_date_is_in_december(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_next_month_with_offset(
            date(2026, 12, 15),
        ) == date(2027, 1, 1)

    def test_skips_holiday_when_moving_to_january(self):
        calendar = BusinessCalendarImpl(
            [date(2027, 1, 1)],
        )

        assert calendar.business_day_of_beginning_of_next_month_with_offset(
            date(2026, 12, 15),
        ) == date(2027, 1, 4)


class TestBusinessDayOfBeginningOfPreviousMonthWithOffset:
    def test_returns_first_day_when_previous_month_start_is_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_previous_month_with_offset(
            date(2026, 8, 15),
        ) == date(2026, 7, 1)

    def test_returns_first_business_day_when_previous_month_start_is_weekend(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_previous_month_with_offset(
            date(2026, 9, 15),
        ) == date(2026, 8, 3)

    def test_returns_first_business_day_when_previous_month_start_is_holiday(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 7, 1)],
        )

        assert calendar.business_day_of_beginning_of_previous_month_with_offset(
            date(2026, 8, 15),
        ) == date(2026, 7, 2)

    def test_returns_second_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_previous_month_with_offset(
            date(2026, 8, 15),
            2,
        ) == date(2026, 7, 2)

    def test_returns_second_business_day_when_month_start_is_holiday(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 7, 1)],
        )

        assert calendar.business_day_of_beginning_of_previous_month_with_offset(
            date(2026, 8, 15),
            2,
        ) == date(2026, 7, 3)

    def test_offset_zero_returns_first_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_previous_month_with_offset(
            date(2026, 8, 15),
            0,
        ) == date(2026, 7, 1)

    def test_moves_to_december_when_target_date_is_in_january(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_previous_month_with_offset(
            date(2027, 1, 15),
        ) == date(2026, 12, 1)

    def test_skips_holiday_when_moving_to_december(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 12, 1)],
        )

        assert calendar.business_day_of_beginning_of_previous_month_with_offset(
            date(2027, 1, 15),
        ) == date(2026, 12, 2)


class TestBusinessDayOfEndMonthWithOffset:
    def test_returns_last_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_month_with_offset(
            date(2026, 8, 15),
            1,
        ) == date(2026, 8, 31)

    def test_returns_previous_business_day_with_offset_two(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_month_with_offset(
            date(2026, 8, 15),
            2,
        ) == date(2026, 8, 28)

    def test_skips_holiday_at_end_of_month(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 8, 31)],
        )

        assert calendar.business_day_of_end_month_with_offset(
            date(2026, 8, 15),
            1,
        ) == date(2026, 8, 28)

    def test_skips_multiple_non_business_days(self):
        calendar = BusinessCalendarImpl(
            [
                date(2026, 8, 31),
                date(2026, 8, 28),
            ],
        )

        assert calendar.business_day_of_end_month_with_offset(
            date(2026, 8, 15),
            1,
        ) == date(2026, 8, 27)

    def test_offset_zero_is_treated_as_one(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_month_with_offset(
            date(2026, 8, 15),
            0,
        ) == date(2026, 8, 31)

    def test_handles_february_in_leap_year(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_month_with_offset(
            date(2028, 2, 15),
            1,
        ) == date(2028, 2, 29)

    def test_handles_february_in_non_leap_year(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_month_with_offset(
            date(2027, 2, 15),
            1,
        ) == date(2027, 2, 26)

    def test_handles_december(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_month_with_offset(
            date(2026, 12, 15),
            1,
        ) == date(2026, 12, 31)


class TestBusinessDayOfEndOfNextMonthWithOffset:
    def test_returns_last_business_day_of_next_month(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_next_month_with_offset(
            date(2026, 8, 15),
            1,
        ) == date(2026, 9, 30)

    def test_returns_previous_business_day_with_offset_two(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_next_month_with_offset(
            date(2026, 8, 15),
            2,
        ) == date(2026, 9, 29)

    def test_skips_holiday_at_end_of_next_month(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 9, 30)],
        )

        assert calendar.business_day_of_end_of_next_month_with_offset(
            date(2026, 8, 15),
            1,
        ) == date(2026, 9, 29)

    def test_offset_zero_is_treated_as_one(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_next_month_with_offset(
            date(2026, 8, 15),
            0,
        ) == date(2026, 9, 30)

    def test_handles_year_boundary(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_next_month_with_offset(
            date(2026, 11, 15),
            1,
        ) == date(2026, 12, 31)

    def test_handles_december(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_next_month_with_offset(
            date(2026, 12, 15),
            1,
        ) == date(2027, 1, 29)


class TestBusinessDayOfEndOfPreviousMonthWithOffset:
    def test_returns_last_business_day_of_previous_month(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_previous_month_with_offset(
            date(2026, 8, 15),
            1,
        ) == date(2026, 7, 31)

    def test_returns_previous_business_day_with_offset_two(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_previous_month_with_offset(
            date(2026, 8, 15),
            2,
        ) == date(2026, 7, 30)

    def test_skips_holiday_at_end_of_previous_month(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 7, 31)],
        )

        assert calendar.business_day_of_end_of_previous_month_with_offset(
            date(2026, 8, 15),
            1,
        ) == date(2026, 7, 30)

    def test_skips_multiple_non_business_days(self):
        calendar = BusinessCalendarImpl(
            [
                date(2026, 7, 31),
                date(2026, 7, 30),
            ],
        )

        assert calendar.business_day_of_end_of_previous_month_with_offset(
            date(2026, 8, 15),
            1,
        ) == date(2026, 7, 29)

    def test_offset_zero_is_treated_as_one(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_previous_month_with_offset(
            date(2026, 8, 15),
            0,
        ) == date(2026, 7, 31)

    def test_handles_january(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_previous_month_with_offset(
            date(2027, 1, 15),
            1,
        ) == date(2026, 12, 31)

    def test_handles_february_in_leap_year(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_previous_month_with_offset(
            date(2028, 3, 15),
            1,
        ) == date(2028, 2, 29)

    def test_handles_february_in_non_leap_year(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_previous_month_with_offset(
            date(2027, 3, 15),
            1,
        ) == date(2027, 2, 26)


class TestBusinessDayOfBeginningOfYear:
    def test_returns_first_business_day_when_january_first_is_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_year(
            date(2026, 6, 15),
            1,
        ) == date(2026, 1, 1)

    def test_returns_second_business_day_with_offset_two(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_year(
            date(2026, 6, 15),
            2,
        ) == date(2026, 1, 2)

    def test_skips_holidays_at_beginning_of_year(self):
        calendar = BusinessCalendarImpl(
            [
                date(2026, 1, 1),
                date(2026, 1, 2),
            ],
        )

        assert calendar.business_day_of_beginning_of_year(
            date(2026, 6, 15),
            1,
        ) == date(2026, 1, 5)

    def test_returns_first_business_day_when_offset_is_zero(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_beginning_of_year(
            date(2026, 6, 15),
            0,
        ) == date(2025, 12, 31)


class TestBusinessDayOfEndOfYear:
    def test_returns_last_business_day_of_year(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_year(
            date(2026, 6, 15),
            1,
        ) == date(2026, 12, 31)

    def test_returns_previous_business_day_with_offset_two(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_year(
            date(2026, 6, 15),
            2,
        ) == date(2026, 12, 30)

    def test_skips_holiday_at_end_of_year(self):
        calendar = BusinessCalendarImpl(
            [date(2026, 12, 31)],
        )

        assert calendar.business_day_of_end_of_year(
            date(2026, 6, 15),
            1,
        ) == date(2026, 12, 30)

    def test_offset_zero_returns_last_business_day(self):
        calendar = BusinessCalendarImpl([])

        assert calendar.business_day_of_end_of_year(
            date(2026, 6, 15),
            0,
        ) == date(2026, 12, 31)

    def test_skips_multiple_non_business_days(self):
        calendar = BusinessCalendarImpl(
            [
                date(2026, 12, 31),
                date(2026, 12, 30),
            ],
        )

        assert calendar.business_day_of_end_of_year(
            date(2026, 6, 15),
            1,
        ) == date(2026, 12, 29)
