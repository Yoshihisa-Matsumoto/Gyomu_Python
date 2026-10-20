from project_b.class_hierarchy.base import UnresolvedSymbol
from project_b.class_hierarchy.intermediate import Intermediate

NotClass = 1.0


class DerivedFromUnknown(UnknownBase):
    """Class whose base class cannot be resolved."""


class DerivedFromUnknown3(UnresolvedSymbol):
    """Class whose base class cannot be resolved."""


class DerivedFromUnknown4(NotClass):
    """Class whose base class cannot be resolved."""


class DerivedFromUnknown5(NonExistence):
    """Class whose base class cannot be resolved."""


class MixedUnknown(UnknownBase, Intermediate):
    """Class whose base class cannot be resolved."""
