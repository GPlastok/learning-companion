import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def makefile_targets(makefile):
    return set(re.findall(r"^([a-z][a-z-]*):", makefile, re.MULTILINE))


def documented_targets(claude_md):
    commands = claude_md.split("## Commands", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"`make ([a-z][a-z-]*)[` ]", commands))


def undocumented_targets(makefile, claude_md):
    return makefile_targets(makefile) - documented_targets(claude_md)


def test_ac11_claude_md_commands_match_makefile():
    makefile = (REPO_ROOT / "Makefile").read_text()
    claude_md = (REPO_ROOT / "CLAUDE.md").read_text()

    assert undocumented_targets(makefile, claude_md) == set()
    assert documented_targets(claude_md) <= makefile_targets(makefile)
    assert "Added by the scaffold ticket" not in claude_md


def test_ac11_target_counts_only_in_commands_table():
    makefile = "dev:\n\techo\n"
    claude_md = (
        "## Commands\n\n| `make dev-server` | x |\n\n## Other\n\nRun `make dev`.\n"
    )

    assert undocumented_targets(makefile, claude_md) == {"dev"}
