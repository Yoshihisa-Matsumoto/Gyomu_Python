from dataclasses import dataclass

import pydantic as Base

import project_b.reference_resolution.models
import project_b.reference_resolution.sub
from project_b.reference_resolution.models import LocalModel as LM


class LocalConsumer:
    pass


@dataclass
class Consumer:
    local: LocalConsumer
    imported: LM
    aliased_module: Base.BaseModel
    dotted_module_import: project_b.reference_resolution.models.LocalModel
    sub: project_b.reference_resolution.sub.SubModel
