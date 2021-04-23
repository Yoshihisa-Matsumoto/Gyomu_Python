from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.gyomu_db_model import GyomuMilestoneDaily
from datetime import date, datetime, timedelta
from sqlalchemy.sql import exists
import time


class MilestoneAccess:
    @staticmethod
    def __get_target_date(target_date: date, is_monthly: bool) -> str:
        if is_monthly:
            return target_date.strftime('%Y%m') + '**'
        else:
            return target_date.strftime('%Y%m%d')

    @staticmethod
    def exists(milestone_id: str, target_date: date, is_monthly: bool = False) -> bool:
        target_date_yyyymmdd = MilestoneAccess.__get_target_date(target_date, is_monthly)
        with DbConnectionFactory.get_gyomu_db_session() as session:
            return session.query(exists().where(GyomuMilestoneDaily.milestone_id == milestone_id
                                                and GyomuMilestoneDaily.target_date == target_date_yyyymmdd)).scalar()

    @staticmethod
    def register(milestone_id: str, target_date: date, is_monthly: bool = False):
        if MilestoneAccess.exists(milestone_id, target_date, is_monthly):
            return
        target_date_yyyymmdd = MilestoneAccess.__get_target_date(target_date, is_monthly)
        with DbConnectionFactory.get_gyomu_db_session() as session:
            milestone = GyomuMilestoneDaily()
            milestone.milestone_id= milestone_id
            milestone.target_date = target_date_yyyymmdd
            session.add(milestone)
            session.commit()

    @staticmethod
    def unregister(milestone_id: str, target_date: date, is_monthly: bool = False):
        target_date_yyyymmdd = MilestoneAccess.__get_target_date(target_date, is_monthly)
        record: GyomuMilestoneDaily
        with DbConnectionFactory.get_gyomu_db_session() as session:
            record = session.query(GyomuMilestoneDaily).\
                filter(GyomuMilestoneDaily.milestone_id == milestone_id
                       and GyomuMilestoneDaily.target_date == target_date_yyyymmdd).first()
            if record is not None:
                session.delete(record)
                session.commit()


    @staticmethod
    def wait(milestone_id: str, target_date: date, timeout_minutes:int, is_monthly: bool = False) -> bool:
        timeout = datetime.now() + timedelta(minutes=timeout_minutes)
        while timeout > datetime.now():
            if MilestoneAccess.exists(milestone_id, target_date, is_monthly):
                return True
            time.sleep(5)
        return False
