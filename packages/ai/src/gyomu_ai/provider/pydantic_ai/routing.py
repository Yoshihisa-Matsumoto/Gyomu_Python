from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import NewType

from gyomu_schema.option.retry import RetryOption

from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry

ModelRouteId = NewType("ModelRouteId", str)
"""Defines a unique identifier for a model route."""

ModelRouteTableId = NewType("ModelRouteTableId", str)
"""Defines a unique identifier for a model route table."""


@dataclass
class RouteNode:
    """Represents an execution node within a model route, containing a model registry
    and retry configuration.
    """

    registry: PydanticAiModelRegistry
    """The model registry associated with this route node."""

    retry_option: RetryOption = field(
        default_factory=lambda: RetryOption(max_attempts=3)
    )
    """The retry configuration for requests handled by this route node."""


@dataclass
class ModelRoute:
    """Represents a sequence of route nodes forming a complete model routing path."""

    nodes: tuple[RouteNode, ...]
    """The tuple of route nodes that make up this model route."""


@dataclass
class ModelRoutes:
    """Container mapping model route identifiers to their corresponding model routes."""

    routes: Mapping[ModelRouteId, ModelRoute]
    """A mapping of model route identifiers to model routes."""
