from gyomu.user import User


class ProposalInformation:
    def __init__(self, is_required: bool):
        self.__proposal_required = is_required
        self.__destination_persons = []

    @property
    def proposal_required(self) -> bool:
        return self.__proposal_required

    @property
    def destination_persons(self) -> list[User]:
        return self.__destination_persons
