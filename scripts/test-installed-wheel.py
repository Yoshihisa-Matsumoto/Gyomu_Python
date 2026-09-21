from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PACKAGE_TESTS = Path("packages/ai-compiler/tests/integration")


def run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> None:
    print(f"$ {' '.join(command)}")
    subprocess.run(command, cwd=cwd, env=env, check=True)


def get_uv_command() -> str:
    uv = shutil.which("uv")
    if uv is None:
        raise RuntimeError("uv was not found in PATH")

    return uv


def get_venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"

    return venv_dir / "bin" / "python"


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    uv = get_uv_command()

    test_path = repo_root / PACKAGE_TESTS
    if not test_path.is_dir():
        raise RuntimeError(f"Package test directory was not found: {test_path}")

    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    with tempfile.TemporaryDirectory(prefix="gyomu-wheel-test-") as temp:
        temp_dir = Path(temp)
        wheel_dir = temp_dir / "wheels"
        venv_dir = temp_dir / "venv"

        wheel_dir.mkdir()

        print(f"Temporary directory: {temp_dir}")

        # 1. Build all workspace packages as wheels.
        run(
            [
                uv,
                "build",
                "--all-packages",
                "--wheel",
                "--out-dir",
                str(wheel_dir),
            ],
            cwd=repo_root,
            env=env,
        )

        wheels = sorted(wheel_dir.glob("*.whl"))
        if not wheels:
            raise RuntimeError(f"No wheels were built in: {wheel_dir}")

        print("Built wheels:")
        for wheel in wheels:
            print(f"  {wheel.name}")

        # 2. Create an independent virtual environment.
        run(
            [
                uv,
                "venv",
                str(venv_dir),
            ],
            cwd=repo_root,
            env=env,
        )

        venv_python = get_venv_python(venv_dir)

        if not venv_python.is_file():
            raise RuntimeError(
                f"Virtual environment Python was not found: {venv_python}"
            )

        # 3. Install the built wheels and pytest into the independent environment.
        run(
            [
                uv,
                "pip",
                "install",
                "--python",
                str(venv_python),
                "pytest",
                *[str(wheel) for wheel in wheels],
            ],
            cwd=temp_dir,
            env=env,
        )

        # Verify that the package is imported from the independent environment.
        run(
            [
                str(venv_python),
                "-c",
                ("import gyomu_ai_compiler; print(gyomu_ai_compiler.__file__)"),
            ],
            cwd=temp_dir,
            env=env,
        )

        # 4. Run only package tests using the independent environment.
        run(
            [
                str(venv_python),
                "-m",
                "pytest",
                str(test_path),
                "-m",
                "package",
                "--import-mode=importlib",
            ],
            cwd=temp_dir,
            env=env,
        )


if __name__ == "__main__":
    main()
