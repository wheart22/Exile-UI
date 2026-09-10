#!/usr/bin/env python3
"""Create a deterministic, standalone PoE1 Simplified Chinese release archive."""

from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "localization"
PACKS = WORK / "packs"
REPORTS = WORK / "reports"
CONFIG = WORK / "release.json"
def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def release_asset_bytes(path: Path) -> bytes:
    """Normalize user-facing installer text for reproducible Windows archives."""
    text = path.read_text(encoding="utf-8-sig")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if path.suffix.lower() in {".cmd", ".txt"}:
        text = text.replace("\n", "\r\n")
    return text.encode("utf-8")


def add_bytes(
    archive: zipfile.ZipFile,
    name: str,
    data: bytes,
    zip_time: tuple[int, int, int, int, int, int],
) -> None:
    info = zipfile.ZipInfo(name, zip_time)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def runtime_archive_entries(
    config: dict[str, Any], archive_root: str
) -> list[tuple[str, bytes]]:
    """Read the runtime from git so export-ignore rules match upstream archives."""
    roots = [str(item).replace("\\", "/").rstrip("/") for item in config.get("runtime_paths", [])]
    if not roots:
        raise SystemExit("release has no runtime_paths")
    result = subprocess.run(
        ["git", "archive", "--format=tar", f"--prefix={archive_root}/", "HEAD", "--", *roots],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    entries: list[tuple[str, bytes]] = []
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode="r:") as archive:
        for item in archive:
            if not item.isfile():
                continue
            source = archive.extractfile(item)
            if source is None:
                raise SystemExit(f"unable to read release file: {item.name}")
            entries.append((item.name, source.read()))
    if not entries:
        raise SystemExit("release runtime_paths contain no tracked files")
    return entries


def create_application_archive(
    path: Path,
    config: dict[str, Any],
    zip_time: tuple[int, int, int, int, int, int],
) -> dict[str, str]:
    members: dict[str, str] = {}
    root = f"Exile-UI-zh-CN-{config['version']}"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for member, data in runtime_archive_entries(config, root):
            add_bytes(archive, member, data, zip_time)
            members[member] = sha256_bytes(data)

        instructions = config.get("release_instructions", {})
        source = ROOT / instructions.get("instructions_source", "")
        member = instructions.get("instructions_archive_name", "")
        if not source.is_file() or not member:
            raise SystemExit("missing standalone-release instructions")
        data = release_asset_bytes(source)
        member = f"{root}/{member}"
        add_bytes(archive, member, data, zip_time)
        members[member] = sha256_bytes(data)
    return members


def verify_release_scope(config: dict[str, Any]) -> None:
    validate = read_json(REPORTS / "validate.json")
    if not validate.get("ok") or validate.get("errors") or validate.get("warnings"):
        raise SystemExit("localization validation is not clean")

    for locale in config["locales"]:
        report = read_json(REPORTS / f"build-{locale}.json")
        required_complete = (
            "UI.txt",
            "[leveltracker] default guide.json",
            "[leveltracker] areas.json",
            "[leveltracker] gems.json",
        )
        for name in required_complete:
            item = report.get(name, {})
            if not item.get("built") or item.get("translated") != item.get("total"):
                raise SystemExit(f"{locale}/{name} is not complete")
            if item.get("unresolved"):
                raise SystemExit(f"{locale}/{name} has unresolved entries")

        tooltip = report.get("help tooltips.json", {})
        if not tooltip.get("built") or tooltip.get("translated", 0) < 148:
            raise SystemExit(f"{locale}/help tooltips.json is missing the reviewed PoE1 scope")

        for excluded in config.get("excluded_files", []):
            if excluded in config["included_files"]:
                raise SystemExit(f"excluded file accidentally included: {excluded}")

    if config.get("archive_layout") != "exile-ui-root":
        raise SystemExit("standalone releases must use the Exile UI root layout")
    runtime_archive_entries(config, f"Exile-UI-zh-CN-{config['version']}")
    release_instructions = config.get("release_instructions", {})
    instructions = ROOT / release_instructions.get("instructions_source", "")
    if not instructions.is_file():
        raise SystemExit(f"missing standalone-release instructions: {instructions}")

def main() -> None:
    config = read_json(CONFIG)
    subprocess.run(
        [sys.executable, str(WORK / "tools" / "localize.py"), "validate"],
        cwd=ROOT,
        check=True,
    )
    verify_release_scope(config)

    version = config["version"]
    year, month, day = (int(part) for part in config["release_date"].split("-"))
    zip_time = (year, month, day, 0, 0, 0)
    output = WORK / "releases" / version
    output.mkdir(parents=True, exist_ok=True)
    locales = config["locales"]

    archives: dict[str, dict[str, Any]] = {}
    if len(locales) != 1:
        raise SystemExit("the standalone release must contain exactly one locale")
    locale = locales[0]
    name = f"Exile-UI-{locale}-{version}.zip"
    path = output / name
    members = create_application_archive(path, config, zip_time)
    archives[name] = {
        "sha256": sha256_bytes(path.read_bytes()),
        "size": path.stat().st_size,
        "members": members,
    }

    upstream_manifest = WORK / "state" / "upstream-manifest.json"
    manifest = {
        **config,
        "upstream_manifest_sha256": sha256_bytes(upstream_manifest.read_bytes()),
        "validation": read_json(REPORTS / "validate.json"),
        "archives": archives,
    }
    write_json(output / "manifest.json", manifest)
    checksums = "".join(f"{item['sha256']}  {name}\n" for name, item in sorted(archives.items()))
    (output / "SHA256SUMS.txt").write_text(checksums, encoding="utf-8")
    print(f"created {len(archives)} archives in {output}")


if __name__ == "__main__":
    main()
