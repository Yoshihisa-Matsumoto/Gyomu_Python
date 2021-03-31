from gyomu.db_connection_factory import DbConnectionFactory, GYOMU_COMMON_MAINDB_CONNECTION
from gyomu.gyomu_db_model import *
import os
from gyomu.user_factory import UserFactory
from gyomu.user import User


TEST_APPLICATION_ID = 32650

def test_insert_app_info(environment_setup):

    app = GyomuAppsInfoCdtbl()
    app.application_id = TEST_APPLICATION_ID
    app.description = "Test Application"
    user: User = UserFactory.get_current_user()
    app.mail_from_name = user.userid
    app.mail_from_address = "Test@test.com"

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.add(app)
        session.commit()

    with DbConnectionFactory.get_gyomu_db_session() as session:
        app2 = session.query(GyomuAppsInfoCdtbl).get(TEST_APPLICATION_ID)
        assert app2 is not None

    with DbConnectionFactory.get_gyomu_db_session() as session:
        session.delete(app)
        session.commit()
