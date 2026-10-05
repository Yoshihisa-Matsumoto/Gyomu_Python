from typing import Literal

from gyomu_schema.schemas.document.section import LanguageCodes

ReadmeSectionId = Literal[
    "overview",
    "features",
    "installation",
    "requirements",
    "quick-start",
    "architecture",
    "public-api",
    "development",
    "dependencies",
    "license",
]

README_SECTION_TITLES: dict[LanguageCodes, dict[ReadmeSectionId, str]] = {
    "en": {
        "overview": "Overview",
        "features": "Features",
        "installation": "Installation",
        "public-api": "Public API",
        "quick-start": "Quick Start",
        "architecture": "Architecture",
        "dependencies": "Dependencies",
        "development": "Development",
        "license": "License",
        "requirements": "Requirements",
    },
    "ja": {
        "overview": "概要",
        "features": "機能",
        "installation": "インストール",
        "public-api": "Public API",
        "quick-start": "クイックスタート",
        "architecture": "アーキテクチャ",
        "dependencies": "依存関係",
        "development": "開発",
        "license": "ライセンス",
        "requirements": "要件",
    },
}

README_LINK: dict[LanguageCodes, str] = {
    "en": "US English",
    "ja": "JP 日本語",
}
