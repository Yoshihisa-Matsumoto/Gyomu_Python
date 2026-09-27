from datetime import date

from gyomu_schema.market_holiday import MarketHoliday

from gyomu_infra.db.model.generated.models import GyomuMarketHoliday


def to_schema(model: GyomuMarketHoliday) -> MarketHoliday:
    """Converts a GyomuMarketHoliday database model to a MarketHoliday schema.

    Converts a database market holiday model to a schema object.

    Args:
        model (GyomuMarketHoliday): The database market holiday model to convert.

    Returns:
        MarketHoliday: The converted MarketHoliday schema object.
    """
    return MarketHoliday(
        id=model.id,
        market=model.market,
        holiday=date.fromisoformat(model.holiday),
    )


def to_model(schema: MarketHoliday) -> GyomuMarketHoliday:
    """Converts a MarketHoliday schema to a GyomuMarketHoliday database model.

    Converts a market holiday schema object to a database model.

    Args:
        schema (MarketHoliday): The market holiday schema object to convert.

    Returns:
        GyomuMarketHoliday: The converted GyomuMarketHoliday database model.
    """
    return GyomuMarketHoliday(
        id=schema.id,
        market=schema.market,
        year=schema.holiday.year,
        holiday=schema.holiday.isoformat(),
    )
