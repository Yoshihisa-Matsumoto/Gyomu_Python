from gyomu.user_factory import UserFactory
from gyomu.user import User


def test_get_current_user():
    user: User = UserFactory.get_current_user()
    assert user is not None
    assert user.user_id is not None and user.user_id != ""
    print(user.userid)
