# parameter_master.py

from uuid import UUID

from pydantic import BaseModel


class ParameterMasterBase(BaseModel):
    """Defines the base parameter master schema with an item key, value, and optional
    start date.
    """

    item_key: str
    """The key identifier for the parameter."""

    item_value: str
    """The value associated with the parameter key."""

    item_fromdate: str | None = None
    """The optional start date from which the parameter is valid."""


class ParameterMaster(ParameterMasterBase):
    """Defines the complete parameter master schema including its unique identifier."""

    id: UUID
    """The unique identifier of the parameter master record."""


class ParameterMasterCreate(ParameterMasterBase):
    """Defines the schema for creating a new parameter master record."""

    pass


class ParameterMasterUpdate(BaseModel):
    """Defines the schema for updating an existing parameter master record with optional
    fields.
    """

    id: UUID
    """The unique identifier of the parameter master record to update."""

    item_key: str | None = None
    """The optional updated key identifier for the parameter."""

    item_value: str | None = None
    """The optional updated value associated with the parameter key."""

    item_fromdate: str | None = None
    """The optional updated start date from which the parameter is valid."""
