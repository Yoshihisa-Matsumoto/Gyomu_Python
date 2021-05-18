from gyomu.gyomu_db_model import GyomuAppsInfoCdtbl
from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.status_code import StatusCode
from gyomu.gyomu_db_schema import GyomuAppsSchema

gyomuapps_schema = GyomuAppsSchema()

class GyomuAppsInfoCdtblAccess:
    @staticmethod
    def get_all() -> (list[GyomuAppsInfoCdtbl], StatusCode):
        with DbConnectionFactory.get_gyomu_db_session() as session:
            return session.query(GyomuAppsInfoCdtbl).all(), StatusCode.SUCCEED_STATUS

    @staticmethod
    def get(application_id: int) -> (GyomuAppsInfoCdtbl, StatusCode):
        with DbConnectionFactory.get_gyomu_db_session() as session:
            return session.query(GyomuAppsInfoCdtbl).get(application_id), StatusCode.SUCCEED_STATUS

    @staticmethod
    def add(app: GyomuAppsInfoCdtbl) -> StatusCode :
        with DbConnectionFactory.get_gyomu_db_session() as session:
            session.add(app)
            session.commit()
        return StatusCode.SUCCEED_STATUS

    @staticmethod
    def convert_from_json(json_string: str) -> (GyomuAppsInfoCdtbl, StatusCode):
        dictionary = gyomuapps_schema.loads(json_data=json_string)
        return GyomuAppsInfoCdtbl(**dictionary), StatusCode.SUCCEED_STATUS

    @staticmethod
    def add_from_json(json_string: str) -> StatusCode:
        app, ret_val = GyomuAppsInfoCdtblAccess.convert_from_json(json_string)
        if not ret_val.is_success:
            return ret_val
        return GyomuAppsInfoCdtblAccess.add(app)

    @staticmethod
    def update(app: GyomuAppsInfoCdtbl,original_application_id = -1) -> StatusCode.SUCCEED_STATUS:
        with DbConnectionFactory.get_gyomu_db_session() as session:
            application_id = app.application_id if original_application_id==-1 else original_application_id
            current_app: GyomuAppsInfoCdtbl = session.query(GyomuAppsInfoCdtbl).get(application_id)
            if original_application_id !=-1:
                current_app.application_id = app.application_id
            current_app.description = app.description
            current_app.mail_from_name=app.mail_from_name
            current_app.mail_from_address=app.mail_from_address
            session.commit()
        return StatusCode.SUCCEED_STATUS

    @staticmethod
    def update_from_json(json_string: str, original_application_id = -1) -> StatusCode.SUCCEED_STATUS:
        app, ret_val = GyomuAppsInfoCdtblAccess.convert_from_json(json_string)
        if not ret_val.is_success:
            return ret_val
        return GyomuAppsInfoCdtblAccess.update(app,original_application_id=original_application_id)

    @staticmethod
    def delete( app: GyomuAppsInfoCdtbl) -> StatusCode.SUCCEED_STATUS:
        with DbConnectionFactory.get_gyomu_db_session() as session:
            app = session.query(GyomuAppsInfoCdtbl).get(app.application_id)
            session.delete(app)
            session.commit()
        return StatusCode.SUCCEED_STATUS


