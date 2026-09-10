#!/usr/bin/env python3
"""Build a curated batch for upstream path-only reorganizations.

Only translations with the same file, byte-for-byte identical English source,
and one unambiguous reviewed translation are migrated. The script never edits
translation memory directly; its JSON output must still be applied explicitly.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRANSLATIONS = ROOT / "localization" / "translations"
LOCALES = ("zh-CN",)
ACCEPTED = {"translated", "reviewed"}


def read_jsonl_text(text: str) -> list[dict]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def read_current(locale: str) -> list[dict]:
    return read_jsonl_text(
        (TRANSLATIONS / f"{locale}.jsonl").read_text(encoding="utf-8-sig")
    )


def read_baseline(ref: str, locale: str) -> list[dict]:
    path = f"localization/translations/{locale}.jsonl"
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return read_jsonl_text(result.stdout)


def build_locale(ref: str, locale: str, files: set[str]) -> tuple[dict, list[str]]:
    old_rows = read_baseline(ref, locale)
    current_rows = read_current(locale)
    old_ids = {row["id"] for row in old_rows}

    by_source: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in old_rows:
        translation = row.get("translation", "")
        if row.get("status") in ACCEPTED and translation:
            by_source[(row["file"], row["source"])].add(translation)

    migrated: dict[str, str] = {}
    unresolved: list[str] = []
    for row in current_rows:
        if row["file"] not in files:
            continue
        affected = row.get("status") == "needs-review" or row["id"] not in old_ids
        if not affected:
            continue
        matches = by_source.get((row["file"], row["source"]), set())
        if len(matches) != 1:
            unresolved.append(
                f"{row['id']}: expected one prior translation, found {len(matches)}"
            )
            continue
        migrated[row["id"]] = next(iter(matches))
    return migrated, unresolved


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline-ref", default="HEAD")
    parser.add_argument("--file", action="append", required=True, dest="files")
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--allow-unmatched",
        action="store_true",
        help="write unambiguous matches and report unmatched units instead of failing",
    )
    args = parser.parse_args()

    output: dict[str, dict] = {}
    unresolved: list[str] = []
    for locale in LOCALES:
        migrated, locale_unresolved = build_locale(
            args.baseline_ref, locale, set(args.files)
        )
        output[locale] = migrated
        unresolved.extend(f"{locale}: {item}" for item in locale_unresolved)

    if unresolved and not args.allow_unmatched:
        raise SystemExit(
            "Source migration was not unambiguous:\n" + "\n".join(unresolved)
        )

    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        f"wrote {target} with "
        + ", ".join(f"{locale}={len(output[locale])}" for locale in LOCALES)
    )
    if unresolved:
        print(f"left {len(unresolved)} units for manual review")


if __name__ == "__main__":
    main()
