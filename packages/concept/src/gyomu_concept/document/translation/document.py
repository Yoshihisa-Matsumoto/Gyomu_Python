from dataclasses import dataclass

from gyomu_schema.schemas.document.section import LanguageCodes, Section


@dataclass
class TranslatedDocument:
    language: LanguageCodes
    sections: tuple[Section, ...]
