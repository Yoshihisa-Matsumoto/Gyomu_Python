from gyomu.tasks.abstract_base_task import AbstractBaseTask
from gyomu.tasks.delegate import DelegateInformation, DelegateInformationFactory
from gyomu.tasks.proposal import ProposalInformation
from gyomu.status_code import StatusCode

class AbstractSimpleTask(AbstractBaseTask):
    @property
    def delegate_information(self) -> DelegateInformation:
        return DelegateInformationFactory.create_no_delegation()

    @property
    def proposal_information(self) -> ProposalInformation:
        return ProposalInformation(False)


