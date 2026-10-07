from gyomu_schema.schemas.document.section import LanguageCodes


def get_readme_filename(language: LanguageCodes) -> str:
    """Returns the appropriate README filename based on the given language code.

    Args:
        language (LanguageCodes): Language code for the README file.

    Returns:
        str: The generated README filename for the specified language.
    """
    if language == "en":
        return "README.md"
    else:
        return f"README.{language}.md"
