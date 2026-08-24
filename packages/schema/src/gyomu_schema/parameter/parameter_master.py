# parameter_master.py

from uuid import UUID

from pydantic import BaseModel


class ParameterMasterBase(BaseModel):
    item_key: str
    item_value: str
    item_fromdate: str | None = None


class ParameterMaster(ParameterMasterBase):
    id: UUID


class ParameterMasterCreate(ParameterMasterBase):
    pass


class ParameterMasterUpdate(BaseModel):
    id: UUID
    item_key: str | None = None
    item_value: str | None = None
    item_fromdate: str | None = None
