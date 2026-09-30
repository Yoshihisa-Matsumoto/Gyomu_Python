from dataclasses import dataclass

from gyomu_schema.schemas.document.section import Section
from gyomu_schema.schemas.document.translation import LanguageCodes


@dataclass
class TranslatedDocument:
    language: LanguageCodes
    sections: tuple[Section, ...]
