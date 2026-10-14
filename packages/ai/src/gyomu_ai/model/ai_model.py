from enum import StrEnum
from typing import NewType


class AiModelKey(StrEnum):
    """Enum representing available AI model keys.

    Defines keys representing different categories of AI models.
    """

    FAST = "fast"
    """Fast model variant key."""

    SMART = "smart"
    """Smart model variant key."""

    REASONING = "reasoning"
    """Reasoning model variant key."""

    VISION = "vision"
    """Vision model variant key."""

    EMBEDDING = "embedding"
    """Embedding model variant key."""


BucketId = NewType("BucketId", str)
"""Type alias representing a unique bucket identifier.

Type alias representing a unique bucket identifier.
"""
