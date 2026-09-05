"""User management module.

This module provides operations for creating and updating users.

Notes:
    User data is managed by the application service layer.

Gyomu Context:
    This module belongs to the user synchronization workflow.
    It should only be used by the application service layer.
"""

from dataclasses import dataclass


@dataclass
class User:
    name: str
