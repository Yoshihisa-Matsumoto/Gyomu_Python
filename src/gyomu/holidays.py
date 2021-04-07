from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.gyomu_db_model import GyomuMarketHoliday
from datetime import date, datetime, timedelta
import threading
from dateutil.relativedelta import relativedelta

class MarketDateAccess:
    __market_holidays: dict[str, list[date]] = dict()
    __lock = threading.Lock()

    __market: str
    __holidays: list[date]

    def __init__(self, market):
        self.__market = market
        self.__init_data()

    @classmethod
    def __load_market_holidays(cls) -> dict[str, list[date]]:
        return cls.__market_holidays

    def __init_data(self):
        with MarketDateAccess.__lock:
            if self.__market in MarketDateAccess.__load_market_holidays():
                self.__holidays = MarketDateAccess.__load_market_holidays()[self.__market]
                return
            self.__holidays = list()
            with DbConnectionFactory.get_gyomu_db_session() as session:
                holiday_row: GyomuMarketHoliday
                for holiday_row in session.query(GyomuMarketHoliday).filter(
                        GyomuMarketHoliday.market == self.__market).all():
                    self.__holidays.append(datetime.strptime(holiday_row.holiday, '%Y%m%d').date())
            MarketDateAccess.__market_holidays[self.__market] = self.__holidays

    def get_business_day(self, target_date: date, day_offset: int) -> date:
        """

        :param target_date: target date as date
        :param day_offset: 1 ( 2 , ...) if 1st(2nd) business day from target_date,
        -1 (-2, ...) if 1st ( 2nd ) previous business day from target_date
        0 if nearest business day (pick next business day if target_date is not business day)
        :return:
        """
        if day_offset == 0:
            return self._get_next_business_day(self._get_previous_business_day(target_date, 1), 1)
        if day_offset > 0:
            return self._get_next_business_day(target_date, day_offset)
        else:
            return self._get_previous_business_day(target_date, -day_offset)

    def _get_next_business_day(self, target_date: date, day_offset: int) -> date:
        business_day: date = target_date
        while day_offset > 0:
            business_day = business_day + timedelta(days=1)
            if self.is_business_day(business_day):
                day_offset -= 1
        return business_day

    def _get_previous_business_day(self, target_date: date, day_offset: int) -> date:
        business_day: date = target_date
        while day_offset > 0:
            business_day = business_day - timedelta(days=1)
            if self.is_business_day(business_day):
                day_offset -= 1
        return business_day

    def __get_holiday(self):
        return self.__holidays

    def is_business_day(self, target_date: date):
        if target_date.isoweekday() > 5:
            return False
        return not target_date in self.__get_holiday()

    def get_business_day_of_beginning_month(self, target_date: date, day_offset: int=1) -> date:
        """

        :param target_date: target date as date
        :param day_offset: for example, 1(2) if 1st(2nd) business day of beginning of month,
        -1(-2) if 1st(2nd) business day of end of month
        :return: calculated business day as date
        """
        bbom = date(target_date.year,target_date.month,1)
        if self.is_business_day(bbom):
            if day_offset>1:
                return self.get_business_day(bbom, day_offset-1)
            elif day_offset==1 or day_offset ==0:
                return bbom
            else:
                return self.get_business_day(bbom,day_offset)
        else:
            if day_offset==0:
                day_offset=1
            return self.get_business_day(bbom, day_offset)

    def get_business_day_of_beginning_of_next_month(self, target_date: date, day_offset: int=1) -> date:
        next_month = target_date + relativedelta(months=1)
        return self.get_business_day_of_beginning_month(next_month,day_offset)