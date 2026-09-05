class User:
    """User model.

    This class represents a user in the application.

    Notes:
        User instances are managed by the application service layer.

    Gyomu Context:
        This class is used by the user synchronization workflow.
        It should only be created by the application service layer.
    """

    name: str
    """The user's name."""

    active: bool
    """Whether the user is active."""

    def __init__(
        self,
        name: str,
        active: bool = True,
    ) -> None:
        """Initialize a user.

        Args:
            name (str): The user's name.
            active (bool): Whether the user is active.

        Notes:
            The user is active by default.
        """
        self.name = name
        self.active = active

    def activate(self) -> None:
        """Activate the user.

        This method marks the user as active.

        Returns:
            None.

        Gyomu Context:
            This method is used during the user synchronization workflow.
        """
        self.active = True

    def deactivate(self) -> None:
        """Deactivate the user.

        This method marks the user as inactive.

        Notes:
            Deactivated users are not synchronized.
        """
        self.active = False
