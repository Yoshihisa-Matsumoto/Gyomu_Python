from project_b.class_hierarchy.base import Base


class Left(Base):
    """Left branch."""


class Right(Base):
    """Right branch."""


class Diamond(Left, Right):
    """Diamond inheritance."""
