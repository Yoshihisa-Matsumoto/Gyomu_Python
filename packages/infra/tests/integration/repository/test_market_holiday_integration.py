import os

import pytest
from datetime import date
from uuid import uuid4

from sqlalchemy import Engine, create_engine, delete
from sqlalchemy.orm import Session

from gyomu_infra.db.model.market_holiday import GyomuMarketHoliday
from gyomu_infra.repository.sqlalchemy_market_holiday import (
    SqlAlchemyMarketHolidayRepository,
)


TEST_MARKET = "#TEST"


def test_find_by_market(db_engine: Engine) -> None:
    
   
    with Session(db_engine) as session:
        # Arrange
        session.execute(
            delete(GyomuMarketHoliday).where(
                GyomuMarketHoliday.market == TEST_MARKET
            )
        )

        id_1 = uuid4()
        id_2 = uuid4()

        session.add_all(
            [
                GyomuMarketHoliday(
                    id=id_1,
                    market=TEST_MARKET,
                    year=2099,
                    holiday="2099-01-01",
                ),
                GyomuMarketHoliday(
                    id=id_2,
                    market=TEST_MARKET,
                    year=2099,
                    holiday="2099-01-02",
                ),
            ]
        )

        session.commit()

        # Act
        repository = SqlAlchemyMarketHolidayRepository(session)

        result = repository.find_by_market(TEST_MARKET)

        # Assert
        assert len(result) == 2

        assert result[0].id == id_1
        assert result[0].market == TEST_MARKET
        assert result[0].holiday == date(2099, 1, 1)

        assert result[1].id == id_2
        assert result[1].market == TEST_MARKET
        assert result[1].holiday == date(2099, 1, 2)


        # Cleanup
        session.execute(
            delete(GyomuMarketHoliday).where(
                GyomuMarketHoliday.market == TEST_MARKET
            )
        )
        session.commit()
