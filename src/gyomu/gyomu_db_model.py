# coding: utf-8
from sqlalchemy import BigInteger, Boolean, CHAR, Column, DateTime, Index, Integer, SmallInteger, String, Text, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class GyomuAppsInfoCdtbl(Base):
    __tablename__ = 'gyomu_apps_info_cdtbl'

    application_id = Column(SmallInteger, primary_key=True)
    description = Column(String(50))
    mail_from_address = Column(String(200))
    mail_from_name = Column(String(200))


class GyomuMarketHoliday(Base):
    __tablename__ = 'gyomu_market_holiday'
    __table_args__ = (
        Index('ix_gyomu_market_holiday', 'market', 'year'),
    )

    market = Column(String(10), primary_key=True, nullable=False)
    year = Column(SmallInteger, nullable=False)
    holiday = Column(CHAR(8), primary_key=True, nullable=False)


class GyomuMilestoneDaily(Base):
    __tablename__ = 'gyomu_milestone_daily'

    target_date = Column(String(8), primary_key=True, nullable=False)
    milestone_id = Column(String(200), primary_key=True, nullable=False, index=True)
    update_time = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))


class GyomuParamMaster(Base):
    __tablename__ = 'gyomu_param_master'

    item_key = Column(String(50), primary_key=True, nullable=False)
    item_value = Column(Text, nullable=False)
    item_fromdate = Column(String(8), primary_key=True, nullable=False, server_default=text("''::character varying"))


class GyomuServiceCdtbl(Base):
    __tablename__ = 'gyomu_service_cdtbl'

    id = Column(SmallInteger, primary_key=True)
    description = Column(String(100), nullable=False)
    service_type_id = Column(SmallInteger, nullable=False)
    parameter = Column(Text)


class GyomuServiceTypeCdtbl(Base):
    __tablename__ = 'gyomu_service_type_cdtbl'

    id = Column(SmallInteger, primary_key=True)
    description = Column(String(100), nullable=False)
    assembly_name = Column(String(100))
    class_name = Column(String(100))


class GyomuStatusHandler(Base):
    __tablename__ = 'gyomu_status_handler'

    id = Column(Integer, primary_key=True)
    application_id = Column(SmallInteger, nullable=False)
    region = Column(String(3))
    status_type = Column(SmallInteger)
    recipient_address = Column(String(200))
    recipient_type = Column(String(3))


class GyomuStatusInfo(Base):
    __tablename__ = 'gyomu_status_info'

    id = Column(BigInteger, primary_key=True)
    application_id = Column(SmallInteger, nullable=False)
    entry_date = Column(DateTime(True), nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP"))
    entry_author = Column(String(30), nullable=False)
    status_type = Column(SmallInteger, nullable=False)
    error_id = Column(SmallInteger, nullable=False)
    instance_id = Column(Integer, nullable=False)
    hostname = Column(String(50))
    summary = Column(String(400))
    description = Column(String(1000))
    developer_info = Column(Text)


class GyomuStatusTypeCdtbl(Base):
    __tablename__ = 'gyomu_status_type_cdtbl'

    status_type = Column(SmallInteger, primary_key=True)
    description = Column(String(15))


class GyomuTaskData(Base):
    __tablename__ = 'gyomu_task_data'

    id = Column(BigInteger, primary_key=True)
    application_id = Column(SmallInteger, nullable=False, index=True)
    task_info_id = Column(SmallInteger, nullable=False, index=True)
    entry_date = Column(DateTime(True), nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP"))
    entry_author = Column(String(30), nullable=False, index=True)
    parent_task_data_id = Column(BigInteger)
    parameter = Column(Text)


class GyomuTaskDataLog(Base):
    __tablename__ = 'gyomu_task_data_log'
    __table_args__ = (
        Index('cx_gyomu_task_data_log', 'task_data_id', 'log_time'),
    )

    id = Column(BigInteger, primary_key=True)
    task_data_id = Column(BigInteger, nullable=False)
    log_time = Column(DateTime(True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    log = Column(Text, nullable=False)


class GyomuTaskDataStatus(Base):
    __tablename__ = 'gyomu_task_data_status'

    task_data_id = Column(BigInteger, primary_key=True)
    task_status = Column(String(10))
    latest_update_date = Column(DateTime(True), nullable=False)
    latest_task_instance_id = Column(BigInteger, nullable=False)


class GyomuTaskInfoAccessList(Base):
    __tablename__ = 'gyomu_task_info_access_list'
    __table_args__ = (
        Index('cx_gyomu_task_info_access_list', 'application_id', 'task_info_id', 'account_name'),
    )

    id = Column(BigInteger, primary_key=True)
    application_id = Column(SmallInteger, nullable=False)
    task_info_id = Column(SmallInteger, nullable=False)
    account_name = Column(String(100), nullable=False)
    can_access = Column(Boolean, nullable=False)
    forbidden = Column(Boolean, nullable=False)


class GyomuTaskInfoCdtbl(Base):
    __tablename__ = 'gyomu_task_info_cdtbl'

    application_id = Column(SmallInteger, primary_key=True, nullable=False)
    task_id = Column(SmallInteger, primary_key=True, nullable=False)
    description = Column(String(100), nullable=False)
    assembly_name = Column(String(100), nullable=False)
    class_name = Column(String(100), nullable=False)
    restartable = Column(Boolean, nullable=False)


class GyomuTaskInstance(Base):
    __tablename__ = 'gyomu_task_instance'

    id = Column(BigInteger, primary_key=True)
    task_data_id = Column(BigInteger, nullable=False, index=True)
    entry_date = Column(DateTime(True), nullable=False, index=True, server_default=text("CURRENT_TIMESTAMP"))
    entry_author = Column(String(30), nullable=False)
    task_status = Column(String(10), index=True)
    is_done = Column(Boolean, nullable=False)
    status_info_id = Column(BigInteger)
    parameter = Column(Text)
    comment = Column(Text)


class GyomuTaskInstanceSubmitInformation(Base):
    __tablename__ = 'gyomu_task_instance_submit_information'
    __table_args__ = (
        Index('cx_gyomu_task_instance_submit_information', 'task_instance_id', 'submit_to'),
    )

    id = Column(BigInteger, primary_key=True)
    task_instance_id = Column(BigInteger, nullable=False)
    submit_to = Column(String(30))


class GyomuTaskSchedulerConfig(Base):
    __tablename__ = 'gyomu_task_scheduler_config'
    __table_args__ = (
        Index('ix_gyomu_task_scheduler_config3', 'application_id', 'task_id'),
    )

    id = Column(BigInteger, primary_key=True)
    service_id = Column(SmallInteger, nullable=False, index=True)
    description = Column(String(200), nullable=False, index=True)
    application_id = Column(SmallInteger, nullable=False)
    task_id = Column(SmallInteger, nullable=False)
    monitor_parameter = Column(Text, nullable=False)
    next_trigger_time = Column(DateTime(True), nullable=False)
    task_parameter = Column(Text)
    is_enabled = Column(Boolean, nullable=False, index=True)


class GyomuVariableParameter(Base):
    __tablename__ = 'gyomu_variable_parameter'

    variable_key = Column(String(20), primary_key=True)
    description = Column(String(200), nullable=False)