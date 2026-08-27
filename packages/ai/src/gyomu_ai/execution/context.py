from collections.abc import Mapping
from dataclasses import dataclass

from gyomu_schema.option.retry import RetryOption


@dataclass(frozen=True)
class AiModelContext:
    headers: Mapping[str, str] | None = None


@dataclass(frozen=True)
class AiExecutionContext(AiModelContext):
    temperature: float | None = None
    retry_option: RetryOption | None = None
