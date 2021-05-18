from gyomu.db_connection_factory import DbConnectionFactory, GYOMU_COMMON_MAINDB_CONNECTION
from gyomu.gyomu_db_model import *
import os
from gyomu.user_factory import UserFactory
from gyomu.user import User
from gyomu.gyomu_db_access import GyomuAppsInfoCdtblAccess


TEST_APPLICATION_ID2 = 32651
TEST_APPLICAIONT_ID_AMEND=32652

def test_insert_app_info(environment_setup):
    app = GyomuAppsInfoCdtblAccess.get(TEST_APPLICATION_ID2)
    if app is not None:
        GyomuAppsInfoCdtblAccess.delete(app)

    original_apps_count =  len(GyomuAppsInfoCdtblAccess.get_all())

    app = GyomuAppsInfoCdtbl()
    app.application_id = TEST_APPLICATION_ID2
    app.description = "Test Application"
    user: User = UserFactory.get_current_user()
    app.mail_from_name = user.userid
    app.mail_from_address = "Test@test.com"

    GyomuAppsInfoCdtblAccess.add(app)

    new_apps_count = len(GyomuAppsInfoCdtblAccess.get_all())

    assert new_apps_count == (original_apps_count+1)

    app = GyomuAppsInfoCdtblAccess.get(TEST_APPLICATION_ID2)
    amend_description="Test2 Application"
    app.description=amend_description
    amend_mail_name='dummy'
    app.mail_from_name=amend_mail_name
    amend_mail_address='Test2@test.com'
    app.mail_from_address = amend_mail_address

    GyomuAppsInfoCdtblAccess.update(app)
    app = GyomuAppsInfoCdtblAccess.get(TEST_APPLICATION_ID2)
    assert app.description == amend_description
    assert app.mail_from_name==amend_mail_name
    assert app.mail_from_address == amend_mail_address

    app.application_id= TEST_APPLICAIONT_ID_AMEND
    GyomuAppsInfoCdtblAccess.update(app, original_application_id=TEST_APPLICATION_ID2)
    app = GyomuAppsInfoCdtblAccess.get(TEST_APPLICATION_ID2)
    assert app is None
    app = GyomuAppsInfoCdtblAccess.get(TEST_APPLICAIONT_ID_AMEND)
    assert app.application_id == TEST_APPLICAIONT_ID_AMEND

    GyomuAppsInfoCdtblAccess.delete(app)