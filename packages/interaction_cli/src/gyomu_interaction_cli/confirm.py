from questionary import confirm


def confirm_or_cancel() -> bool:
    """Ask the user to confirm or cancel an interaction.

    Returns:
        True if the user confirms, otherwise False.
    """
    try:
        result = confirm("Confirm?").ask()
    except (EOFError, KeyboardInterrupt):
        return False

    return result is True
