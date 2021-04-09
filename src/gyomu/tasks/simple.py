from gyomu.tasks.abstract_base_task import AbstractBaseTask
from gyomu.tasks.delegate import DelegateInformation, DelegateInformationFactory
from gyomu.tasks.proposal import ProposalInformation
from gyomu.status_code import StatusCode
from abc import abstractmethod
from gyomu.variable import VariableTranslator
from datetime import date, datetime
from gyomu.configurator import Configurator


class AbstractSimpleTask(AbstractBaseTask):
    # def __init__(self, config: Configurator):
    #     super().__init__(config)

    @property
    def delegate_information(self) -> DelegateInformation:
        return DelegateInformationFactory.create_no_delegation()

    @property
    def proposal_information(self) -> ProposalInformation:
        return ProposalInformation(False)

    @property
    def is_async(self) -> bool:
        return False


class AbstractDailyTask(AbstractSimpleTask):
    # def __init__(self, config: Configurator):
    #     super().__init__(config)

    @property
    @abstractmethod
    def _market_access(self):
        pass

    _translator: VariableTranslator

    def on_exec(self, parameter: str) -> StatusCode:
        target_date: date = datetime.today().date()
        if parameter and len(parameter) == 8 and parameter.isdecimal():
            try:
                target_date = datetime.strptime(parameter, '%Y%m%d')
            except Exception:
                pass
        _translator = VariableTranslator(self._market_access)
        return self.on_daily_exec(target_date)

    @abstractmethod
    def on_daily_exec(self, target_date: date) -> StatusCode:
        pass
