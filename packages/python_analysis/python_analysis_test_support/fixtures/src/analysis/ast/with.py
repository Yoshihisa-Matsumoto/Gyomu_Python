from pathlib import Path


def simple_with(path: Path) -> str:
    with path.open("r") as file:
        return file.read()


def with_as(path: Path) -> str:
    with path.open("r") as file:
        content = file.read()
    return content


def with_multiple(path1: Path, path2: Path) -> str:
    with path1.open("r") as file1, path2.open("r") as file2:
        return file1.read() + file2.read()


def with_without_as(path: Path) -> None:
    with path.open("r"):
        pass


def nested_with(path1: Path, path2: Path) -> str:
    with path1.open("r") as file1:
        with path2.open("r") as file2:
            return file1.read() + file2.read()


def with_multiple_statements(path: Path) -> str:
    with path.open("r") as file:
        content = file.read()
        content = content.strip()
        return content
