from datetime import date
from uuid import UUID

from pydantic import BaseModel


class MarketHoliday(BaseModel):
    """Represents a market holiday.

    Defines a market holiday record containing an identifier, market name, and holiday
    date.
    """

    id: UUID
    """The unique identifier.

    Unique identifier for the market holiday record.
    """
    market: str
    """The market name.

    Name or identifier of the market.
    """
    holiday: date
    """The holiday date.

    Date on which the holiday falls.
    """
