from gyomu_docstring.update.docstring.line import (
    DocstringBlank,
    DocstringLine,
    DocstringSectionItem,
    DocstringText,
)


def render_docstring_string(
    lines: tuple[DocstringLine, ...],
    is_added: bool,
    indent: int,
) -> str | None:
    if not lines:
        return None

    prefix = " " * indent

    if _is_single_line_docstring(lines):
        assert lines[0].type == "text"
        text = lines[0].text
        result = f'{prefix}"""{text}"""'
    else:
        first_line = compute_docstring_line(lines[0], prefix)
        start = f'{prefix}"""{first_line.removeprefix(prefix)}'

        string_lines = [
            start,
            *(compute_docstring_line(line, prefix) for line in lines[1:]),
            f'{prefix}"""',
        ]

        result = "\n".join(string_lines)

    if is_added:
        result += "\n"

    return result


def compute_docstring_line(
    line: DocstringLine,
    prefix: str,
) -> str:
    match line:
        case DocstringBlank():
            return prefix

        case DocstringText(text=text):
            return "\n".join(f"{prefix}{part}" for part in text.split("\n"))

        case DocstringSectionItem(text=text):
            return "\n".join(f"{prefix}{part}" for part in text.split("\n"))


def _is_single_line_docstring(
    lines: tuple[DocstringLine, ...],
) -> bool:
    return (
        len(lines) == 1
        and isinstance(lines[0], DocstringText)
        and "\n" not in lines[0].text
    )
