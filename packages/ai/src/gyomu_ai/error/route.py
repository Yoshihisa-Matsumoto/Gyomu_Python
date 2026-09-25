from collections.abc import Mapping

from gyomu_ai.provider.pydantic_ai.routing import ModelRouteId, ModelRouteTableId
from gyomu_schema.error.base import BaseError


class RoutingError(BaseError):
    def __init__(
        self,
        message: str,
        *,
        route_id: ModelRouteId | None,
        route_table_id: ModelRouteTableId | None,
        context: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            message,
            context=context,
            details=details,
        )
        self.table_id = route_table_id
        self.route_id = route_id
