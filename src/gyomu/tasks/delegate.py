from gyomu.user import User


class DelegateInformation:

    def __init__(self, delegation_required: bool, delegation_users: list[User]):
        self.__delegation_required = delegation_required
        self.__delegation_users = delegation_users

    @property
    def delegation_required(self) -> bool:
        return self.__delegation_required

    @property
    def delegation_users(self) -> list[User]:
        return self.__delegation_users


class DelegateInformationFactory:

    @staticmethod
    def create_no_delegation() -> DelegateInformation:
        return DelegateInformation(False, None)

    @staticmethod
    def create_delegation(delegate_to: list[User]) -> DelegateInformation:
        return DelegateInformation(True, delegate_to)
