from gyomu.gyomu_db_model import GyomuAppsInfoCdtbl
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate

class GyomuAppsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model= GyomuAppsInfoCdtbl
        load_instance = False

    mail_from_address = fields.Email(validate=validate.Length(max=200))