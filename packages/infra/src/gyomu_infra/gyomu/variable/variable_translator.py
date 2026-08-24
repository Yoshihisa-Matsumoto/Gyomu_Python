from calendar import monthrange
from datetime import date, timedelta
from enum import Enum
from typing import Literal, TypeGuard, assert_never

from dateutil.relativedelta import relativedelta
from gyomu_schema.error.io import GyomuIOError
from gyomu_schema.error.validation import ValidationError
from gyomu_schema.gyomu.holiday.business_calendar import BusinessCalendar
from returns.result import Failure, Result, Success

from gyomu_infra.db.repository.market_holiday import MarketHolidayRepository
from gyomu_infra.db.repository.parameter_master import ParameterMasterRepository
from gyomu_infra.gyomu.date.business_calendar import BusinessCalendarService
from gyomu_infra.gyomu.parameter.parameter_access import ParameterAccessImpl

VariableDateParameter = Literal[
    "TODAY",
    "BBOM",
    "NEXTBBOM",
    "BOM",
    "BEOM",
    "NEXTBEOM",
    "PREVBEOM",
    "EOM",
    "NEXTBUS",
    "NEXTDAY",
    "PREVBUS",
    "PREVDAY",
    "EOY",
    "BEOY",
    "BBOY",
    "BOY",
]
VARIABLE_DATE_PARAMETERS: tuple[VariableDateParameter, ...] = (
    "TODAY",
    "BBOM",
    "NEXTBBOM",
    "BOM",
    "BEOM",
    "NEXTBEOM",
    "PREVBEOM",
    "EOM",
    "NEXTBUS",
    "NEXTDAY",
    "PREVBUS",
    "PREVDAY",
    "EOY",
    "BEOY",
    "BBOY",
    "BOY",
)


def _is_variable_date_parameter(
    value: str,
) -> TypeGuard[VariableDateParameter]:
    return value in VARIABLE_DATE_PARAMETERS


class VariableType(Enum):
    Date = (1,)
    ParamMaster = (2,)
    ParamMasterStringDictionary = (3,)
    Argument = (4,)
    ArgumentFile = 5


class VariableTranslatorImpl:
    def __init__(
        self,
        market_holiday: MarketHolidayRepository,
        parameter_master: ParameterMasterRepository,
    ) -> None:
        self.market_holiday = market_holiday
        self.business_calendar_service = BusinessCalendarService(self.market_holiday)
        self.parameter_master = ParameterAccessImpl(parameter_master)
        # self.variable_date_parameter_type = [
        #     "TODAY",
        #     "BBOM",
        #     "NEXTBBOM",
        #     "BOM",
        #     "BEOM",
        #     "NEXTBEOM",
        #     "PREVBEOM",
        #     "EOM",
        #     "NEXTBUS",
        #     "NEXTDAY",
        #     "PREVBUS",
        #     "PREVDAY",
        #     "EOY",
        #     "BEOY",
        #     "BBOY",
        #     "BOY",
        # ]

    def parse_date(
        self, keyword: str, target_date: date
    ) -> Result[date, GyomuIOError | ValidationError]:
        parts = keyword.split("$")
        factor_index = 1

        support_market_result = self.market_holiday.get_supported_market()
        if isinstance(support_market_result, Failure):
            return support_market_result
        supported_market = support_market_result.unwrap()

        business_calendar_result = self.business_calendar_service.get(
            supported_market[0]
        )
        if isinstance(business_calendar_result, Failure):
            return business_calendar_result
        business_calendar = business_calendar_result.unwrap()

        for p in parts:
            if p.isdecimal():
                factor_index = int(p)
                continue
            if p in supported_market:
                business_calendar_result = self.business_calendar_service.get(p)
                if isinstance(business_calendar_result, Failure):
                    return business_calendar_result
                business_calendar = business_calendar_result.unwrap()
                continue
            if _is_variable_date_parameter(p):
                return Success(
                    self.__translate_date(
                        business_calendar=business_calendar,
                        target_date=target_date,
                        date_parameter=p,
                        factor_index=factor_index,
                    )
                )

        return Failure(ValidationError(message=f"Invalid Parameter:{keyword}"))

    def __translate_date(
        self,
        business_calendar: BusinessCalendar,
        target_date: date,
        date_parameter: VariableDateParameter,
        factor_index: int,
    ) -> date:
        match date_parameter:
            case "TODAY":
                return target_date
            case "BBOM":
                # Business Day of Beginning of Month
                return business_calendar.business_day_of_beginning_month_with_offset(
                    target_date, factor_index
                )
            case "NEXTBBOM":
                # Business Day of Beginning of Next Month
                return business_calendar.business_day_of_beginning_of_next_month_with_offset(
                    target_date, factor_index
                )
            case "BOM":
                # Beginning of Month
                beginning_of_month = date(
                    year=target_date.year, month=target_date.month, day=1
                )
                return beginning_of_month + timedelta(days=(factor_index - 1))
            case "BEOM":
                # Business Day of End Of Month
                return business_calendar.business_day_of_beginning_of_next_month_with_offset(
                    target_date, -factor_index
                )
            case "NEXTBEOM":
                # Business Day of End of Next Month
                two_month_after = target_date + relativedelta(months=2)
                return business_calendar.business_day_of_beginning_month_with_offset(
                    two_month_after, -factor_index
                )
            case "PREVBEOM":
                # Business Day of End of Previous Month
                bom = date(target_date.year, target_date.month, 1)
                return business_calendar.business_day(bom, -factor_index)
            case "EOM":
                # End of Month
                last_day = monthrange(target_date.year, target_date.month)[1]
                return date(
                    target_date.year, target_date.month, last_day - factor_index + 1
                )
            case "NEXTBUS":
                # Next Business Day
                return business_calendar.business_day(target_date, factor_index)
            case "NEXTDAY":
                # Next Day
                return target_date + timedelta(days=factor_index)
            case "PREVBUS":
                # Previous Business Day
                return business_calendar.business_day(target_date, -factor_index)
            case "PREVDAY":
                # Previous Day
                return target_date - timedelta(days=factor_index)

            case "EOY":
                # End of Year
                next_year = date(target_date.year + 1, 1, 1)
                return next_year - timedelta(days=factor_index)
            case "BEOY":
                # Business Day of End of Year
                next_year = date(target_date.year + 1, 1, 1)
                return business_calendar.business_day(next_year, -factor_index)
            case "BBOY":
                # Business Day of Beginning of Year
                next_year = date(target_date.year, 1, 1)
                if business_calendar.is_business_day(next_year):
                    return business_calendar.business_day(next_year, factor_index - 1)
                else:
                    return business_calendar.business_day(next_year, factor_index)
            case "BOY":
                next_year = date(target_date.year, 1, 1)
                return next_year + timedelta(days=factor_index - 1)
        return assert_never(date_parameter)

    def parse(
        self, input_string: str, target_date: date
    ) -> Result[str, GyomuIOError | ValidationError]:

        support_market_result = self.market_holiday.get_supported_market()
        if isinstance(support_market_result, Failure):
            return support_market_result
        supported_market = support_market_result.unwrap()

        start_index = input_string.find("{%")
        end_index = input_string.find("%}")
        if start_index != -1 and end_index != -1 and end_index > start_index:
            prefix = input_string[:start_index]
            keyword = input_string[start_index + 2 : end_index]
            suffix = input_string[end_index + 2 :]

            translate_result = self.__translate(supported_market, keyword, target_date)
            if isinstance(translate_result, Failure):
                return translate_result

            input_string = prefix + translate_result.unwrap() + suffix
            return self.parse(input_string, target_date)
        else:
            return Success(input_string)

    def __translate(
        self,
        supported_market: list[str],
        keyword: str,
        target_date: date,
        arguments: list[str] | None = None,
    ) -> Result[str, GyomuIOError | ValidationError]:
        parts = keyword.split("$")
        factor_index = 1
        variable_type = VariableType.Date
        business_calendar_result = self.business_calendar_service.get(
            supported_market[0]
        )
        if isinstance(business_calendar_result, Failure):
            return business_calendar_result
        business_calendar = business_calendar_result.unwrap()

        date_parameter: date | None = None
        str_list: list[str] = []

        for p in parts:
            if p.isdecimal():
                factor_index = int(p)
                continue
            if p in supported_market:
                business_calendar_result = self.business_calendar_service.get(p)
                if isinstance(business_calendar_result, Failure):
                    return business_calendar_result
                business_calendar = business_calendar_result.unwrap()
                continue
            if _is_variable_date_parameter(p):
                date_parameter = self.__translate_date(
                    business_calendar=business_calendar,
                    target_date=target_date,
                    date_parameter=p,
                    factor_index=factor_index,
                )

            elif p == "PARAMMASTER":
                # Retrieve from DB Parameter
                variable_type = VariableType.ParamMaster
            elif p == "PARAMDICTIONARY":
                # return dictionary value based on specified key. Dictionary comes from DB Parameter
                variable_type = VariableType.ParamMasterStringDictionary
            elif p == "ARGUMENT":
                variable_type = VariableType.Argument
            elif p == "ATTACHMENTFILE":
                variable_type = VariableType.ArgumentFile
            else:
                if variable_type == VariableType.Date:
                    translate_format = p
                    if translate_format == "yyyyMMdd" or translate_format == "yyyymmdd":
                        translate_format = "%Y%m%d"
                    if date_parameter is None:
                        return Failure(ValidationError(f"Invalid Parameter: {keyword}"))
                    str_list.append(date_parameter.strftime(translate_format))
                elif variable_type == VariableType.ParamMaster:
                    parameter_result = self.parameter_master.get_value(p)
                    if isinstance(parameter_result, Failure):
                        return parameter_result
                    str_list.append(parameter_result.unwrap())
                elif variable_type == VariableType.ParamMasterStringDictionary:
                    # parameter_key = p.split(":")
                    # dictionary: dict[str, str] = (
                    #     ParameterAccess.get_json_serialized_value(
                    #         parameter_key[0], dict[str, str]
                    #     )
                    # )
                    # str_list.append(dictionary[parameter_key[1]])
                    pass
                elif variable_type == VariableType.Argument:
                    if arguments is None or len(arguments) < factor_index:
                        return Failure(
                            ValidationError(f"Invalid Argument: {arguments}")
                        )
                    str_list.append(arguments[factor_index - 1])
                elif variable_type == VariableType.ArgumentFile:
                    pass

        return Success("".join(str_list))
