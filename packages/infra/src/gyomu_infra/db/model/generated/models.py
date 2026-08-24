from typing import Optional
import uuid

from sqlalchemy import CHAR, Index, PrimaryKeyConstraint, SmallInteger, String, Uuid
from sqlalchemy.dialects.mssql import NTEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class GyomuMarketHoliday(Base):
    __tablename__ = 'gyomu_market_holiday'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_gyomu_market_holiday'),
        Index('CX_gyomu_market_holiday', 'market', 'holiday', mssql_clustered=True, unique=True),
        Index('IX_gyomu_market_holiday', 'market', 'year', mssql_clustered=False)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    market: Mapped[str] = mapped_column(String(10, 'Japanese_CI_AS'), nullable=False)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    holiday: Mapped[str] = mapped_column(CHAR(10, 'Japanese_CI_AS'), nullable=False)


class GyomuParamMaster(Base):
    __tablename__ = 'gyomu_param_master'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='PK_gyomu_param_master'),
        Index('CX_gyomu_param_master', 'item_key', 'item_fromdate', mssql_clustered=True, unique=True)
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    item_key: Mapped[str] = mapped_column(String(50, 'Japanese_CI_AS'), nullable=False)
    item_value: Mapped[str] = mapped_column(NTEXT(8, 'Japanese_CI_AS'), nullable=False)
    item_fromdate: Mapped[Optional[str]] = mapped_column(String(10, 'Japanese_CI_AS'))
