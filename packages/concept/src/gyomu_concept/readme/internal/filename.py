from gyomu_schema.schemas.document.section import LanguageCodes


def get_readme_filename(language: LanguageCodes) -> str:
    if language == "en":
        return "README.md"
    else:
        return f"README.{language}.md"
