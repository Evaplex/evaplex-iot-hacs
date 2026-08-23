"""Assemble GitHub Release notes from CHANGELOG.md or conventional commit subjects."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
SUBJECT_RE = re.compile(r"^(?P<type>[a-zA-Z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s+(?P<summary>.+)$")
SECTION_RE = re.compile(r"^##[ \t]+(?:\[)?v?(?P<version>\d+\.\d+\.\d+)(?:\])?(?:[ \t].*)?$", re.MULTILINE)
GROUP_TITLES = {
    "feat": "Added",
    "fix": "Fixed",
    "docs": "Documentation",
    "perf": "Performance",
    "refactor": "Changed",
    "test": "Tests",
    "ci": "CI",
    "build": "Build",
    "chore": "Maintenance",
}
SKIP_TYPES = {"revert"}
TAG_RE = re.compile(r"^v?\d+\.\d+\.\d+$")


def normalize_tag(value: str) -> str:
    raw = value.strip()
    if raw.startswith("refs/tags/"):
        raw = raw.removeprefix("refs/tags/")
    if not TAG_RE.match(raw):
        raise ValueError(f"expected semver tag vX.Y.Z, got {value!r}")
    return raw if raw.startswith("v") else f"v{raw}"


def version_from_tag(tag: str) -> str:
    return normalize_tag(tag).removeprefix("v")


def extract_changelog_section(text: str, version: str) -> str | None:
    matches = list(SECTION_RE.finditer(text))
    for index, match in enumerate(matches):
        if match.group("version") != version:
            continue
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        return text[start:end].strip()
    return None


def parse_subject(subject: str) -> tuple[str, str] | None:
    match = SUBJECT_RE.match(subject.strip())
    if match is None:
        return None
    commit_type = match.group("type").lower()
    if commit_type in SKIP_TYPES:
        return None
    return commit_type, match.group("summary").strip()


def group_subjects(subjects: list[str]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for subject in subjects:
        parsed = parse_subject(subject)
        if parsed is None:
            continue
        commit_type, summary = parsed
        title = GROUP_TITLES.get(commit_type, "Other")
        if summary not in grouped[title]:
            grouped[title].append(summary)
    return grouped


def render_groups(version: str, grouped: dict[str, list[str]]) -> str:
    lines = [f"## {version}", ""]
    if not grouped:
        lines.append("No conventional commit subjects for this tag.")
        lines.append("")
        return "\n".join(lines).strip()
    order = (
        "Added",
        "Fixed",
        "Changed",
        "Performance",
        "Documentation",
        "Tests",
        "CI",
        "Build",
        "Maintenance",
        "Other",
    )
    for title in order:
        items = grouped.get(title)
        if not items:
            continue
        lines.append(f"### {title}")
        lines.append("")
        lines.extend(f"- {item}" for item in items)
        lines.append("")
    return "\n".join(lines).strip()


def git_output(args: list[str]) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def commit_subjects(tag: str) -> list[str]:
    current = normalize_tag(tag)
    names = [
        line
        for line in git_output(["tag", "--list", "--sort=version:refname", "v*.*.*"]).splitlines()
        if TAG_RE.match(line)
    ]
    previous = None
    if current in names:
        index = names.index(current)
        if index > 0:
            previous = names[index - 1]
    else:
        previous = names[-1] if names else None
    rev_range = f"{previous}..{current}" if previous else current
    log = git_output(["log", "--no-merges", "--format=%s", rev_range])
    return [line.strip() for line in log.splitlines() if line.strip()]


def notes_for_tag(tag: str, changelog_text: str | None = None) -> str:
    version = version_from_tag(tag)
    text = CHANGELOG.read_text(encoding="utf-8") if changelog_text is None and CHANGELOG.is_file() else changelog_text
    if text:
        section = extract_changelog_section(text, version)
        if section:
            return section
    return render_groups(version, group_subjects(commit_subjects(tag)))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", default="", help="Release tag (vX.Y.Z). Defaults to GITHUB_REF_NAME or latest tag.")
    args = parser.parse_args(argv)
    tag = args.tag.strip()
    if not tag:
        tag = os.environ.get("GITHUB_REF_NAME", "").strip()
    if not tag:
        listed = git_output(["tag", "--list", "--sort=version:refname", "v*.*.*"])
        tag = listed.splitlines()[-1] if listed else ""
    if not tag:
        print("no semver tag; pass --tag vX.Y.Z", file=sys.stderr)
        return 2
    print(notes_for_tag(tag))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
