from pathlib import Path
from pprint import pprint

from griffe import Alias, visit


def dump_docstring(obj: object, indent: str) -> None:
    docstring = getattr(obj, "docstring", None)

    if docstring is None:
        print(f"{indent}docstring: <none>")
        return

    print(f"{indent}docstring type: {type(docstring)}")
    print(f"{indent}docstring value: {docstring.value!r}")

    for name in dir(docstring):
        if (
            "line" in name.lower()
            or "column" in name.lower()
            or "offset" in name.lower()
            or "position" in name.lower()
            or "loc" in name.lower()
        ):
            try:
                value = getattr(docstring, name)
            except Exception:
                continue

            if not callable(value):
                print(f"{indent}{name}: {value!r}")


def dump_alias(
    alias: Alias,
    indent: str,
) -> None:
    print(f"{indent}Alias: {alias.name}")
    print(f"{indent}  target_path: {alias.target_path}")
    pprint(alias)
    print(f"{indent}  is_alias: {alias.is_alias}")


def dump_object(obj: object, indent: str = "") -> None:
    if isinstance(obj, Alias):
        dump_alias(obj, indent)
        return

    print(f"{indent}{type(obj).__name__}: {getattr(obj, 'name', '<unknown>')}")

    for attr in (
        "lineno",
        "endlineno",
        # "docstring",
        "members",
        "bases",
        "parameters",
        "returns",
        "decorators",
        "annotation",
        "value",
        "kind",
    ):
        try:
            value = getattr(obj, attr)
        except AttributeError:
            continue

        print(f"{indent}  {attr}: {value!r}")

    dump_docstring(obj, indent + "    ")

    members = getattr(obj, "members", None)

    if members:
        for member in members.values():
            print()
            dump_object(member, indent + "    ")


def main() -> None:
    source_path = Path("sample.py").resolve()

    source = source_path.read_text(encoding="utf-8")

    module = visit(
        module_name="sample",
        filepath=source_path,
        code=source,
    )

    dump_object(module)


if __name__ == "__main__":
    main()
