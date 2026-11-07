"""Self-check of a verification map against the app it describes.

Copy to `.claude/skills/verify-<app>/scripts/selfcheck.py` and fill in the
block marked FILL IN; everything below it is generic.  Keep the exit codes and
the flags, because the plans, the task-runner recipe, and the pre-commit hook
depend on them.

A feature map rots the moment the app changes, and a plan can land a
user-facing change without touching it.  This script says when that has
happened, without launching anything:

  integrity   every feature file is indexed in features/README.md and keeps the
              four-section shape, its Status and Sources lines parse, its
              sub-feature ids are unique, every steps file it names exists, and
              every steps file is named somewhere (a feature file, SKILL.md,
              or the suite manifest)
  surfaces    every user-facing source file (SURFACE_GLOBS) is claimed by some
              feature's `Sources:` line, so a new screen, dialog, or control
              cannot appear without a feature file; a Sources glob that matches
              nothing is dead and fails too (only warns under --hook)
  stale       a feature whose claimed sources changed after its `driven on`
              date (a later commit, or uncommitted edits) needs driving again;
              a warning, a failure under --strict
  strings     visible string literals in the surface files that no feature
              file or steps file quotes; a warning, because many are copy
              inside a mapped feature, but a new button or dialog shows up here
              first

  python selfcheck.py            everything; exit 1 on an integrity or surface failure
  python selfcheck.py --strict   stale features fail too
  python selfcheck.py --hook     integrity and surfaces only, no git, for pre-commit;
                                 a dead Sources glob only warns there, because in a
                                 stack of commits the map may land before the code

A failure means the map is behind the app, not that the app is broken.
"""

from __future__ import annotations

import argparse
import glob
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
REPO = SKILL_DIR.parent.parent.parent  # .claude/skills/verify-<app>/scripts -> repo root
FEATURES_DIR = SKILL_DIR / "features"
STEPS_DIR = SKILL_DIR / "scripts" / "steps"
SKILL_MD = SKILL_DIR / "SKILL.md"
SUITE_TXT = STEPS_DIR / "suite.txt"

# ---- FILL IN for the app --------------------------------------------------------
# Files a user sees the result of (screens, dialogs, widgets, CLI commands);
# each must be claimed by a feature's Sources line.  Globs are relative to the
# repository root; `**` recurses.  Leave none out that a user can reach.
SURFACE_GLOBS: tuple[str, ...] = (
    # "projects/<app>/lib/features/**/*.dart",
    # "projects/<app>/lib/widgets/*.dart",
)
SURFACE_IGNORE = (re.compile(r"\.g\.dart$"), re.compile(r"_test\.dart$"))

# The driving H2 names the harness; the other three are fixed across the family.
DRIVING_H2 = "Driving it with <harness>"

# Visible copy in the app's sources, one regex per literal shape, group 1 the text.
# These are for Flutter (Text(...), tooltips, labels, titles as plain literals;
# interpolated strings are skipped).  Replace for another toolkit: JSX text and
# aria-labels for React, `msgid` for gettext, `--help` strings for a CLI.
STRING_RES = (
    re.compile(r"\bText\(\s*(?:const\s+)?'((?:[^'\\$]|\\.)+)'"),
    re.compile(r"\bText\(\s*(?:const\s+)?\"((?:[^\"\\$]|\\.)+)\""),
    re.compile(
        r"\b(?:tooltip|label|semanticsLabel|message|title|hint|hintText):\s*(?:const\s+)?(?:Text\()?'((?:[^'\\$]|\\.)+)'"
    ),
    re.compile(
        r"\b(?:tooltip|label|semanticsLabel|message|title|hint|hintText):\s*(?:const\s+)?(?:Text\()?\"((?:[^\"\\$]|\\.)+)\""
    ),
)
STRING_IGNORE = (
    re.compile(r"^[a-z0-9_./:-]+$"),  # identifiers, paths, topics
    re.compile(r"^\W*$"),
    re.compile(r"^.{0,2}$"),
)
# ---- end of the block to fill in -------------------------------------------------

H2S = ("Sub-features", "How to get to it (user POV)", DRIVING_H2, "Gotchas")
STATUS_RE = re.compile(
    r"^Status: (drafted from source, not yet driven|driven on (\d{4}-\d{2}-\d{2}).*)$"
)
SOURCES_RE = re.compile(r"^Sources: (.+)$")
STEPS_REF_RE = re.compile(r"scripts/steps/([\w-]+\.steps)")
SUBFEATURE_RE = re.compile(r"^- `([a-z0-9]+(?:-[a-z0-9]+)*)`")
INDEX_LINK_RE = re.compile(r"\]\(\./([\w-]+\.md)\)")
NAV_NODE_RE = re.compile(r"<br/>([\w-]+\.md)\"\]")


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.notes: list[str] = []

    def fail(self, text: str) -> None:
        self.failures.append(text)

    def warn(self, text: str) -> None:
        self.warnings.append(text)

    def ok(self, text: str) -> None:
        self.notes.append(text)


def _expand(pattern: str) -> list[str]:
    return sorted(
        p.replace("\\", "/")
        for p in glob.glob(pattern, root_dir=REPO, recursive=True)
        if (REPO / p).is_file()
    )


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Feature:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.name = path.name
        self.text = _read(path)
        self.lines = self.text.splitlines()
        self.status: str | None = None
        self.driven: date | None = None
        self.sources: list[str] = []
        self.files: list[str] = []
        self.ids: list[str] = []


def load_features() -> list[Feature]:
    return [Feature(p) for p in sorted(FEATURES_DIR.glob("*.md")) if p.name != "README.md"]


def check_index(features: list[Feature], report: Report) -> None:
    readme = _read(FEATURES_DIR / "README.md")
    listed = INDEX_LINK_RE.findall(readme)
    present = [f.name for f in features]
    for name in present:
        if name not in listed:
            report.fail(f"features/README.md does not list {name} under Features")
    for name in listed:
        if name not in present:
            report.fail(f"features/README.md lists {name}, which does not exist")
    if len(listed) != len(set(listed)):
        report.fail("features/README.md lists a feature twice")
    for name in NAV_NODE_RE.findall(readme):
        if name not in present:
            report.fail(f"the navigation diagram names {name}, which does not exist")
    report.ok(f"index: {len(present)} feature files, all listed")


def check_feature(
    feature: Feature, report: Report, seen_ids: dict[str, str], dead_glob_fails: bool = True
) -> None:
    name = feature.name
    lines = feature.lines
    if not lines or not lines[0].startswith("# "):
        report.fail(f"{name}: the first line is not an H1 title")
    status_lines = [line for line in lines[:6] if line.startswith("Status:")]
    if not status_lines:
        report.fail(f"{name}: no `Status:` line in the first six lines")
    else:
        m = STATUS_RE.match(status_lines[0])
        if not m:
            report.fail(
                f"{name}: Status line is neither drafted nor `driven on <date>`: {status_lines[0]!r}"
            )
        else:
            feature.status = status_lines[0]
            if m.group(2):
                feature.driven = date.fromisoformat(m.group(2))
    sources_lines = [line for line in lines[:8] if line.startswith("Sources:")]
    if not sources_lines:
        report.fail(
            f"{name}: no `Sources:` line under Status (the globs of the app source that renders it)"
        )
    else:
        feature.sources = [
            s.strip("`") for s in SOURCES_RE.match(sources_lines[0]).group(1).split()
        ]
        for pattern in feature.sources:
            files = _expand(pattern)
            if not files:
                say = report.fail if dead_glob_fails else report.warn
                say(f"{name}: Sources glob `{pattern}` matches no file")
            feature.files.extend(files)
    h2s = [line[3:].strip() for line in lines if line.startswith("## ")]
    if h2s != list(H2S):
        report.fail(f"{name}: H2 sections are {h2s}, expected {list(H2S)} in that order")
    in_subfeatures = False
    for line in lines:
        if line.startswith("## "):
            in_subfeatures = line[3:].strip() == H2S[0]
            continue
        if in_subfeatures and line.startswith("- "):
            m = SUBFEATURE_RE.match(line)
            if not m:
                report.fail(
                    f"{name}: sub-feature bullet without a kebab-case id in backticks: {line[:60]!r}"
                )
                continue
            sub_id = m.group(1)
            if sub_id in seen_ids:
                report.fail(f"{name}: sub-feature id `{sub_id}` is also in {seen_ids[sub_id]}")
            seen_ids[sub_id] = name
            feature.ids.append(sub_id)
    if not feature.ids:
        report.fail(f"{name}: no sub-feature ids")
    for ref in sorted(set(STEPS_REF_RE.findall(feature.text))):
        if not (STEPS_DIR / ref).exists():
            report.fail(f"{name}: names scripts/steps/{ref}, which does not exist")
    proof = [line for line in lines if line.startswith("- **Proof.**")]
    if not proof:
        report.fail(f"{name}: no `- **Proof.**` bullet under Driving")
    elif (
        not STEPS_REF_RE.search(proof[0])
        and "scripts/live/" not in proof[0]
        and "<run>/live/" not in proof[0]
    ):
        report.fail(f"{name}: the Proof bullet names no steps file or live script")


def check_steps_referenced(features: list[Feature], report: Report) -> None:
    corpus = "\n".join(f.text for f in features) + _read(SKILL_MD)
    if SUITE_TXT.exists():
        corpus += _read(SUITE_TXT)
    for steps in sorted(STEPS_DIR.glob("*.steps")):
        if steps.name not in corpus:
            report.fail(
                f"scripts/steps/{steps.name} is named by no feature file, SKILL.md, or suite.txt"
            )
    report.ok(f"steps: {len(list(STEPS_DIR.glob('*.steps')))} files, all referenced")


def check_surfaces(features: list[Feature], report: Report) -> None:
    if not SURFACE_GLOBS:
        report.fail(
            "SURFACE_GLOBS is empty: fill in the user-facing source globs at the top of selfcheck.py"
        )
        return
    claimed: dict[str, list[str]] = {}
    for feature in features:
        for path in feature.files:
            claimed.setdefault(path, []).append(feature.name)
    surfaces: list[str] = []
    for pattern in SURFACE_GLOBS:
        surfaces.extend(p for p in _expand(pattern) if not any(r.search(p) for r in SURFACE_IGNORE))
    surfaces = sorted(set(surfaces))
    unclaimed = [p for p in surfaces if p not in claimed]
    for path in unclaimed:
        report.fail(
            f"surface {path} is claimed by no feature file's Sources line (a new screen, dialog, or control needs a feature file or a Sources line)"
        )
    report.ok(f"surfaces: {len(surfaces)} files, {len(surfaces) - len(unclaimed)} claimed")


def _git(*args: str) -> str:
    try:
        out = subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8", check=False
        )
    except OSError:
        return ""
    return out.stdout.strip()


def check_stale(features: list[Feature], report: Report, strict: bool) -> None:
    for feature in features:
        say = report.fail if strict else report.warn
        if feature.driven is None:
            if feature.status is not None:
                say(f"{feature.name}: never driven ({feature.status})")
            continue
        if not feature.files:
            continue
        last = _git("log", "-1", "--format=%cs", "--", *feature.files)
        dirty = _git("status", "--porcelain", "--", *feature.files)
        if dirty:
            changed = sorted({row[3:] for row in dirty.splitlines()})
            say(
                f"{feature.name}: driven on {feature.driven}, but its sources have uncommitted changes ({', '.join(changed[:4])}{'...' if len(changed) > 4 else ''}); drive it again"
            )
        elif last and date.fromisoformat(last) > feature.driven:
            say(
                f"{feature.name}: driven on {feature.driven}, sources last committed {last}; drive it again"
            )
    report.ok("stale: dates compared for every driven feature")


def _unescape(text: str) -> str:
    return text.replace("\\'", "'").replace('\\"', '"').replace("\\n", " ")


def check_strings(features: list[Feature], report: Report) -> None:
    corpus = "\n".join(f.text for f in features)
    for steps in STEPS_DIR.glob("*.steps"):
        corpus += "\n" + _read(steps)
    corpus += "\n" + _read(SKILL_MD)
    corpus_flat = " ".join(corpus.split())
    found = 0
    unmapped: list[tuple[str, str]] = []
    seen: set[str] = set()
    for pattern in SURFACE_GLOBS:
        for path in _expand(pattern):
            text = _read(REPO / path)
            for regex in STRING_RES:
                for m in regex.finditer(text):
                    literal = _unescape(m.group(1)).strip()
                    if any(r.search(literal) for r in STRING_IGNORE) or literal in seen:
                        continue
                    seen.add(literal)
                    found += 1
                    if " ".join(literal.split()) not in corpus_flat:
                        unmapped.append((path, literal))
    for path, literal in unmapped[:60]:
        report.warn(f"{path}: visible copy {literal!r} is quoted by no feature file or steps file")
    if len(unmapped) > 60:
        report.warn(f"... and {len(unmapped) - 60} more unmapped strings")
    report.ok(f"strings: {found} visible literals, {found - len(unmapped)} quoted in the map")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--strict", action="store_true", help="stale features fail instead of warning"
    )
    parser.add_argument(
        "--hook", action="store_true", help="integrity and surfaces only (no git, no strings)"
    )
    args = parser.parse_args()
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    report = Report()
    features = load_features()
    check_index(features, report)
    seen_ids: dict[str, str] = {}
    for feature in features:
        check_feature(feature, report, seen_ids, dead_glob_fails=not args.hook)
    check_steps_referenced(features, report)
    check_surfaces(features, report)
    if not args.hook:
        check_stale(features, report, args.strict)
        check_strings(features, report)

    for line in report.notes:
        print(f"ok    {line}")
    for line in report.warnings:
        print(f"WARN  {line}")
    for line in report.failures:
        print(f"FAIL  {line}")
    print(f"self-check: {len(report.failures)} failures, {len(report.warnings)} warnings")
    return 1 if report.failures else 0


if __name__ == "__main__":
    sys.exit(main())
