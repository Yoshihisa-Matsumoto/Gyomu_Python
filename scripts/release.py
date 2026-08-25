import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT / "version" / "__about__.py"
DIST_DIR = ROOT / "dist"


def get_current_version() -> str:
    content = VERSION_FILE.read_text(encoding="utf-8")

    match = re.search(
        r'^__version__\s*=\s*"([^"]+)"\s*$',
        content,
        re.MULTILINE,
    )

    if match is None:
        raise RuntimeError(f"Version not found in {VERSION_FILE}")

    return match.group(1)


def set_version(version: str) -> None:
    content = VERSION_FILE.read_text(encoding="utf-8")

    updated = re.sub(
        r'^__version__\s*=\s*"[^"]+"\s*$',
        f'__version__ = "{version}"',
        content,
        count=1,
        flags=re.MULTILINE,
    )

    # if updated == content:
    #     raise RuntimeError(f"Version not found in {VERSION_FILE}")

    VERSION_FILE.write_text(updated, encoding="utf-8")


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> None:
    current_version = get_current_version()

    print(f"Current version: {current_version}")

    new_version = input("New version: ").strip()

    if not new_version:
        raise RuntimeError("Version must not be empty.")

    # if new_version == current_version:
    #     raise RuntimeError(
    #         f"New version is the same as current version: {current_version}"
    #     )

    print()
    print(f"Release: {current_version} -> {new_version}")

    pypi_version = get_pypi_version("gyomu-schema")
    print(f"PyPI Version: {pypi_version}")

    if pypi_version == new_version:
        raise RuntimeError(f"PyPI version is same as new version: {pypi_version}")

    confirm = input("Continue? [y/N]: ").strip().lower()

    if confirm != "y":
        print("Release cancelled.")
        return

    print()
    print("Updating version...")
    set_version(new_version)

    print("Cleaning dist...")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)

    print("Building packages...")
    run("uv", "build", "--all-packages")

    print("Checking distributions...")
    run("uvx", "twine", "check", *dist_files())

    print()
    print(f"Ready to upload version {new_version}.")
    confirm = input("Upload to PyPI? [y/N]: ").strip().lower()

    if confirm != "y":
        print("Build completed. Upload skipped.")
        return

    print("Uploading to PyPI...")
    run("uvx", "twine", "upload", *dist_files())

    print()
    print(f"Release {new_version} completed.")


def dist_files() -> list[str]:
    return [
        str(path)
        for path in sorted(DIST_DIR.iterdir())
        if path.is_file() and path.suffix in {".whl", ".gz"}
    ]


def get_pypi_version(package_name: str) -> str | None:
    url = f"https://pypi.org/pypi/{package_name}/json"

    try:
        with urlopen(url) as response:
            data = json.load(response)
    except Exception:
        return None

    return data["info"]["version"]


if __name__ == "__main__":
    main()
