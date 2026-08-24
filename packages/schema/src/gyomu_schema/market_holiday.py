from datetime import date
from uuid import UUID

from pydantic import BaseModel


class MarketHoliday(BaseModel):
    id: UUID
    market: str
    holiday: date
