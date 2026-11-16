from collections.abc import Callable
from typing import TextIO


def confirm_or_cancel(
    *,
    input_func: Callable[[str], str],
    output: TextIO,
) -> bool:
    """Ask the user to confirm or cancel an interaction.

    Returns:
        True if the user confirms, otherwise False.
    """
    while True:
        try:
            command = input_func("Confirm? [y/n]: ")
        except (EOFError, KeyboardInterrupt):
            return False

        normalized_command = command.strip().lower()

        if normalized_command == "y":
            return True

        if normalized_command == "n":
            return False

        print(
            "Please enter 'y' to confirm or 'n' to cancel.",
            file=output,
        )
