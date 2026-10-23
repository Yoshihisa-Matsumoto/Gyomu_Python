from collections.abc import Mapping

from gyomu_schema.error.base import BaseError, caller_context

from gyomu_ai.provider.pydantic_ai.routing import ModelRouteId, ModelRouteTableId


class RoutingError(BaseError):
    """Raised when a model routing or route table operation fails."""

    def __init__(
        self,
        message: str,
        *,
        route_id: ModelRouteId | None,
        route_table_id: ModelRouteTableId | None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=caller_context(),
            details=details,
        )
        self.table_id = route_table_id
        self.route_id = route_id
