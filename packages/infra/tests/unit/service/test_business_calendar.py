from datetime import date

from gyomu_infra.service.business_calendar import BusinessCalendarImpl

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
