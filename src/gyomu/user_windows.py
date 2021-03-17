from gyomu.user import User


class _WindowsUser(User):
    _groups = []
    _is_group_initialized = False
    user_id: str

    def get_groups(self):
        if not self._is_group_initialized:
            self._init_group()
        return self._groups

    def is_group(self) -> bool:
        pass

    def is_valid(self) -> bool:
        pass

    def get_members(self):
        pass

    def get_userid(self):
        return self.user_id

    def is_in_member(self, group_user: User) -> bool:
        pass

    def _init_group(self):
        pass

    def __init__(self, user_id: str):
        self.user_id=user_id
