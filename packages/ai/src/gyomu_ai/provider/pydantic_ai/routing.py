from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import NewType

from gyomu_ai.provider.pydantic_ai.ai_model import PydanticAiModelRegistry
from gyomu_schema.option.retry import RetryOption

ModelRouteId = NewType("ModelRouteId", str)
ModelRouteTableId = NewType("ModelRouteTableId", str)


@dataclass
class RouteNode:
    registry: PydanticAiModelRegistry
    retry_option: RetryOption = field(
        default_factory=lambda: RetryOption(max_attempts=3)
    )


@dataclass
class ModelRoute:
    nodes: tuple[RouteNode, ...]


@dataclass
class ModelRoutes:
    routes: Mapping[ModelRouteId, ModelRoute]
