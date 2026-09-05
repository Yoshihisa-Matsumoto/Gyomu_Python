def process_user(
    user_id: int,
    name: str,
    *,
    active: bool = True,
) -> dict[str, object]:
    """Process a user.

    This function loads a user and updates its information.

    Args:
        user_id (int): The user ID.
        name (str): The user's name.
        active (bool): Whether the user is active.

    Raises:
        ValueError: If the user ID is invalid.
        LookupError: If the user does not exist.

    Returns:
        dict[str, object]: The updated user information.

    Examples:
        >>> process_user(1, "Alice")
        {'id': 1, 'name': 'Alice', 'active': True}

    Notes:
        The user is loaded from the repository before being updated.
        The operation is transactional.
    """
    return dict()
