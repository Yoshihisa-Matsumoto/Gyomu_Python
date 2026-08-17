
from datetime import date

from gyomu_infra.db.model.market_holiday import GyomuMarketHoliday
from gyomu_schema.market_holiday import MarketHoliday


def to_schema(model: GyomuMarketHoliday) -> MarketHoliday:
    return MarketHoliday(
        id=model.id,
        market=model.market,
        holiday=date.fromisoformat(model.holiday),
    )

def to_model(schema: MarketHoliday) -> GyomuMarketHoliday:
    return GyomuMarketHoliday(
        id=schema.id,
        market=schema.market,
        year=schema.holiday.year,
        holiday=schema.holiday.isoformat(),
    )
