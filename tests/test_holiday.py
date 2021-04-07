from datetime import date
import pytest
from gyomu.holidays import MarketDateAccess
from collections import namedtuple

DateResult = namedtuple('DateResult', ['input_date', 'input_offset', 'expected_date'])





class TestMarketDate:
    @pytest.mark.parametrize('input_data',
                             {
                                 DateResult(input_date=date(1984, 5, 1), input_offset=-1,
                                            expected_date=date(1984, 4, 27)),
                                 DateResult(input_date=date(1984, 5, 7), input_offset=-1,
                                            expected_date=date(1984, 5, 4)),
                                 DateResult(input_date=date(1984, 5, 7), input_offset=-2,
                                            expected_date=date(1984, 5, 2)),
                                 DateResult(input_date=date(1984, 4, 27), input_offset=1,
                                            expected_date=date(1984, 5, 1)),
                                 DateResult(input_date=date(1984, 5, 4), input_offset=1,
                                            expected_date=date(1984, 5, 7)),
                                 DateResult(input_date=date(1984, 5, 2), input_offset=2,
                                            expected_date=date(1984, 5, 7)),
                                 DateResult(input_date=date(1984, 5, 7), input_offset=0,
                                            expected_date=date(1984, 5, 7)),
                                 DateResult(input_date=date(1984, 4, 28), input_offset=0,
                                            expected_date=date(1984, 5, 1)),
                             })
    def test_get_business_day(self, mock_holiday, input_data):

        market_access = MarketDateAccess("JP")

        assert input_data.expected_date == market_access.get_business_day(input_data.input_date,
                                                                          input_data.input_offset)
        # assert date(1984, 4, 27) == marketAccess.get_business_day(date(1984, 5, 1), -1)

    def test_get_month_day(self, mock_holiday):

        market_access = MarketDateAccess("JP")
        assert market_access.get_business_day_of_beginning_month(date(1984, 5, 2), 2) == date(1984, 5, 2)

        assert market_access.get_business_day_of_beginning_of_next_month(date(1984, 5, 2), -2) == date(1984, 5, 30)

        assert market_access.get_business_day_of_beginning_of_next_month(date(1984, 5, 2), 2) == date(1984, 6, 4)
        assert market_access.get_business_day_of_beginning_of_next_month(date(1984, 5, 1), 2) == date(1984, 6, 4)
        assert market_access.get_business_day_of_beginning_of_next_month(date(1984, 5, 31), 2) == date(1984, 6, 4)