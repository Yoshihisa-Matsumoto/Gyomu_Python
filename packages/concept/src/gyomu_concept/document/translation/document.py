from dataclasses import dataclass

from gyomu_schema.schemas.document.section import LanguageCodes, Section


@dataclass
class TranslatedDocument[TSectionId: str]:
    """Represents a translated document containing a language code and a tuple of
    sections.

    Represents a translated document in a specific language, containing a collection of
    sections.
    """

    language: LanguageCodes
    sections: tuple[Section[TSectionId], ...]
