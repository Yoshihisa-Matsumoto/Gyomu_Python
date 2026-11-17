import subprocess
from pathlib import Path

from dotenv import load_dotenv
from gyomu_schema.config.config_loader_option import EnvironmentLoaderOption
from gyomu_schema.db.config import DbConfig

from gyomu_infra.config.loader import ConfigLoader

load_dotenv()

TABLES = ("gyomu_param_master", "gyomu_market_holiday")

OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "gyomu_infra"
    / "db"
    / "model"
    / "generated"
)


def main() -> None:
    config = ConfigLoader.load(
        DbConfig,
        EnvironmentLoaderOption(
            use_dot_env=True,
            dot_env_path=Path("../../../.env"),
            variables={"GYOMU_COMMON_MAINDB_CONNECTION": "connection_string"},
        ),
    ).unwrap()
    connection_string = config.connection_string

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    command = [
        "sqlacodegen",
        connection_string,
        "--tables",
        ",".join(TABLES),
    ]

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    output_file = OUTPUT_DIR / "models.py"
    output_file.write_text(result.stdout, encoding="utf-8")


if __name__ == "__main__":
    main()
