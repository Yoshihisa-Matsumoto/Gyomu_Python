from gyomu.db_connection_factory import DbConnectionFactory
from gyomu.gyomu_db_model import GyomuTaskData, GyomuTaskInfoCdtbl, GyomuTaskInstance, GyomuTaskInfoAccessList, \
    GyomuTaskDataStatus, GyomuTaskInstanceSubmitInformation
from gyomu.configurator import Configurator
from gyomu.user import User
from gyomu.user_factory import UserFactory
import threading
from abc import ABCMeta, abstractmethod
from gyomu.tasks.delegate import DelegateInformation
from gyomu.tasks.proposal import ProposalInformation
from gyomu.status_code import StatusCode
from gyomu.common_status_code import CommonStatusCode


class AbstractBaseTask(metaclass=ABCMeta):
    _task_data_parameter: str =''

    _current_task: GyomuTaskData = None
    __current_task_info: GyomuTaskInfoCdtbl = None

    __lock = threading.Lock()

    __task_data_loaded: bool = False
    _task_data_id: int =-1
    __config: Configurator

    _latest_instance: GyomuTaskInstance = None
    _latest_instance_id: int = -1


    @property
    def task_data_id(self) -> int:
        return self._task_data_id

    __instances: [GyomuTaskInstance] =[]

    @property
    def _instance_list(self):
        return self.__instances

    @property
    def latest_instance(self) -> GyomuTaskInstance:
        return self._latest_instance

    @property
    def current_task_info(self) -> GyomuTaskInfoCdtbl:
        if self.__current_task_info is None:
            with DbConnectionFactory.get_gyomu_db_session() as session:
                self.__current_task_info = session.query(GyomuTaskInfoCdtbl).filter(
                    GyomuTaskInfoCdtbl.application_id == self.application_id
                    and GyomuTaskInfoCdtbl.task_id == self.task_info_id).one()
        return self.__current_task_info

    @property
    def latest_instance_id(self) -> int:
        return self._latest_instance_id

    @property
    def instances(self) -> list[GyomuTaskInstance]:
        return self.__instances

    @property
    def config(self) -> Configurator:
        return self.__config

    @property
    def current_user(self) -> User:
        return self.config.user

    @property
    def access_list(self) -> list[GyomuTaskInfoAccessList]:
        return self.__access_list

    STATUS_INIT = 'INIT'
    STATUS_EXECUTE = 'EXEC'
    STATUS_COMPLETE = 'COMPLETE'
    STATUS_FAIL = 'FAIL'
    STATUS_REQUEST = 'REQUEST'
    STATUS_APPROVAL = 'APPROVE'
    STATUS_REJECT = 'REJECT'
    STATUS_NOTEXEC = 'NOTEXEC'
    STATUS_CANCEL = 'CANCEL'
    STATUS_DELEGATE = 'DELEGATE'

    DELEGATE_BACK_TO_OWNER = '@@OWNER@@'
    DELEGATE_BACK_TO_PREVIOUS_PERSON = '@@PREVIOUS@@'
    PROPOSE_TO_OWNER = '@@PROPOSITION_OWNER@@'
    PROPOSE_TO_DESTINATION = '@@PROPOSITION_DESTINATION@@'

    @property
    def _can_request(self):
        return self.__next_action_enable(self.STATUS_REQUEST)

    @property
    def _can_approve(self):
        return self.__next_action_enable(self.STATUS_APPROVAL)

    @property
    def _can_reject(self):
        return self.__next_action_enable(self.STATUS_REJECT)

    @property
    def _can_cancel(self):
        return self.__next_action_enable(self.STATUS_CANCEL)

    @property
    def _can_execute(self):
        return self.__next_action_enable(self.STATUS_EXECUTE)

    _async_thread: threading.Thread

    def __init__(self, config: Configurator):
        self.__config = config

    # def __init_subclass__(cls, **kwargs):
    #     super().__init_subclass__()
    #     if cls.__config is None:
    #         raise ValueError('task needs config in initialization')

    def start(self, parameter: str, comment: str) -> StatusCode:
        result: StatusCode = self.__init(parameter, comment)
        if not result.is_success:
            return result
        return self.__run(parameter,comment)

    def abort(self, parameter: str, comment: str) -> StatusCode:
        result: StatusCode = self.__create_new_instance(parameter=parameter, status=self.STATUS_CANCEL, comment=comment)
        if not result.is_success:
            return result
        return self.on_cancel(parameter, comment)

    def __init(self, parameter: str, comment: str) -> StatusCode:
        result: StatusCode
        try:
            result = self.__check_status_and_owner(self.STATUS_INIT)
            if not result.is_success:
                return result
            self._task_data_parameter = parameter
            if self.task_data_id != -1:
                return StatusCode(CommonStatusCode.TASK_ALREADY_GENERATED,
                                  arguments=[self.application_id, self.task_info_id, self._task_data_parameter,
                                             self.task_data_id],
                                  config=self.config, target_application_id=self.application_id)

            try:
                with DbConnectionFactory.get_gyomu_db_session() as session:
                    task_data = GyomuTaskData()
                    task_data.application_id = self.application_id
                    task_data.task_info_id = self.task_info_id
                    task_data.entry_author = self.config.username
                    task_data.parameter = parameter
                    session.add(task_data)
                    session.flush()
                    task_instance = GyomuTaskInstance()
                    task_instance.task_data_id = task_data.id
                    task_instance.entry_date = task_data.entry_date
                    task_instance.entry_author = task_data.entry_author
                    task_instance.task_status = "INIT"
                    task_instance.is_done = False
                    task_instance.parameter = parameter
                    task_instance.comment = comment
                    session.add(task_instance)
                    session.flush()
                    task_status = GyomuTaskDataStatus()
                    task_status.task_data_id = task_data.id
                    task_status.latest_task_instance_id = task_instance.id
                    task_status.latest_update_date = task_instance.entry_date
                    task_status.task_status = task_instance.task_status
                    session.add(task_status)
                    session.commit()
                    self._current_task = task_data
                    self._task_data_id = task_data.id
                    self._latest_instance = task_instance
                    self.__instances = [task_instance]
                    self._latest_instance_id = task_instance.id
            except Exception as ex:
                return StatusCode(CommonStatusCode.TASK_GENERATE_ERROR,
                                  arguments=[self.application_id, self.task_info_id, parameter],
                                  config=self.config, target_application_id=self.application_id,
                                  exception=ex)
        except Exception as ex:
            return StatusCode(CommonStatusCode.TASK_LIBRARY_INTERNAL_ERROR,
                              arguments=[self.application_id, self.task_info_id, parameter, self.task_data_id],
                              config=self.config, target_application_id=self.application_id,
                              exception=ex)
        return result

    def __run(self, parameter: str, comment: str) -> StatusCode:
        try:
            with self.__lock:
                self.__lock_instance_and_refresh_task_data()
                return self.__execution_decision(parameter, comment)

        except Exception as ex:
            return StatusCode(CommonStatusCode.TASK_LIBRARY_INTERNAL_ERROR,
                              arguments=[self.application_id, self.task_info_id, parameter, self.task_data_id],
                              config=self.config, target_application_id=self.application_id,
                              exception=ex)

    def __execution_decision(self, parameter: str, comment: str) -> StatusCode:
        apply_information = self.proposal_information
        if apply_information.proposal_required:
            return self.__send_apply(apply_information, parameter, comment)
        else:
            delegate_information = self.delegate_information
            if self.is_async and (self.current_user in delegate_information.delegation_users):
                result = self.on_delegate(parameter, comment)
                if not result.is_success:
                    return result
                return self.__create_new_instance(parameter, self.STATUS_DELEGATE,
                                                  delegate_information.delegation_users, None, comment)

            else:
                result = self.__create_new_instance(parameter, self.STATUS_EXECUTE,
                                                    None, None, comment)
                if not result.is_success:
                    return result
                if self.is_async:
                    thread1 = threading.Thread(target=self.do_exec, args=[parameter])
                    thread1.start()
                    self._async_thread = thread1
                    return StatusCode.SUCCEED_STATUS
                else:
                    return self.do_exec(parameter)

    def __create_new_instance(self, parameter: str, status: str, submit_to: list[User] = None,
                              status_code: StatusCode = None, comment: str = '') -> StatusCode:
        try:
            new_instance = GyomuTaskInstance()
            with DbConnectionFactory.get_gyomu_db_session() as session:

                new_instance.task_data_id = self._current_task.id
                new_instance.is_done = status in [self.STATUS_COMPLETE, self.STATUS_FAIL, self.STATUS_CANCEL]
                # new_instance.entry_date = self._current_task.entry_date
                new_instance.entry_author = self.config.username
                new_instance.task_status = status
                new_instance.parameter = parameter
                new_instance.comment = comment
                new_instance.status_info_id = None if status_code is None else status_code.get_status_id()
                session.add(new_instance)
                session.flush()
                task_status = session.get(GyomuTaskDataStatus, self._current_task.id)
                if task_status is None:
                    task_status = GyomuTaskDataStatus()
                    task_status.task_data_id = self._current_task.id
                    task_status.latest_task_instance_id = new_instance.id
                    task_status.latest_update_date = new_instance.entry_date
                    task_status.task_status = new_instance.task_status
                    session.add(task_status)
                else:
                    task_status.latest_task_instance_id = new_instance.id
                    task_status.latest_update_date = new_instance.entry_date
                    task_status.task_status = new_instance.task_status

                if submit_to is not None and len(submit_to) > 0:
                    for user in submit_to:
                        if user.is_valid:
                            submit_information = GyomuTaskInstanceSubmitInformation()
                            submit_information.task_instance_id = self.latest_instance_id
                            submit_information.submit_to = user.userid
                            session.add(submit_information)

                session.commit()
                self._latest_instance = new_instance
                self._latest_instance_id = new_instance.id
                self.__instances.append(new_instance)

            return StatusCode.SUCCEED_STATUS

        except Exception as ex:
            return StatusCode(CommonStatusCode.TASK_INSTANCE_GENERATE_ERROR,
                              arguments=[self.application_id, self.task_info_id, self.task_data_id, parameter],
                              config=self.config, target_application_id=self.application_id,
                              exception=ex)

    def on_delegate(self, parameter: str, comment: str) -> StatusCode:
        return StatusCode.SUCCEED_STATUS

    def __check_status_and_owner(self, target_status: str) -> StatusCode:
        if not self.__internal_valid_status(target_status):
            return StatusCode(CommonStatusCode.TASK_STATUS_INCONSISTENT,
                              arguments=[self.application_id, self.task_info_id, self.task_data_id,
                                         self.latest_instance_id, self.latest_instance.task_status, target_status],
                              config=self.config, target_application_id=self.application_id)
        elif not self.__internal_valid_owner(target_status):
            return StatusCode(CommonStatusCode.INVALID_USER_ACCESS,
                              arguments=[self.application_id, self.task_info_id, self.task_data_id,
                                         self.latest_instance_id, target_status, self.current_user.userid],
                              config=self.config, target_application_id=self.application_id)
        else:
            return StatusCode.SUCCEED_STATUS

    def __next_action_enable(self, status: str) -> bool:
        with self.__lock:
            self.__load_task_data()
            if self.latest_instance is None:
                return False
            eligibility = self.__internal_valid_owner(status) and self.__internal_valid_status(status)
            if status == self.STATUS_REQUEST:
                if eligibility:
                    if self.proposal_information.proposal_required:
                        return True
                return False
            return eligibility

    def __internal_valid_owner(self, target_status_mnemonic: str) -> bool:
        if self.latest_instance is None:
            return True

        if target_status_mnemonic == self.STATUS_INIT:
            return True if self.__internal_check_task_accessibility else False

        current_status: str
        current_status = self.latest_instance.task_status

        if target_status_mnemonic == self.STATUS_APPROVAL or target_status_mnemonic == self.STATUS_REJECT:
            if not self._is_self_approve_enable():
                requester: User = UserFactory.get_user(self.latest_instance.entry_author)
                if requester.is_valid and requester == self.current_user:
                    return False
            for task_submit_information in self.__get_task_submission_information_list(self.latest_instance):
                submit_user: User = UserFactory.get_user(task_submit_information.submit_to)
                if submit_user.is_valid:
                    if not submit_user.is_group and submit_user == self.current_user:
                        return True
                    if submit_user.is_group and self.current_user.is_in_member(submit_user):
                        return True
        elif target_status_mnemonic == self.STATUS_EXECUTE:
            if current_status != self.STATUS_DELEGATE:
                if self.delegate_information.delegation_required:
                    # self.instances
                    current_delegated_instances = [instance for instance in self.instances
                                                   if instance.task_status == self.STATUS_DELEGATE
                                                   and instance.entry_author == self.current_user.userid]
                    if len(current_delegated_instances) > 0:
                        return True

                previous_user: User = UserFactory.get_user(self.latest_instance.entry_author)
                if previous_user.is_valid and previous_user == self.current_user:
                    return True
            else:
                for task_submit_information in self.__get_task_submission_information_list(self.latest_instance):
                    submit_user: User = UserFactory.get_user(task_submit_information.submit_to)
                    if submit_user.is_valid:
                        if not submit_user.is_group and submit_user == self.current_user:
                            return True
                        if submit_user.is_group and self.current_user.is_in_member(submit_user):
                            return True

        elif target_status_mnemonic == self.STATUS_REQUEST:
            # Approver or Starter
            starter: User = UserFactory.get_user(self._current_task.entry_author)
            if starter.is_valid and starter == self.current_user:
                return True
            if self.latest_instance.task_status == self.STATUS_APPROVAL:
                approver: User = UserFactory.get_user(self.latest_instance.entry_author)
                if approver.is_valid and approver == self.current_user:
                    return True
        elif target_status_mnemonic == self.STATUS_CANCEL:
            # Requestor
            requester: User = UserFactory.get_user(self.latest_instance.entry_author)
            if requester.is_valid and requester == self.current_user:
                return True

        elif target_status_mnemonic == self.STATUS_COMPLETE:
            if not self.__internal_check_task_accessibility:
                return False
            if current_status == self.STATUS_FAIL:
                return True

        else:
            return True
        return False

    def __internal_valid_status(self, target_status_mnemonic: str) -> bool:
        if self.latest_instance is None:
            return True
        current_status = self.latest_instance.task_status

        if target_status_mnemonic == self.STATUS_APPROVAL or target_status_mnemonic == self.STATUS_REJECT:
            if current_status == self.STATUS_REQUEST:
                return True
        elif target_status_mnemonic == self.STATUS_EXECUTE:
            if current_status in [self.STATUS_DELEGATE, self.STATUS_INIT, self.STATUS_APPROVAL]:
                return True
            if current_status in [self.STATUS_COMPLETE or self.STATUS_FAIL] \
                    and self.current_task_info.restartable:
                return True
        elif target_status_mnemonic == self.STATUS_REQUEST:
            if current_status in [self.STATUS_INIT, self.STATUS_APPROVAL, self.STATUS_CANCEL, self.STATUS_REJECT]:
                return True
        elif target_status_mnemonic == self.STATUS_DELEGATE:
            if current_status in [self.STATUS_INIT, self.STATUS_APPROVAL]:
                return True
        elif target_status_mnemonic == self.STATUS_CANCEL:
            if current_status == self.STATUS_REQUEST:
                return True
        else:
            return True
        return False

    @property
    @abstractmethod
    def application_id(self) -> int:
        pass

    @property
    @abstractmethod
    def task_info_id(self) -> int:
        pass

    @property
    @abstractmethod
    def delegate_information(self) -> DelegateInformation:
        pass

    @property
    @abstractmethod
    def proposal_information(self) -> ProposalInformation:
        pass

    @property
    @abstractmethod
    def is_async(self) -> bool:
        pass

    @abstractmethod
    def on_exec(self, parameter: str) -> StatusCode:
        pass

    def on_request(self, parameter: str, comment: str) -> StatusCode:
        return StatusCode.SUCCEED_STATUS

    def is_email_required(self, request_status: str) -> bool:
        return True

    def on_cancel(self, parameter: str, comment: str) -> StatusCode:
        return StatusCode.SUCCEED_STATUS

    def do_exec(self, parameter: str) -> StatusCode:
        result: StatusCode = StatusCode.SUCCEED_STATUS
        try:
            try:
                result = self.on_exec(parameter if parameter else self._task_data_parameter)
                if result.is_success:
                    # notify "[Task] " + this.CurrentTaskInfo.description + " Done"
                    pass
            except Exception as ex:
                result = StatusCode(CommonStatusCode.TASK_EXECUTION_FAILED,
                                    arguments=[self.application_id, self.task_info_id, self._task_data_parameter,
                                               self.task_data_id],
                                    exception=ex,
                                    config=self.config, target_application_id=self.application_id)

            result = self.__create_new_instance(parameter,
                                                status=self.STATUS_COMPLETE if result.is_success else self.STATUS_FAIL,
                                                submit_to=None, status_code=None if result.is_success else result,
                                                comment='')
        except Exception as ex2:
            result = StatusCode(CommonStatusCode.TASK_LIBRARY_INTERNAL_ERROR,
                                arguments=[self.application_id, self.task_info_id, self._task_data_parameter,
                                           self.task_data_id],
                                exception=ex2,
                                config=self.config, target_application_id=self.application_id)
        # Event Notification for Task Finish

        return result

    def __get_task_submission_information_list(self, latest_instance: GyomuTaskInstance) \
            -> list[GyomuTaskInstanceSubmitInformation]:
        with DbConnectionFactory.get_gyomu_db_session() as session:
            return session.query(GyomuTaskInstanceSubmitInformation).filter(
                GyomuTaskInstanceSubmitInformation.task_instance_id == latest_instance.id).all()

    def _is_self_approve_enable(self) -> bool:
        return True

    def __lock_instance_and_refresh_task_data(self):
        with DbConnectionFactory.get_gyomu_db_session() as session:
            task_data = session.query(GyomuTaskData).filter(
                GyomuTaskData.id == self.task_data_id).with_for_update().one()
            self.__load_task_data(session)

    def __load_task_data(self, upper_session=None):
        if self.__task_data_loaded:
            return

        task_data: GyomuTaskData
        if upper_session is not None:
            session = upper_session
        else:
            session = DbConnectionFactory.get_gyomu_db_session()

        if self._current_task is None:
            task_data = session.get(GyomuTaskData, self.task_data_id)
            self._current_task = task_data
        self._task_data_parameter = self._current_task.parameter
        self.__instances = session.query(GyomuTaskInstance). \
            filter(GyomuTaskInstance.task_data_id == self._current_task.id).order_by(
            GyomuTaskInstance.entry_date.desc()).all()
        self._latest_instance = self.__instances[0]
        self.__access_list = session.query(GyomuTaskInfoAccessList). \
            filter(
            GyomuTaskInfoAccessList.application_id == self.application_id
            and GyomuTaskInfoAccessList.task_info_id == self.task_info_id).all()

        if upper_session is None:
            with session:
                pass

        self.__task_data_loaded = True

    @property
    def __internal_check_task_accessibility(self) -> bool:
        if len(self.access_list) == 0:
            return True
        current_user_name = self.config.username.upper()
        can_access: bool = False
        for access in self.access_list:
            account_name: str = access.account_name
            if current_user_name == account_name.upper():
                if access.forbidden:
                    return False
                if access.can_access:
                    can_access = True
            target_user: User = UserFactory.get_user(account_name)
            if target_user.is_valid and target_user.is_group:
                if self.config.user.is_in_member(target_user):
                    if access.forbidden:
                        return False
                    if access.can_access:
                        can_access = True
        return can_access

    def __send_apply(self, apply_information, parameter, comment) -> StatusCode:
        result = self.__check_status_and_owner(self.STATUS_REQUEST)
        if not result.is_success:
            return result
        result = self.__create_new_instance(parameter=parameter, comment=comment, status=self.STATUS_REQUEST,
                                            submit_to=apply_information.destination_persons)
        if not result.is_success:
            return result
        result = self.on_request(parameter, comment)
        if not result.is_success:
            return result
        if self.is_email_required(self.STATUS_REQUEST):
            return self.__send_proposal_mail_from_requested_status(apply_information.destination_persons, comment,
                                                                   self.STATUS_REQUEST)
        return result

    def __send_proposal_mail_from_requested_status(self, recipients: list[User], comment: str,
                                                   requested_status: str) -> StatusCode:
        requested_action = ''
        if requested_status == self.STATUS_REQUEST:
            requested_action = "submitted"
        elif requested_status == self.STATUS_APPROVAL:
            requested_action = "approved"
        elif requested_status == self.STATUS_REJECT:
            requested_action = "rejected"
        elif requested_status == self.STATUS_CANCEL:
            requested_action = "cancelled"

        mail_subject = ''
        if self.current_task_info is not None:
            mail_subject = self.current_task_info.description + ' approval request ' + requested_action + ' by ' + self.current_user.userid
        mail_body = ''
        if comment:
            mail_body = comment

        # self.on_custom_mail_information(requested_status, recipients, comment,  )
        return StatusCode.SUCCEED_STATUS
        # pending till we find way to retrieve mailaddress from user account
