import ast
import re
from textwrap import dedent

from griffe import (
    Docstring,
    DocstringNamedElement,
    DocstringSectionAdmonition,
    DocstringSectionKind,
)
from griffe import DocstringSection as GriffeSection
from griffe import DocstringSectionExamples as GriffeSectionExamples
from griffe import DocstringSectionParameters as GriffeSectionParameters
from griffe import DocstringSectionRaises as GriffeSectionRaises
from griffe import DocstringSectionReturns as GriffeSectionReturns
from griffe import (
    DocstringSectionText as GriffeSectionText,
)
from gyomu_infra.logger import logger
from gyomu_schema.schemas.python.docstring import (
    DocstringAnalysis,
    DocstringCustomSection,
    DocstringExamplesSection,
    DocstringExamplesSectionItem,
    DocstringGyomuContextSection,
    DocstringNotesSection,
    DocstringParametersSection,
    DocstringParametersSectionItem,
    DocstringRaisesSection,
    DocstringRaisesSectionItem,
    DocstringReturnsSection,
    DocstringReturnsSectionItem,
    DocstringSection,
    DocstringStyle,
    DocstringTextSection,
)

_CUSTOM_SECTION_PATTERN = re.compile(r"^(?P<name>[A-Za-z][A-Za-z0-9 _-]*):\s*$")

from gyomu_python_analysis.analysis.analyzers.internal.common import (
    build_docstring_common,
)
from gyomu_python_analysis.analysis.analyzers.types import analyze_type


def _analyze_parameters(section: GriffeSectionParameters) -> DocstringParametersSection:
    parameters: list[DocstringParametersSectionItem] = []
    for parameter in section.value:
        param_type = analyze_type(parameter.annotation)
        parameters.append(
            DocstringParametersSectionItem(
                name=parameter.name,
                description=parameter.description,
                type=param_type if param_type is None else param_type.text,
            )
        )
    return DocstringParametersSection(items=tuple(parameters))


def _analyze_raises(section: GriffeSectionRaises) -> DocstringRaisesSection:
    raises: list[DocstringRaisesSectionItem] = []
    for raiseItem in section.value:
        raise_type = analyze_type(raiseItem.annotation)
        raises.append(
            DocstringRaisesSectionItem(
                description=raiseItem.description,
                type=raise_type if raise_type is None else raise_type.text,
            )
        )
    return DocstringRaisesSection(items=tuple(raises))


def _analyze_examples(section: GriffeSectionExamples) -> DocstringExamplesSection:
    examples: list[DocstringExamplesSectionItem] = []
    for exampleItem in section.value:
        for item in exampleItem:
            item_text: str
            if (
                isinstance(item, str)
                and item is not DocstringSectionKind.text
                and item is not DocstringSectionKind.examples
            ):
                item_text = item
                examples.append(DocstringExamplesSectionItem(value=item_text))
    return DocstringExamplesSection(items=tuple(examples))


def _analyze_returns(section: GriffeSectionReturns) -> DocstringReturnsSection:
    # Gyomu models a Returns section as a single item.
    # Google-style docstrings are expected to contain at most one return item.
    if len(section.value) > 1:
        logger.warning(
            "Multiple return items are not supported; using the first item: %r",
            section.value,
        )

    return_item = section.value[0]
    print(return_item.as_dict())
    return_type = analyze_type(return_item.annotation)

    return DocstringReturnsSection(
        item=DocstringReturnsSectionItem(
            description=_extract_return_description(return_item.description),
            type=return_type.text if return_type is not None else None,
        )
    )


def _extract_return_description(description: str) -> str:
    description = description.strip()

    if ":" not in description:
        return description

    type_text, return_description = description.split(":", 1)
    type_text = type_text.strip()
    return_description = return_description.strip()

    if not _looks_like_type(type_text):
        return description

    return return_description


def _looks_like_type(text: str) -> bool:
    try:
        ast.parse(text, mode="eval")
        return True
    except SyntaxError:
        return False


def _analyze_admonition(section: DocstringSectionAdmonition) -> DocstringSection:
    return _parse_custom_section(title=section.title, value=section.value.description)


def _parse_custom_section(title: str | None, value: str) -> DocstringSection:
    if title == "Notes":
        return DocstringNotesSection(value=value)
    elif title == "Gyomu Context":
        return DocstringGyomuContextSection(value=value)
    else:
        return DocstringCustomSection(
            title=title if title is not None else "",
            value=value,
        )


def _is_indented(line: str) -> bool:
    return bool(line) and line[0].isspace()


def parse_text_section(
    text: str,
) -> tuple[str, str, list[DocstringSection]]:
    lines = text.splitlines()

    while lines and not lines[0].strip():
        lines.pop(0)

    while lines and not lines[-1].strip():
        lines.pop()

    if not lines:
        return "", "", []

    # First paragraph = summary.
    summary_lines: list[str] = []

    index = 0
    while index < len(lines) and lines[index].strip():
        summary_lines.append(lines[index])
        index += 1

    summary = "\n".join(summary_lines).strip()

    # Skip blank lines between summary and the rest.
    while index < len(lines) and not lines[index].strip():
        index += 1

    description_lines: list[str] = []
    custom_sections: list[DocstringSection] = []

    while index < len(lines):
        match = _CUSTOM_SECTION_PATTERN.match(lines[index])

        if match and index + 1 < len(lines) and _is_indented(lines[index + 1]):
            name = match.group("name")
            index += 1

            section_lines: list[str] = []

            while index < len(lines):
                if (
                    _CUSTOM_SECTION_PATTERN.match(lines[index])
                    and index + 1 < len(lines)
                    and _is_indented(lines[index + 1])
                ):
                    break

                section_lines.append(lines[index])
                index += 1

            section_text = "\n".join(section_lines)
            section_text = dedent(section_text).strip()

            custom_sections.append(
                _parse_custom_section(
                    title=name,
                    value=section_text,
                )
            )
            continue

        description_lines.append(lines[index])
        index += 1

    description = "\n".join(description_lines).strip()

    return summary, description, (custom_sections)


def analyze_docstring(
    doc: Docstring | None,
    source_lines: list[str],
) -> DocstringAnalysis | None:
    if doc is None:
        return None
    doc_common = build_docstring_common(
        doc=doc,
        source_lines=source_lines,
    )
    # print(doc.source)
    sections = doc.parse(parser="auto")

    text_section: DocstringTextSection | None = None
    parsed_sections: list[DocstringSection] = []
    for section in sections:
        if isinstance(section, GriffeSectionText):
            text_section = DocstringTextSection(value=section.value)
        elif isinstance(section, GriffeSectionParameters):
            parsed_sections.append(_analyze_parameters(section))
        elif isinstance(section, GriffeSectionRaises):
            parsed_sections.append(_analyze_raises(section))
        elif isinstance(section, GriffeSectionExamples):
            parsed_sections.append(_analyze_examples(section))
        elif isinstance(section, GriffeSectionReturns):
            parsed_sections.append(_analyze_returns(section))
        elif isinstance(section, DocstringSectionAdmonition):
            parsed_sections.append(_analyze_admonition(section))
        else:
            print("Unknown Section in Docstring")
            value = section.value
            if isinstance(value, str):
                print(section.as_dict())
            elif isinstance(value, list):
                for item in value:
                    print(f"Kind: {section.kind}, item is list")
                    if isinstance(
                        item,
                        (GriffeSection, DocstringNamedElement, GriffeSectionRaises),
                    ):
                        print(item.as_dict())
                    else:
                        print(item)
            else:
                print(section.as_dict())
    if text_section:
        summary, description, sections2 = parse_text_section(text_section.value)
        return DocstringAnalysis(
            **doc_common,
            raw=doc.source,
            summary=None if summary == "" else summary,
            description=None if description == "" else description,
            sections=tuple(parsed_sections if len(parsed_sections) > 0 else sections2),
            style=DocstringStyle.GOOGLE,
        )
    return DocstringAnalysis(
        **doc_common,
        raw=doc.source,
        summary=None,
        description=None,
        sections=tuple(parsed_sections),
        style=DocstringStyle.GOOGLE,
    )
