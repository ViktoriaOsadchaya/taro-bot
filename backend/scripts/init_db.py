"""
Применение миграций Alembic (обёртка для удобства).

Рекомендуемый способ:
    alembic upgrade head

Этот скрипт делает то же самое.

Перед запуском:
    docker compose up -d
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    backend_dir = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=backend_dir,
        check=True,
    )
    print("Миграции применены (alembic upgrade head).")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(exc.returncode)
