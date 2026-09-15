from gyomu_schema.schemas.python.docstring import (
    DocstringCustomSection,
    DocstringExamplesSection,
    DocstringGyomuContextSection,
    DocstringNotesSection,
    DocstringParametersSection,
    DocstringParametersSectionItem,
    DocstringRaisesSection,
    DocstringRaisesSectionItem,
    DocstringReturnsSection,
    DocstringSectionKind,
    DocstringStyle,
)

from gyomu_docstring.update.docstring.line import (
    DocstringBlank,
    DocstringLine,
    DocstringSectionItem,
    DocstringText,
)
from gyomu_docstring.update.docstring.updated_docstring import UpdatedDocstring


def render_docstring_lines(updated: UpdatedDocstring) -> tuple[DocstringLine, ...]:
    lines: list[DocstringLine] = []
    docstring = updated.docstring
    if docstring.summary is not None:
        lines.append(DocstringText(text=docstring.summary))

    if docstring.description is not None:
        lines.append(DocstringBlank())
        lines.append(DocstringText(text=docstring.description))

    for section in docstring.sections:
        lines.append(DocstringBlank())
        match section.kind:
            case DocstringSectionKind.ARGS:
                compute_args_tag(section, lines, docstring.style)
            case DocstringSectionKind.RETURNS:
                compute_returns_tag(section, lines, docstring.style)
            case DocstringSectionKind.RAISES:
                compute_raises_tag(section, lines, docstring.style)
            case DocstringSectionKind.NOTES:
                compute_notes_tag(section, lines, docstring.style)
            case DocstringSectionKind.EXAMPLES:
                compute_examples_tag(section, lines, docstring.style)
            case DocstringSectionKind.GYOMU_CONTEXT:
                compute_gyomu_context(section, lines, docstring.style)
            case DocstringSectionKind.CUSTOM:
                computeCustom_tag(section, lines, docstring.style)
    return tuple(lines)


def computeCustom_tag(
    section: DocstringCustomSection,
    lines: list[DocstringLine],
    style: DocstringStyle,
) -> None:
    match style:
        case DocstringStyle.GOOGLE:
            lines.append(DocstringSectionItem(text=section.title + ":"))
            lines.append(DocstringText(text=f"    {section.value}"))


def compute_gyomu_context(
    section: DocstringGyomuContextSection,
    lines: list[DocstringLine],
    style: DocstringStyle,
) -> None:
    match style:
        case DocstringStyle.GOOGLE:
            lines.append(DocstringSectionItem(text="Gyomu Context:"))
            lines.append(DocstringText(text=f"    {section.value}"))


def compute_examples_tag(
    section: DocstringExamplesSection, lines: list[DocstringLine], style: DocstringStyle
) -> None:

    match style:
        case DocstringStyle.GOOGLE:
            lines.append(DocstringSectionItem(text="Examples:"))
            for item in section.items:
                lines.append(DocstringText(text=f"    {item.value}"))
                lines.append(DocstringBlank())


def compute_notes_tag(
    section: DocstringNotesSection, lines: list[DocstringLine], style: DocstringStyle
) -> None:
    match style:
        case DocstringStyle.GOOGLE:
            lines.append(DocstringSectionItem(text="Notes:"))
            lines.append(DocstringText(text=f"    {section.value}"))


def compute_raises_tag(
    section: DocstringRaisesSection, lines: list[DocstringLine], style: DocstringStyle
) -> None:
    if len(section.items) == 0:
        return

    lines.append(DocstringSectionItem(text=_get_raises_section_name(style)))
    for item in section.items:
        lines.append(DocstringText(text=_compute_raises_item(item, style)))


def _get_raises_section_name(style: DocstringStyle) -> str:
    match style:
        case DocstringStyle.GOOGLE:
            return "Raises:"


def _compute_raises_item(
    item: DocstringRaisesSectionItem, style: DocstringStyle
) -> str:
    match style:
        case DocstringStyle.GOOGLE:
            raise_type = f"{item.type}: " if item.type else ""
            return f"    {raise_type}{item.description}"


def compute_returns_tag(
    section: DocstringReturnsSection, lines: list[DocstringLine], style: DocstringStyle
) -> None:
    item = section.item
    match style:
        case DocstringStyle.GOOGLE:
            lines.append(DocstringSectionItem(text="Returns:"))
            return_type = f"{item.type}: " if item.type else ""
            lines.append(DocstringText(text=f"    {return_type}{item.description}"))


def compute_args_tag(
    section: DocstringParametersSection,
    lines: list[DocstringLine],
    style: DocstringStyle,
) -> None:
    if len(section.items) == 0:
        return

    lines.append(DocstringSectionItem(text=_get_args_section_name(style)))
    for parameter in section.items:
        lines.append(
            DocstringText(text=_compute_args_item(parameter=parameter, style=style))
        )


def _get_args_section_name(style: DocstringStyle) -> str:
    match style:
        case DocstringStyle.GOOGLE:
            return "Args:"


def _compute_args_item(
    parameter: DocstringParametersSectionItem, style: DocstringStyle
) -> str:
    match style:
        case DocstringStyle.GOOGLE:
            param_type = f" ({parameter.type})" if parameter.type else ""
            return f"    {parameter.name}{param_type}: {parameter.description}"
