from textwrap import wrap

from gyomu_schema.schemas.python.docstring import (
    DocstringCustomListSection,
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


def render_docstring_lines(
    updated: UpdatedDocstring, formatter_line_length: int
) -> tuple[DocstringLine, ...]:
    lines: list[DocstringLine] = []
    docstring = updated.docstring
    target_line_length = formatter_line_length - updated.docstring.indent

    if docstring.summary is not None:
        for item in wrap_text(docstring.summary, target_line_length):
            if item == "":
                lines.append(DocstringBlank())
            else:
                lines.append(DocstringText(text=item))

    if docstring.description is not None and docstring.description != "":
        lines.append(DocstringBlank())
        for item in wrap_text(docstring.description, target_line_length):
            if item == "":
                lines.append(DocstringBlank())
            else:
                lines.append(DocstringText(text=item))

    for section in docstring.sections:
        lines.append(DocstringBlank())
        match section.kind:
            case DocstringSectionKind.ARGS:
                compute_args_tag(section, lines, docstring.style, target_line_length)
            case DocstringSectionKind.RETURNS:
                compute_returns_tag(section, lines, docstring.style, target_line_length)
            case DocstringSectionKind.RAISES:
                compute_raises_tag(section, lines, docstring.style, target_line_length)
            case DocstringSectionKind.NOTES:
                compute_notes_tag(section, lines, docstring.style)
            case DocstringSectionKind.EXAMPLES:
                compute_examples_tag(section, lines, docstring.style)
            case DocstringSectionKind.GYOMU_CONTEXT:
                compute_gyomu_context(
                    section, lines, docstring.style, target_line_length
                )
            case DocstringSectionKind.CUSTOM:
                compute_custom_tag(section, lines, docstring.style)
            case DocstringSectionKind.CUSTOM_LIST:
                compute_custom_list_tag(section, lines, docstring.style)

    return tuple(lines)


def compute_custom_list_tag(
    section: DocstringCustomListSection,
    lines: list[DocstringLine],
    style: DocstringStyle,
) -> None:
    match style:
        case DocstringStyle.GOOGLE:
            lines.append(DocstringSectionItem(text=section.title + ":"))

            for item in section.items:
                if item.name:
                    lines.append(DocstringText(text=f"    {item.name}: {item.value}"))
                else:
                    lines.append(DocstringText(text=f"    {item.value}"))


def compute_custom_tag(
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
    formatter_line_length: int,
) -> None:
    match style:
        case DocstringStyle.GOOGLE:
            lines.append(DocstringSectionItem(text="Gyomu Context:"))
            for text in wrap_docstring_item(
                section.value,
                line_length=formatter_line_length,
                first_line_indent=4,
                continuation_indent=4,
            ):
                if text == "":
                    lines.append(DocstringBlank())
                else:
                    lines.append(DocstringText(text=text))


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
    section: DocstringRaisesSection,
    lines: list[DocstringLine],
    style: DocstringStyle,
    formatter_line_length: int,
) -> None:
    if len(section.items) == 0:
        return

    lines.append(DocstringSectionItem(text=_get_raises_section_name(style)))
    for item in section.items:
        for text in _compute_raises_item(item, style, formatter_line_length):
            if text == "":
                lines.append(DocstringBlank())
            else:
                lines.append(DocstringText(text=text))


def _get_raises_section_name(style: DocstringStyle) -> str:
    match style:
        case DocstringStyle.GOOGLE:
            return "Raises:"


def _compute_raises_item(
    item: DocstringRaisesSectionItem, style: DocstringStyle, formatter_line_length: int
) -> tuple[str, ...]:
    match style:
        case DocstringStyle.GOOGLE:
            raise_type = f"{item.type}: " if item.type else ""
            return wrap_docstring_item(
                f"{raise_type}{item.description}",
                line_length=formatter_line_length,
                first_line_indent=4,
                continuation_indent=8,
            )


def compute_returns_tag(
    section: DocstringReturnsSection,
    lines: list[DocstringLine],
    style: DocstringStyle,
    formatter_line_length: int,
) -> None:
    item = section.item
    match style:
        case DocstringStyle.GOOGLE:
            lines.append(DocstringSectionItem(text="Returns:"))
            return_type = f"{item.type}: " if item.type else ""
            for text in wrap_docstring_item(
                f"{return_type}{item.description}",
                line_length=formatter_line_length,
                first_line_indent=4,
                continuation_indent=8,
            ):
                if text == "":
                    lines.append(DocstringBlank())
                else:
                    lines.append(DocstringText(text=text))


def compute_args_tag(
    section: DocstringParametersSection,
    lines: list[DocstringLine],
    style: DocstringStyle,
    formatter_line_length: int,
) -> None:
    if len(section.items) == 0:
        return

    lines.append(DocstringSectionItem(text=_get_args_section_name(style)))
    for parameter in section.items:
        for text in _compute_args_item(
            parameter=parameter,
            style=style,
            formatter_line_length=formatter_line_length,
        ):
            if text == "":
                lines.append(DocstringBlank())
            else:
                lines.append(DocstringText(text=text))


def _get_args_section_name(style: DocstringStyle) -> str:
    match style:
        case DocstringStyle.GOOGLE:
            return "Args:"


def _compute_args_item(
    parameter: DocstringParametersSectionItem,
    style: DocstringStyle,
    formatter_line_length: int,
) -> tuple[str, ...]:
    match style:
        case DocstringStyle.GOOGLE:
            param_type = f" ({parameter.type})" if parameter.type else ""
            return wrap_docstring_item(
                f"{parameter.name}{param_type}: {parameter.description}",
                line_length=formatter_line_length,
                first_line_indent=4,
                continuation_indent=8,
            )


def wrap_text(
    text: str,
    max_length: int,
) -> tuple[str, ...]:
    lines: list[str] = []

    for line in text.splitlines():
        wrapped = wrap(
            line,
            width=max_length,
            break_long_words=False,
            break_on_hyphens=False,
        )

        lines.extend(wrapped or ("",))

    return tuple(lines)


def wrap_docstring_item(
    text: str,
    *,
    line_length: int,
    first_line_indent: int,
    continuation_indent: int,
) -> tuple[str, ...]:
    lines: list[str] = []
    first_line = True

    for line in text.splitlines():
        wrapped = wrap(
            line,
            width=line_length,
            initial_indent=(
                " " * first_line_indent if first_line else " " * continuation_indent
            ),
            subsequent_indent=" " * continuation_indent,
            break_long_words=False,
            break_on_hyphens=False,
        )

        if wrapped:
            lines.extend(wrapped)
            first_line = False
        else:
            lines.append("")
            first_line = False

    return tuple(lines)
