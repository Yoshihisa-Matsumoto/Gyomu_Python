from gyomu.holidays import MarketDateAccess
from datetime import date, timedelta
from enum import Enum
from dateutil.relativedelta import relativedelta
from gyomu.parameter_access import ParameterAccess
from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.gyomu_db_model import GyomuMarketHoliday


class VariableTranslator:
    class VariableType(Enum):
        Date = 1,
        ParamMaster = 2,
        ParamMasterStringDictionary = 3,
        Argument = 4,
        ArgumentFile = 5

    __market_access: MarketDateAccess

    def __init__(self, market_access: MarketDateAccess):
        self.__market_access = market_access

    def parse(self, input_string: str, target_date: date) -> str:
        start_index = input_string.find('{%')
        end_index = input_string.find('%}')
        if start_index != -1 and end_index != -1 and end_index > start_index:
            prefix = input_string[:start_index]
            keyword = input_string[start_index + 2:end_index]
            suffix = input_string[end_index + 2:]

            input_string = prefix + self.__translate(keyword, target_date) + suffix
            return self.parse(input_string, target_date)
        else:
            return input_string

    variable_date_parameter_type = ['TODAY', 'BBOM', 'NEXTBBOM', 'BOM', 'BEOM', 'NEXTBEOM', 'PREVBEOM', 'EOM',
                                    'NEXTBUS', 'NEXTDAY', 'PREVBUS', 'PREVDAY', 'EOY', 'BEOY', 'BBOY', 'BOY']

    def parse_date(self, keyword: str, target_date: date) -> date:
        parts = keyword.split('$')
        factor_index = 1
        translate_market_access: MarketDateAccess = self.__market_access
        supported_market = VariableTranslator.__get_supported_market()

        for p in parts:
            if p.isdecimal():
                factor_index = int(p)
                continue
            if p in supported_market:
                translate_market_access = MarketDateAccess(p)
                continue
            if p in self.variable_date_parameter_type:
                return self.__translate_date(translate_market_access=translate_market_access,
                                             target_date=target_date, date_parameter=p, factor_index=factor_index)

    def __translate_date(self, translate_market_access: MarketDateAccess, target_date: date, date_parameter: str,
                         factor_index: int) -> date:
        if date_parameter == 'TODAY':
            return target_date
        elif date_parameter == 'BBOM':
            # Business Day of Beginning of Month
            return translate_market_access.get_business_day_of_beginning_month(target_date, factor_index)
        elif date_parameter == 'NEXTBBOM':
            # Business Day of Beginning of Next Month
            return translate_market_access.get_business_day_of_beginning_of_next_month(target_date, factor_index)
        elif date_parameter == 'BOM':
            # Beginning of Month
            beginning_of_month = date(year=target_date.year, month=target_date.month, day=1)
            return beginning_of_month + timedelta(days=(factor_index - 1))
        elif date_parameter == 'BEOM':
            # Business Day of End Of Month
            return translate_market_access.get_business_day_of_beginning_of_next_month(target_date, -factor_index)
        elif date_parameter == 'NEXTBEOM':
            # Business Day of End of Next Month
            two_month_after = target_date + relativedelta(months=2)
            return translate_market_access.get_business_day_of_beginning_month(two_month_after, -factor_index)
        elif date_parameter == 'PREVBEOM':
            # Business Day of End of Previous Month
            bom = date(target_date.year, target_date.month, 1)
            return translate_market_access.get_business_day(bom, -factor_index)
        elif date_parameter == 'EOM':
            # End of Month
            next_month = target_date + relativedelta(months=1)
            return date(next_month.year, next_month.month, 1) - timedelta(days=factor_index)
        elif date_parameter == 'NEXTBUS':
            # Next Business Day
            return translate_market_access.get_business_day(target_date, factor_index)
        elif date_parameter == 'NEXTDAY':
            # Next Day
            return target_date + timedelta(days=factor_index)
        elif date_parameter == 'PREVBUS':
            # Previous Business Day
            return translate_market_access.get_business_day(target_date, -factor_index)
        elif date_parameter == 'PREVDAY':
            # Previous Day
            return target_date - timedelta(days=factor_index)

        elif date_parameter == 'EOY':
            # End of Year
            next_year = date(target_date.year + 1, 1, 1)
            return next_year - timedelta(days=factor_index)
        elif date_parameter == 'BEOY':
            # Business Day of End of Year
            next_year = date(target_date.year + 1, 1, 1)
            return translate_market_access.get_business_day(next_year, -factor_index)
        elif date_parameter == 'BBOY':
            # Business Day of Beginning of Year
            next_year = date(target_date.year, 1, 1)
            if translate_market_access.is_business_day(next_year):
                return translate_market_access.get_business_day(next_year, factor_index - 1)
            else:
                return translate_market_access.get_business_day(next_year, factor_index)
        elif date_parameter == 'BOY':
            next_year = date(target_date.year, 1, 1)
            return next_year + timedelta(days=factor_index - 1)

    @staticmethod
    def __get_supported_market() -> [str]:
        with DbConnectionFactory.get_gyomu_db_session() as session:
            return session.query(GyomuMarketHoliday).distinct(GyomuMarketHoliday.market).all()

    def __translate(self, keyword: str, target_date: date, arguments: list[str] = None) -> str:
        parts = keyword.split('$')
        factor_index = 1
        variable_type = VariableTranslator.VariableType.Date
        translate_market_access: MarketDateAccess = self.__market_access
        date_parameter: date
        str_list = []
        supported_market = VariableTranslator.__get_supported_market()

        for p in parts:
            if p.isdecimal():
                factor_index = int(p)
                continue
            if p in supported_market:
                translate_market_access = MarketDateAccess(p)
                continue
            if p in self.variable_date_parameter_type:
                date_parameter = self.__translate_date(translate_market_access=translate_market_access,
                                                       target_date=target_date, date_parameter=p,
                                                       factor_index=factor_index)

            elif p == 'PARAMMASTER':
                # Retrieve from DB Parameter
                variable_type == VariableTranslator.VariableType.ParamMaster
            elif p == 'PARAMDICTIONARY':
                # return dictionary value based on specified key. Dictionary comes from DB Parameter
                variable_type == VariableTranslator.VariableType.ParamMasterStringDictionary
            elif p == 'ARGUMENT':
                variable_type == VariableTranslator.VariableType.Argument
            elif p == 'ATTACHMENTFILE':
                variable_type == VariableTranslator.VariableType.ArgumentFile
            else:
                if variable_type == VariableTranslator.VariableType.Date:
                    translate_format = p
                    if translate_format == 'yyyyMMdd' or translate_format == 'yyyymmdd':
                        translate_format = '%Y%m%d'
                    str_list.append(date_parameter.strftime(translate_format))
                elif variable_type == VariableTranslator.VariableType.ParamMaster:
                    str_list.append(ParameterAccess.get_string_value(p))
                elif variable_type == VariableTranslator.VariableType.ParamMasterStringDictionary:
                    parameter_key = p.split(':')
                    dictionary: dict[str, str] = ParameterAccess.get_json_serialized_value(parameter_key[0],
                                                                                           dict[str, str])
                    str_list.append(dictionary[parameter_key[1]])
                elif variable_type == VariableTranslator.VariableType.Argument:
                    str_list.append(arguments[factor_index - 1])
                elif variable_type == VariableTranslator.VariableType.ArgumentFile:
                    pass

        return ''.join(str_list)
