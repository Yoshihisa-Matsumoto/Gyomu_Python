from project_a.models import UserModel, UserSummary


def get_user(user_id: int) -> UserModel:
    """Return a user model for the given ID."""
    return UserModel(user_id=user_id, name="Example", email=None)


def summarize_user(user: UserModel) -> UserSummary:
    """Create a summary from a user model."""
    return UserSummary(
        user_id=user.user_id,
        display_name=user.name,
    )
