import uuid                   
                                    
from sqlalchemy import CHAR, Index, PrimaryKeyConstraint, SmallInteger, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class GyomuMarketHoliday(Base):
    __tablename__ = 'gyomu_market_holiday'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_gyomu_market_holiday'),
        Index('CX_gyomu_market_holiday', 'market', 'holiday', unique=True),
        Index('IX_gyomu_market_holiday', 'market', 'year')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    market: Mapped[str] = mapped_column(String(10, 'Japanese_CI_AS'), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    holiday: Mapped[str] = mapped_column(CHAR(10, 'Japanese_CI_AS'), nullable=False)
