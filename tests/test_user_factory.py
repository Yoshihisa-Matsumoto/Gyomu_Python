from src import gyomu


def test_get_current_user():
    user: gyomu.user.User = src.gyomu.user_factory.UserFactory.get_current_user()
    assert user is not None
    assert user.user_id is not None and user.user_id != ""
