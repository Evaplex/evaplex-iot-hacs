from scripts.release_notes import extract_changelog_section, group_subjects, notes_for_tag, render_groups


def test_extract_changelog_section_stops_at_next_heading() -> None:
    text = """# Changelog

## 0.2.0 - 2026-09-01

### Added

- Newer item

## 0.1.0 - 2026-08-23

### Added

- Older item
"""
    section = extract_changelog_section(text, "0.1.0")
    assert section is not None
    assert "Older item" in section
    assert "Newer item" not in section


def test_group_subjects_uses_summaries_not_raw_prefix() -> None:
    grouped = group_subjects(
        [
            "feat: add cloud integration",
            "docs: add README for GitHub and HACS",
            "Merge pull request #1",
        ]
    )
    assert grouped["Added"] == ["add cloud integration"]
    assert grouped["Documentation"] == ["add README for GitHub and HACS"]
    assert "Merge pull request #1" not in grouped.get("Other", [])


def test_notes_prefer_changelog_over_commits() -> None:
    changelog = """# Changelog

## 0.1.0 - 2026-08-23

### Added

- Public HACS integration
"""
    notes = notes_for_tag("v0.1.0", changelog_text=changelog)
    assert notes.startswith("## 0.1.0")
    assert "Public HACS integration" in notes


def test_render_groups_english_headings() -> None:
    rendered = render_groups("0.1.0", {"Added": ["cloud integration"]})
    assert "### Added" in rendered
    assert "cloud integration" in rendered
