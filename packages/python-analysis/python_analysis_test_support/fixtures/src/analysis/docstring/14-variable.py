"""Variable analysis fixture.

This module contains various kinds of variables for analysis.

Notes:
    Variables are used to represent application configuration and state.

Gyomu Context:
    This module is used by the configuration loading workflow.
"""

# Simple variable
name = "Alice"


# Annotated variable
age: int = 30


# Variable without an initial value
active: bool


# Constant-like variable
MAX_RETRY: int = 3


# Variable with a generic type
users: list[str] = []


# Variable with a docstring
description = "A user description."
"""Description of the user.

This variable contains the human-readable description.

Notes:
    The description is displayed to users.
"""


# Variable with an annotation and a docstring
status: str = "active"
"""Current user status.

Gyomu Context:
    This value is updated during user synchronization.
"""
