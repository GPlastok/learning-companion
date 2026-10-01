import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILE = REPO_ROOT / "learning_companion" / "settings.py"

SCRIPT = """
import json
from django.conf import settings

print(json.dumps({
    "SECRET_KEY": settings.SECRET_KEY,
    "DEBUG": settings.DEBUG,
    "ENGINE": settings.DATABASES["default"]["ENGINE"],
    "NAME": str(settings.DATABASES["default"]["NAME"]),
    "OPENAI_API_KEY": getattr(settings, "OPENAI_API_KEY", None),
}))
"""


def load_settings(tmp_path, **env):
    """Load learning_companion.settings in a fresh process with only the given env."""
    process_env = {
        "PATH": os.environ["PATH"],
        "DJANGO_SETTINGS_MODULE": "learning_companion.settings",
        "ENV_FILE": str(tmp_path / ".env"),
        **env,
    }
    process = subprocess.run(
        [sys.executable, "-c", SCRIPT],
        cwd=REPO_ROOT,
        env=process_env,
        capture_output=True,
        check=False,
        text=True,
    )
    values = json.loads(process.stdout) if process.returncode == 0 else None
    return process, values


@pytest.mark.parametrize("source", ["environment", "env_file"])
def test_ac5_reads_settings(tmp_path, source):
    variables = {
        "SECRET_KEY": "from-test",
        "DEBUG": "False",
        "DATABASE_URL": f"sqlite:///{tmp_path}/a.sqlite3",
        "OPENAI_API_KEY": "sk-test",
    }
    if source == "environment":
        _, values = load_settings(tmp_path, **variables)
    else:
        lines = [f"{name}={value}" for name, value in variables.items()]
        (tmp_path / ".env").write_text("\n".join(lines) + "\n")
        _, values = load_settings(tmp_path)

    assert values["SECRET_KEY"] == "from-test"
    assert values["DEBUG"] is False
    assert values["NAME"] == f"{tmp_path}/a.sqlite3"
    assert values["OPENAI_API_KEY"] == "sk-test"


def test_ac5_settings_hard_code_no_secret():
    assert "django-insecure" not in SETTINGS_FILE.read_text()


def test_ac6_sqlite_url_configures_database(tmp_path):
    _, values = load_settings(
        tmp_path,
        SECRET_KEY="x",
        DATABASE_URL=f"sqlite:///{tmp_path}/b.sqlite3",
    )

    assert values["ENGINE"] == "django.db.backends.sqlite3"
    assert values["NAME"] == f"{tmp_path}/b.sqlite3"
    assert '"ENGINE"' not in SETTINGS_FILE.read_text()


def test_ac14_missing_secret_key_fails(tmp_path):
    process, _ = load_settings(tmp_path)

    assert process.returncode != 0
    assert "SECRET_KEY" in process.stderr


def test_ac15_defaults(tmp_path):
    _, values = load_settings(tmp_path, SECRET_KEY="x")

    assert values["NAME"] == str(REPO_ROOT / "db.sqlite3")
    assert values["DEBUG"] is True
    assert values["OPENAI_API_KEY"] == ""
