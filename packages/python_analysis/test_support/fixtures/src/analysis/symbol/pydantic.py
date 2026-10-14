from pydantic import BaseModel, Field


class User(BaseModel):
    id: int = Field(
        description="Primary identifier",
    )


class FieldDescriptionModel(BaseModel):
    value: int = Field(description="Primary identifier")


class FieldAliasModel(BaseModel):
    value: int = Field(alias="user_id")


class FieldDescriptionAndAliasModel(BaseModel):
    value: int = Field(
        description="Primary identifier",
        alias="user_id",
    )


class FieldDefaultModel(BaseModel):
    value: int = Field(0)


class FieldEllipsisModel(BaseModel):
    value: int = Field(...)


class FieldEmptyModel(BaseModel):
    value: int = Field()


class FieldOptionalModel(BaseModel):
    value: int | None = Field(description="Optional value")


class NonFieldModel(BaseModel):
    value: int = 0
