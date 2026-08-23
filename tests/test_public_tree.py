from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__"}
TEXT_SUFFIXES = {".py", ".md", ".json", ".yml", ".yaml", ".toml", ".txt"}
BADGE_MARKERS = (
    "Add to my Home Assistant",
    "my.home-assistant.io/badges",
    "my.home-assistant.io/redirect/hacs_repository",
    "hacs_repository.svg",
)


def _iter_text_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == "uv.lock":
            continue
        if path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return files


def test_no_readme_or_user_docs() -> None:
    assert not (ROOT / "README.md").exists()
    assert not (ROOT / "README.rst").exists()
    assert not (ROOT / "info.md").exists()
    assert not (ROOT / "docs").exists()


def test_no_add_to_ha_badge() -> None:
    hits: list[str] = []
    for path in _iter_text_files():
        if path.name == "test_public_tree.py":
            continue
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in BADGE_MARKERS):
            hits.append(str(path.relative_to(ROOT)))
    assert hits == []


def test_no_baked_base_url_constant() -> None:
    const_text = (ROOT / "custom_components" / "evaplex" / "const.py").read_text(encoding="utf-8")
    assert "BASE_URL" not in const_text
    assert "example.invalid" not in const_text
    assert "https://" not in const_text
    hits: list[str] = []
    for path in _iter_text_files():
        if path.name == "test_public_tree.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "BASE_URL =" in text or "BASE_URL=" in text:
            hits.append(str(path.relative_to(ROOT)))
    assert hits == []


def test_example_invalid_is_test_fixture_only() -> None:
    hits: list[str] = []
    for path in _iter_text_files():
        if "api.example.invalid" not in path.read_text(encoding="utf-8"):
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] != "tests":
            hits.append(str(rel))
    assert hits == []
