from datetime import date
from uuid import UUID

from gyomu_infra.db.model.market_holiday import GyomuMarketHoliday
from gyomu_infra.mapper.market_holiday import to_model, to_schema
from gyomu_schema.market_holiday import MarketHoliday




def test_to_schema() -> None:
    id = UUID("019dbc9c-221b-7aa9-b2b7-3cacf8bcb8d6")

    model = GyomuMarketHoliday(
        id=id,
        market="JP",
        year=2026,
        holiday="2026-01-01",
    )

    result = to_schema(model)

    assert result == MarketHoliday(
        id=id,
        market="JP",
        holiday=date(2026, 1, 1),
    )


def test_to_model() -> None:
    id = UUID("019dbc9c-221b-7aa9-b2b7-3cacf8bcb8d6")

    schema = MarketHoliday(
        id=id,
        market="JP",
        holiday=date(2026, 1, 1),
    )

    result = to_model(schema)

    assert result.id == id
    assert result.market == "JP"
    assert result.year == 2026
    assert result.holiday == "2026-01-01"
