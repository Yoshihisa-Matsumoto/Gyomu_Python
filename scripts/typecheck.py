from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def collect_source_dirs() -> list[Path]:
    """Collect src roots from packages and apps."""
    return sorted(
        path
        for parent in (ROOT / "packages", ROOT / "apps")
        if parent.exists()
        for path in parent.glob("*/src")
        if path.is_dir()
    )


def collect_test_support_files() -> list[Path]:
    """Collect Python files directly under each test_support directory."""
    return sorted(
        file
        for parent in (ROOT / "packages", ROOT / "apps")
        if parent.exists()
        for support_dir in parent.glob("*/test_support")
        if support_dir.is_dir()
        for file in support_dir.glob("*.py")
        if file.is_file()
    )


def collect_test_dirs() -> list[Path]:
    """Collect tests directories recursively under each package."""
    return sorted(
        path
        for parent in (ROOT / "packages", ROOT / "apps")
        if parent.exists()
        for path in parent.glob("*/tests")
        if path.is_dir()
    )


def run_mypy(
    paths: list[Path],
    *,
    config_file: str,
    group_name: str,
    explicit_package_bases: bool = False,
    monorepo_path: bool = False,
) -> bool:
    if not paths:
        return True

    env = os.environ.copy()
    if monorepo_path:
        env["MYPYPATH"] = str(ROOT)

    cache_dir = ROOT / ".mypy_cache" / group_name

    command = [
        sys.executable,
        "-m",
        "mypy",
        "--config-file",
        str(ROOT / config_file),
        "--cache-dir",
        str(cache_dir),
    ]

    if explicit_package_bases:
        command.append("--explicit-package-bases")

    command.extend(str(path) for path in paths)

    result = subprocess.run(command, cwd=ROOT, env=env, check=False)
    return result.returncode == 0


def main() -> int:
    checks = [
        (
            "src",
            collect_source_dirs(),
            "pyproject.toml",
            False,
            False,
        ),
        (
            "test_support",
            collect_test_support_files(),
            "pyproject.toml",
            True,
            True,
        ),
        (
            "tests",
            collect_test_dirs(),
            "mypy-tests.ini",
            True,
            True,
        ),
    ]

    failed: list[str] = []

    for name, paths, config, explicit_bases, monorepo_path in checks:
        print(f"\n=== mypy: {name} ===", flush=True)

        if not run_mypy(
            paths,
            config_file=config,
            explicit_package_bases=explicit_bases,
            monorepo_path=monorepo_path,
            group_name=name,
        ):
            failed.append(name)

    if failed:
        print(f"\nFailed checks: {', '.join(failed)}")
        return 1

    print("\nAll mypy checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
