from datetime import date
from uuid import UUID
from gyomu_schema.market_holiday import MarketHoliday


def test_market_holiday() -> None:
    model = MarketHoliday(
        id=UUID("019DBC9C-221B-7AA9-B2B7-3CACF8BCB8D6"),
        market="JP",
        holiday=date(2026, 8, 17),
    )

    assert model.market == "JP"
    assert model.holiday == date(2026, 8, 17)
