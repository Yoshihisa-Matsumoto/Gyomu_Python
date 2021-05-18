import pytest
from gyomu.gyomu_db_model import *
from gyomu.gyomu_db_schema import *
from gyomu.user_factory import UserFactory
from gyomu.user import User
from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.json import Json
from marshmallow import ValidationError

gyomuapps_schema = GyomuAppsSchema()
gyomuapps_total_list_schema = GyomuAppsSchema(many=True)

gyomuapps_schema_load = GyomuAppsSchema(load_instance=True)
gyomuapps_total_list_schema_load = GyomuAppsSchema(many=True, load_instance=True)

TEST_APPLICATION_ID2 = 32651
TEST_APPLICAIONT_ID3 = 32652


class TestSchema:
    def test_gyomu_app(self):
        app = GyomuAppsInfoCdtbl()
        app.application_id = TEST_APPLICATION_ID2
        app.description = "Test Application"
        user: User = UserFactory.get_current_user()
        app.mail_from_name = user.userid
        app.mail_from_address = "Test@test.com"

        json_data = Json.to_json(app, gyomuapps_schema)
        app_loaded = Json.deserialize(json_data, GyomuAppsInfoCdtbl, gyomuapps_schema)
        assert app.application_id == app_loaded.application_id

        app2 = GyomuAppsInfoCdtbl()
        app2.application_id = TEST_APPLICAIONT_ID3
        app2.description = "Testw Application"
        user: User = UserFactory.get_current_user()
        app2.mail_from_name = user.userid
        app2.mail_from_address = "Testq@test.com"
        app_list = [app,app2]
        json_data = Json.to_json(app_list, gyomuapps_total_list_schema)
        #json_data = gyomuapps_total_list_schema.dumps(app_list)
        #dictionary = gyomuapps_total_list_schema.loads(json_data=json_data)
        #assert len(dictionary)==2
        app_list_loaded = Json.deserialize(json_data, GyomuAppsInfoCdtbl, gyomuapps_total_list_schema)
        assert len(app_list_loaded)==2

    def test_gyomu_app_load(self,environment_setup):
        app = GyomuAppsInfoCdtbl()
        app.application_id = TEST_APPLICATION_ID2
        app.description = "Test Application"
        user: User = UserFactory.get_current_user()
        app.mail_from_name = user.userid
        app.mail_from_address = "Test@test.com"

        json_data = gyomuapps_schema_load.dumps(app)
        dictionary = gyomuapps_schema.loads(json_data=json_data)
        with DbConnectionFactory.get_gyomu_db_session() as session:
            app_loaded = gyomuapps_schema_load.load(dictionary,session=session)
            assert app.application_id == app_loaded.application_id

        app2 = GyomuAppsInfoCdtbl()
        app2.application_id = TEST_APPLICAIONT_ID3
        app2.description = "Testw Application"
        user: User = UserFactory.get_current_user()
        app2.mail_from_name = user.userid
        app2.mail_from_address = "Testq@test.com"
        app_list = [app,app2]
        json_data = gyomuapps_total_list_schema.dumps(app_list)
        dictionary = gyomuapps_total_list_schema.loads(json_data=json_data)
        with DbConnectionFactory.get_gyomu_db_session() as session:
            apps = gyomuapps_total_list_schema_load.load(dictionary,session=session)
            assert len(apps)==2

    def test_gyomu_app_validation(self):
        app = GyomuAppsInfoCdtbl()
        app.application_id = TEST_APPLICATION_ID2
        app.description = "Test Application"
        user: User = UserFactory.get_current_user()
        app.mail_from_name = user.userid
        app.mail_from_address = "Test@test.com"

        json_data = Json.to_json(app, gyomuapps_schema)
        json_data = '{"mail_from_name": "yoshm", "description": "Test Application", "application_id": "Test", "mail_from_address": "Test@test.com"}'
        with pytest.raises(ValidationError) as ve:
            app2 = Json.deserialize(json_data, GyomuAppsInfoCdtbl, gyomuapps_schema)
        assert 'application_id' in ve.value.messages
        json_data = '{"mail_from_name": "yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789", ' \
                    '"description": "Test Application", "application_id": 32651, "mail_from_address": "Test@test.com"}'
        with pytest.raises(ValidationError) as ve:
            dictionary = gyomuapps_schema.loads(json_data=json_data)
        assert 'mail_from_name' in ve.value.messages
        json_data = '{"mail_from_name": "yoshm",' \
                    ' "description": "Test Application123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789Application123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789", ' \
                    '"application_id": 32651, "mail_from_address": "Test@test.com"}'
        with pytest.raises(ValidationError) as ve:
            dictionary = gyomuapps_schema.loads(json_data=json_data)
        assert 'description' in ve.value.messages
        json_data = '{"mail_from_name": "yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789yoshma123456789123456789123456789123456789123456789123456789", ' \
                    ' "description": "Test Application123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789Application123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789123456789", ' \
                    '"application_id": 32651, "mail_from_address": "Test@test.com"}'
        with pytest.raises(ValidationError) as ve:
            dictionary = gyomuapps_schema.loads(json_data=json_data)
        assert 'description' in ve.value.messages
        assert 'mail_from_name' in ve.value.messages

        json_data = '{"mail_from_name": "yoshm", "description": "Test Application", "application_id": 35456, "mail_from_address": "Testt.com"}'
        with pytest.raises(ValidationError) as ve:
            dictionary = gyomuapps_schema.loads(json_data=json_data)
            pass
        assert 'mail_from_address' in ve.value.messages