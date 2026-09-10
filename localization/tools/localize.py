#!/usr/bin/env python3
"""Incremental, syntax-safe localization workflow for Exile UI."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / "localization"
ENGLISH = ROOT / "data" / "english"
TRANSLATIONS = WORK / "translations"
PACKS = WORK / "packs"
REPORTS = WORK / "reports"
STATE = WORK / "state"
GLOSSARY_FILE = WORK / "glossary" / "glossary.json"
MANUAL_GLOSSARY = WORK / "glossary" / "manual.csv"
QUEST_LABELS_FILE = WORK / "glossary" / "quest-labels.json"
SEEDS_FILE = WORK / "translations" / "seeds.json"
GEM_NAMES_FILE = WORK / "glossary" / "gems-zh-CN.json"
SUPPORTED = ("zh-CN",)
DEFAULT_FILES = (
    "UI.txt",
    "help tooltips.json",
    "[leveltracker] default guide.json",
)

# These are parsed by AHK or select rendering behavior. The whole token is protected,
# then restored after translation. Ordering may change; spelling and multiplicity may not.
TOKEN_RE = re.compile(
    r"areaid[0-9A-Za-z_]+"
    r"|\(quest:(?:[^()]|\([^()]*\))+\)"
    r"|\((?:img|color|lvl|quest):[^()]+\)"
    r"|\(hint\)_*"
    r"|<[^<>\r\n]+>"
    r"|\|\|"
    r"|;;"
    r"|arena:"
    r"|(?<![\w-])(?:buy gem:|buy item:|quest-check|leaguestart:|twinkrun:|optional:|kill)(?![\w-])",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(r"__XUI_TOKEN_\d{3}__")
KEY_VALUE_RE = re.compile(r'^\s*([^;][^=]*?)\s*=\s*"(.*?)"\s*(?:;##.*)?$')


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if line.strip():
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise SystemExit(f"{path}:{number}: invalid JSON: {exc}") from exc
    return records


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(x, ensure_ascii=False, sort_keys=False) + "\n" for x in records)
    path.write_text(content, encoding="utf-8")


def json_pointer(parts: list[Any]) -> str:
    return "/" + "/".join(str(x).replace("~", "~0").replace("/", "~1") for x in parts)


def walk_strings(value: Any, parts: list[Any] | None = None) -> Iterable[tuple[list[Any], str]]:
    parts = parts or []
    if isinstance(value, str):
        yield parts, value
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk_strings(item, parts + [index])
    elif isinstance(value, dict):
        for key, item in value.items():
            # condition values are program data, not display text.
            if key != "condition":
                yield from walk_strings(item, parts + [key])


def set_path(value: Any, parts: list[Any], replacement: str) -> None:
    cursor = value
    for part in parts[:-1]:
        cursor = cursor[part]
    cursor[parts[-1]] = replacement


def get_path(value: Any, parts: list[Any]) -> Any:
    cursor = value
    for part in parts:
        cursor = cursor[part]
    return cursor


CONTROL_TRANSLATIONS = {
    "zh-CN": {"leaguestart:": "开荒:", "twinkrun:": "小号:", "optional:": "可选:", "kill": "击杀"},
}

# Angle brackets are renderer-visible emphasis. Their delimiters are syntax,
# but their contents are player-facing quest/reward labels and must be
# localized. Keep the delimiters while translating every known guide label.
ANGLE_TOKEN_TRANSLATIONS = {
    "zh-CN": {
        "<2_respecs>": "<2点天赋重置点>",
        "<a_fixture_of_fate>": "<命运之语>",
        "<amulet>": "<项链>",
        "<armor>": "<护甲>",
        "<belt/amu>": "<腰带/项链>",
        "<belt>": "<腰带>",
        "<boots>": "<鞋子>",
        "<breaking_some_eggs1>": "<打破鸟蛋>",
        "<breaking_some_eggs2>": "<打破鸟蛋>",
        "<breaking_the_seal>": "<突破封印>",
        "<enemy_at_the_gate>": "<大门口的敌人>",
        "<fallen_from_grace>": "<优雅不再>",
        "<helmet>": "<头盔>",
        "<intruders_in_black>": "<黑色入侵者>",
        "<invite_to_hideout>": "<邀请至藏身处>",
        "<jewel>": "<珠宝>",
        "<lost_in_love>": "<迷失的爱情>",
        "<mercy_mission>": "<医者之心>",
        "<respec_points>": "<天赋重置点>",
        "<respecs>": "<天赋重置点>",
        "<ring>": "<戒指>",
        "<sever_the_right_hand>": "<铲除左右手>",
        "<sharp_and_cruel>": "<清理蜘蛛>",
        "<the_caged_brute1>": "<冲出监牢>",
        "<the_caged_brute2>": "<冲出监牢>",
        "<the_eternal_nightmare>": "<永恒梦魇>",
        "<the_siren's_cadence>": "<海妖之歌>",
        "<the_way_forward>": "<开路先锋>",
        '<type_"/passives"_in_chat>': '<在聊天框中输入_"/passives">',
        "<weap>": "<武器>",
        "<weapon/offhand>": "<武器/副手>",
        "<the_act-tracker_guide_ends_here>": "<章节追踪指南到此结束>",
    }
}

_QUEST_LABELS: dict[str, dict[str, str]] | None = None


def localized_quest_token(original: str, locale: str, context: str = "") -> str:
    global _QUEST_LABELS
    if _QUEST_LABELS is None:
        _QUEST_LABELS = read_json(QUEST_LABELS_FILE) if QUEST_LABELS_FILE.exists() else {}
    inner = original[len("(quest:"):-1]
    wrapped = inner.startswith("(") and inner.endswith(")")
    lookup = inner[1:-1] if wrapped else inner
    suffix = "?" if lookup.endswith("?") else ""
    key = lookup[:-1] if suffix else lookup
    if wrapped and key == "eye" and re.search(r"\bqueen\b", context, re.IGNORECASE):
        key = "eye_of_conquest"
    labels = _QUEST_LABELS.get(locale, {})
    translated = labels.get(f"({key})" if wrapped else key, labels.get(key, key)) + suffix
    if wrapped:
        translated = f"({translated})"
    return f"(quest:{translated})"


def mask_tokens(text: str, locale: str) -> tuple[str, dict[str, str]]:
    tokens: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        key = f"__XUI_TOKEN_{len(tokens) + 1:03d}__"
        original = match.group(0)
        if original.casefold().startswith("(quest:"):
            tokens[key] = localized_quest_token(original, locale, text)
        else:
            tokens[key] = ANGLE_TOKEN_TRANSLATIONS.get(locale, {}).get(
                original,
                CONTROL_TRANSLATIONS.get(locale, {}).get(original.casefold(), original),
            )
        return key

    return TOKEN_RE.sub(replace, text), tokens


def restore_tokens(text: str, tokens: dict[str, str]) -> str:
    found = Counter(PLACEHOLDER_RE.findall(text))
    expected = Counter(tokens.keys())
    if found != expected:
        missing = list((expected - found).elements())
        extra = list((found - expected).elements())
        raise ValueError(f"placeholder mismatch; missing={missing}, extra={extra}")
    # The AHK renderer splits formatting spans on ASCII spaces. Without an
    # explicit boundary, Chinese text after a quest label inherits its green
    # color. Keep punctuation as a separate renderer part as well.
    for placeholder, token in tokens.items():
        if token.casefold().startswith("(quest:"):
            text = text.replace(placeholder + "，", placeholder + " , ")
            text = text.replace(placeholder + "；", placeholder + " ; ")
            text = re.sub(re.escape(placeholder) + r"(?=\S)", placeholder + " ", text)
    # Normalize verbs according to the renderer icon's meaning. A waypoint is
    # activated rather than "obtained", a portal is opened rather than
    # "placed", and numbered arrow icons describe a direction rather than the
    # grammatical object of 前往/寻找.
    direction_placeholders = {
        placeholder
        for placeholder, token in tokens.items()
        if re.fullmatch(r"\(img:[0-7]\)", token, re.IGNORECASE)
    }
    waypoint_placeholders = {
        placeholder
        for placeholder, token in tokens.items()
        if token.casefold() == "(img:waypoint)"
    }
    portal_placeholders = {
        placeholder
        for placeholder, token in tokens.items()
        if token.casefold() == "(img:portal)"
    }
    craft_placeholders = {
        placeholder
        for placeholder, token in tokens.items()
        if token.casefold() == "(img:craft)"
    }
    for placeholder in waypoint_placeholders:
        text = re.sub(rf"取得\s*{re.escape(placeholder)}", f"激活 {placeholder}", text)
    for placeholder in portal_placeholders:
        text = re.sub(rf"(?:放置|设置)\s*{re.escape(placeholder)}", f"开启 {placeholder}", text)
    for placeholder in craft_placeholders:
        text = re.sub(rf"取得\s*{re.escape(placeholder)}", f"解锁 {placeholder} 工艺配方", text)
    for placeholder in direction_placeholders:
        escaped = re.escape(placeholder)
        text = re.sub(rf"向\s*{escaped}\s*前进寻找", f"沿 {placeholder} 方向寻找", text)
        text = re.sub(rf"向\s*{escaped}\s*前往", f"沿 {placeholder} 方向前往", text)
        text = re.sub(rf"向\s*{escaped}\s*激活", f"沿 {placeholder} 方向前进，激活", text)
    for placeholder, token in tokens.items():
        text = text.replace(placeholder, token)
    # Upstream occasionally contains duplicated control words such as
    # "kill kill doedre". Both placeholders must survive validation, but the
    # localized renderer should display the action only once.
    text = re.sub(r"击杀(?:\s*击杀)+", "击杀", text)
    # Color and arena markers also last until the next ASCII space. These are
    # recurring translated clause boundaries in the curated route guide.
    style_boundaries = (
        ("起点与", "起点 与"), ("出口位于", "出口 位于"),
        ("黑渊危机位于", "黑渊危机 位于"), ("桥前", "桥 前"),
        ("洞穴与", "洞穴 与"), ("藏身处购买", "藏身处 购买"),
        ("克雷顿，", "克雷顿 "), ("欧克，", "欧克 "), ("阿莉亚，", "阿莉亚 "),
        ("走廊指向", "走廊 指向"), ("楼梯和", "楼梯 和"),
        ("大门通往", "大门 通往"), ("货车通往", "货车 通往"),
        ("起点西侧", "起点 西侧"),
    )
    parts = text.split(" ")
    for index, part in enumerate(parts):
        if "(color:" in part or "arena:" in part:
            for source, replacement in style_boundaries:
                part = part.replace(source, replacement)
            parts[index] = part
    return " ".join(parts)


def load_glossary() -> list[dict[str, str]]:
    return read_json(GLOSSARY_FILE) if GLOSSARY_FILE.exists() else []


def glossary_hints(text: str, glossary: list[dict[str, str]]) -> list[dict[str, str]]:
    target = "name_zh"
    lower = text.casefold()
    hits = []
    seen = set()
    for row in glossary:
        source = row.get("name_en", "")
        translated = row.get(target, "")
        if len(source) >= 3 and translated and source.casefold() in lower and source.casefold() not in seen:
            seen.add(source.casefold())
            hits.append({"en": source, "target": translated, "category": row.get("category", "")})
    return sorted(hits, key=lambda x: (-len(x["en"]), x["en"]))


def txt_units(path: Path, locale: str, glossary: list[dict[str, str]]) -> list[dict[str, Any]]:
    units = []
    occurrences: Counter[str] = Counter()
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith(";"):
            continue
        match = KEY_VALUE_RE.match(line)
        if not match:
            continue
        key, source = match.group(1).strip(), match.group(2)
        occurrences[key] += 1
        # UI/client values are atomic key/value records. Guide markup is not
        # interpreted in these files, so do not turn ordinary UI words such as
        # "kill" into guide placeholders.
        masked, tokens = source, {}
        unit_id = f"{path.name}::key={key}::occ={occurrences[key]}"
        units.append({
            "id": unit_id,
            "file": path.name,
            "kind": "client-exact" if path.name == "client.txt" else "ui",
            "key": key,
            "occurrence": occurrences[key],
            "line": line_number,
            "source": source,
            "source_hash": sha(source),
            "masked_source": masked,
            "tokens": tokens,
            "glossary": glossary_hints(source, glossary),
            "translation": "",
            "status": "untranslated",
        })
    return units


def json_units(path: Path, locale: str, glossary: list[dict[str, str]]) -> list[dict[str, Any]]:
    units = []
    for parts, source in walk_strings(read_json(path)):
        masked, tokens = mask_tokens(source, locale)
        pointer = json_pointer(parts)
        units.append({
            "id": f"{path.name}::{pointer}",
            "file": path.name,
            "kind": "guide",
            "path": parts,
            "source": source,
            "source_hash": sha(source),
            "masked_source": masked,
            "tokens": tokens,
            "glossary": glossary_hints(source, glossary),
            "translation": "",
            "status": "untranslated",
        })
    return units


def all_units(locale: str, files: Iterable[str]) -> list[dict[str, Any]]:
    glossary = load_glossary()
    result = []
    for name in files:
        path = ENGLISH / name
        if not path.exists():
            continue
        result.extend(json_units(path, locale, glossary) if path.suffix == ".json" else txt_units(path, locale, glossary))
    return result


def merge_memory(current: list[dict[str, Any]], old: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    old_by_id = {x["id"]: x for x in old}
    current_ids = {x["id"] for x in current}
    counts = Counter()
    changed = []
    for unit in current:
        previous = old_by_id.get(unit["id"])
        if not previous:
            counts["new"] += 1
            continue
        if previous.get("source_hash") == unit["source_hash"]:
            for field in ("translation", "status", "reviewer", "note"):
                if field in previous:
                    unit[field] = previous[field]
            counts["unchanged"] += 1
        else:
            if previous.get("translation"):
                unit["previous_translation"] = previous["translation"]
            unit["status"] = "needs-review"
            counts["changed"] += 1
            changed.append(unit["id"])
    removed = sorted(set(old_by_id) - current_ids)
    counts["removed"] = len(removed)
    return current, {"counts": dict(counts), "changed": changed, "removed": removed}


def apply_seeds(locale: str, units: list[dict[str, Any]]) -> None:
    if not SEEDS_FILE.exists():
        return
    seeds = read_json(SEEDS_FILE).get(locale, {})
    for unit in units:
        if unit["id"] in seeds and not unit.get("translation"):
            unit["translation"] = seeds[unit["id"]]
            unit["status"] = "reviewed"
            unit["reviewer"] = "curated-seed"


def command_export(args: argparse.Namespace) -> None:
    path = TRANSLATIONS / f"{args.locale}.jsonl"
    old = read_jsonl(path)
    units, report = merge_memory(all_units(args.locale, args.files), old)
    apply_seeds(args.locale, units)
    write_jsonl(path, units)
    write_json(REPORTS / f"export-{args.locale}.json", report)
    print(f"exported {len(units)} units to {path}")
    print(json.dumps(report["counts"], ensure_ascii=False))


def command_sync(args: argparse.Namespace) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    STATE.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for path in sorted(ENGLISH.iterdir()):
        if path.is_file():
            data = path.read_bytes()
            manifest[path.name] = {"sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}
    old_path = STATE / "upstream-manifest.json"
    old = read_json(old_path) if old_path.exists() else {}
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "new": sorted(set(manifest) - set(old)),
        "changed": sorted(k for k in set(manifest) & set(old) if manifest[k] != old[k]),
        "removed": sorted(set(old) - set(manifest)),
        "unchanged": sorted(k for k in set(manifest) & set(old) if manifest[k] == old[k]),
    }
    write_json(old_path, manifest)
    for locale in SUPPORTED:
        path = TRANSLATIONS / f"{locale}.jsonl"
        units, unit_report = merge_memory(all_units(locale, DEFAULT_FILES), read_jsonl(path))
        apply_seeds(locale, units)
        write_jsonl(path, units)
        report[f"units_{locale}"] = unit_report
    write_json(REPORTS / "sync.json", report)
    print(f"wrote {REPORTS / 'sync.json'}")


def command_glossary(args: argparse.Namespace) -> None:
    source_root = Path(args.poe_trans_data)
    rows: dict[tuple[str, str, str], dict[str, str]] = {}
    categories = ("areas", "quests", "bosses", "npcs", "monsters", "quest_items", "items", "keywords", "guide_entities", "text_audio_entities")
    for game in ("poe1",):
        output = source_root / "data" / game / "output"
        for category in categories:
            path = output / f"{category}.csv"
            if not path.exists():
                continue
            with path.open(encoding="utf-8-sig", newline="") as handle:
                for raw in csv.DictReader(handle):
                    en = (raw.get("name_en") or "").strip()
                    zh = (raw.get("name_zh") or "").strip()
                    if not en or not zh:
                        continue
                    actual_category = (raw.get("category") or category).strip()
                    rows[(game, actual_category, en.casefold())] = {
                        "game": game, "category": actual_category, "name_en": en,
                        "name_zh": zh, "source": str(path), "note": "",
                    }
    if MANUAL_GLOSSARY.exists():
        with MANUAL_GLOSSARY.open(encoding="utf-8-sig", newline="") as handle:
            for raw in csv.DictReader(handle):
                en = (raw.get("name_en") or "").strip()
                if en:
                    rows[(raw.get("game", "shared"), raw.get("category", "manual"), en.casefold())] = {
                        "game": (raw.get("game") or "shared").strip(),
                        "category": (raw.get("category") or "manual").strip(),
                        "name_en": en,
                        "name_zh": (raw.get("name_zh") or "").strip(),
                        "source": (raw.get("source") or "").strip(),
                        "note": (raw.get("note") or "").strip(),
                    }
    result = sorted(rows.values(), key=lambda x: (x["game"], x["category"], x["name_en"].casefold()))
    write_json(GLOSSARY_FILE, result)
    covered = {x["name_en"].casefold() for x in result}
    gaps = []
    poe1_gems = read_json(ENGLISH / "[leveltracker] gems.json")
    for name in poe1_gems:
        if not name.startswith("_") and name.casefold() not in covered:
            gaps.append({"game": "poe1", "category": "gem", "name_en": name})
    write_json(REPORTS / "glossary-gaps.json", gaps)
    print(f"wrote {len(result)} terms to {GLOSSARY_FILE}")
    print(f"reported {len(gaps)} missing gem terms in {REPORTS / 'glossary-gaps.json'}")


def parse_txt_values(path: Path) -> dict[tuple[str, int], str]:
    result: dict[tuple[str, int], str] = {}
    occurrences: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith(";"):
            continue
        match = KEY_VALUE_RE.match(line)
        if match:
            key = match.group(1).strip()
            occurrences[key] += 1
            result[(key, occurrences[key])] = match.group(2)
    return result


def legacy_mask(unit: dict[str, Any], legacy: str, locale: str) -> str:
    if not unit.get("tokens"):
        return legacy
    source_matches = [x.group(0) for x in TOKEN_RE.finditer(unit["source"])]
    masked = legacy
    for index, (placeholder, target_token) in enumerate(unit["tokens"].items()):
        original = source_matches[index]
        candidate = target_token if target_token in masked else original
        if candidate not in masked:
            raise ValueError(f"legacy string lost token {original!r}")
        masked = masked.replace(candidate, placeholder, 1)
    return masked


def command_import_legacy(args: argparse.Namespace) -> None:
    source = Path(args.source_dir)
    path = TRANSLATIONS / f"{args.locale}.jsonl"
    records = read_jsonl(path)
    imported, rejected = 0, []
    json_cache: dict[str, Any] = {}
    txt_cache: dict[str, dict[tuple[str, int], str]] = {}
    for unit in records:
        legacy_path = source / unit["file"]
        if not legacy_path.exists() or unit.get("status") == "reviewed":
            continue
        try:
            if unit["file"].endswith(".json"):
                if unit["file"] not in json_cache:
                    json_cache[unit["file"]] = read_json(legacy_path)
                legacy = get_path(json_cache[unit["file"]], unit["path"])
            else:
                if unit["file"] not in txt_cache:
                    txt_cache[unit["file"]] = parse_txt_values(legacy_path)
                legacy = txt_cache[unit["file"]][(unit["key"], unit["occurrence"])]
            if not isinstance(legacy, str) or legacy == unit["source"]:
                continue
            unit["translation"] = legacy_mask(unit, legacy, args.locale)
            unit["status"] = "translated" if args.trust else "needs-review"
            unit["note"] = f"imported from {source}"
            imported += 1
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            rejected.append({"id": unit["id"], "error": str(exc)})
    write_jsonl(path, records)
    write_json(REPORTS / f"legacy-import-{args.locale}.json", {"imported": imported, "rejected": rejected})
    print(f"imported {imported} records; rejected {len(rejected)}")


def command_apply_curated(args: argparse.Namespace) -> None:
    curated = read_json(Path(args.file))
    total = 0
    for locale in SUPPORTED:
        entries = curated.get(locale, {})
        if not entries:
            continue
        path = TRANSLATIONS / f"{locale}.jsonl"
        records = read_jsonl(path)
        by_id = {x["id"]: x for x in records}
        unknown = sorted(set(entries) - set(by_id))
        if unknown:
            raise SystemExit(f"{locale}: curated file contains unknown ids: {unknown[:5]}")
        for unit_id, payload in entries.items():
            unit = by_id[unit_id]
            if isinstance(payload, str):
                translation, status, note = payload, "reviewed", ""
            else:
                translation = payload["translation"]
                status = payload.get("status", "reviewed")
                note = payload.get("note", "")
            if status in ("translated", "reviewed"):
                restore_tokens(translation, unit.get("tokens", {}))
            unit["translation"] = translation
            unit["status"] = status
            unit["reviewer"] = "curated-batch"
            if note:
                unit["note"] = note
            total += 1
        write_jsonl(path, records)
    print(f"applied {total} curated translations from {args.file}")


def valid_records(locale: str) -> tuple[list[dict[str, Any]], list[str]]:
    records = read_jsonl(TRANSLATIONS / f"{locale}.jsonl")
    errors = []
    for unit in records:
        if unit.get("status") not in ("translated", "reviewed") or not unit.get("translation"):
            continue
        try:
            restore_tokens(unit["translation"], unit.get("tokens", {}))
        except ValueError as exc:
            errors.append(f"{unit['id']}: {exc}")
    return records, errors


def build_txt(name: str, records: list[dict[str, Any]], destination: Path, allow_partial: bool) -> tuple[int, int]:
    selected = [x for x in records if x["file"] == name]
    completed = [x for x in selected if x.get("status") in ("translated", "reviewed") and x.get("translation")]
    if not completed:
        destination.unlink(missing_ok=True)
        return 0, len(selected)
    # UI keys have an English key-level fallback. client.txt does not: a partial
    # file would silently turn missing parser values into "0000" and break features.
    if name == "client.txt" and len(completed) != len(selected) and not allow_partial:
        destination.unlink(missing_ok=True)
        return len(completed), len(selected)
    lines = [
        "; Generated by localization/tools/localize.py. Do not edit this file directly.",
        "; Missing keys intentionally fall back to English.", "",
    ]
    for unit in completed:
        value = restore_tokens(unit["translation"], unit.get("tokens", {})).replace('"', '""')
        lines.append(f'{unit["key"]}\t=\t"{value}"')
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(completed), len(selected)


def build_json(name: str, records: list[dict[str, Any]], destination: Path, allow_partial: bool) -> tuple[int, int]:
    selected = [x for x in records if x["file"] == name]
    completed = [x for x in selected if x.get("status") in ("translated", "reviewed") and x.get("translation")]
    if not completed:
        destination.unlink(missing_ok=True)
        return 0, len(selected)
    if len(completed) != len(selected) and not allow_partial:
        destination.unlink(missing_ok=True)
        return len(completed), len(selected)
    value = read_json(ENGLISH / name)
    for unit in completed:
        set_path(value, unit["path"], restore_tokens(unit["translation"], unit.get("tokens", {})))
    write_json(destination, value)
    return len(completed), len(selected)


def load_gem_names() -> dict[str, str]:
    artifact = read_json(GEM_NAMES_FILE)
    names = artifact.get("names") if isinstance(artifact, dict) else None
    if not isinstance(names, dict):
        raise SystemExit(f"invalid gem-name mapping: {GEM_NAMES_FILE}")
    return names


def gem_mapping_errors(source: dict[str, Any], names: dict[str, str]) -> list[str]:
    expected = {key for key in source if not key.startswith("_")}
    errors = []
    missing = sorted(expected - set(names))
    extra = sorted(set(names) - expected)
    if missing:
        errors.append(f"missing gem translations: {', '.join(missing)}")
    if extra:
        errors.append(f"unknown gem translations: {', '.join(extra)}")
    for key in sorted(expected & set(names)):
        display = names[key]
        if not isinstance(display, str) or not re.fullmatch(r".*[\u3400-\u9fff].*（[^（）]+）", display):
            errors.append(f"{key}: name must be 简体中文（English）")
    return errors


def build_gems(destination: Path) -> tuple[int, int]:
    """Add reviewed bilingual names without changing PoB's English lookup keys."""
    source = read_json(ENGLISH / "[leveltracker] gems.json")
    names = load_gem_names()
    errors = gem_mapping_errors(source, names)
    if errors:
        raise SystemExit("invalid PoE1 gem mapping:\n" + "\n".join(errors))
    for key, display in names.items():
        source[key]["name"] = display
    write_json(destination, source)
    total = len([key for key in source if not key.startswith("_")])
    return total, total


def validate_gems(path: Path) -> list[str]:
    source_path = ENGLISH / "[leveltracker] gems.json"
    if not path.is_file():
        return [f"missing generated PoE1 gem database: {path}"]
    try:
        source = read_json(source_path)
        built = read_json(path)
        names = load_gem_names()
    except (OSError, json.JSONDecodeError, SystemExit) as exc:
        return [f"PoE1 gem database: {exc}"]
    errors = gem_mapping_errors(source, names)
    if not isinstance(built, dict):
        return errors + ["generated PoE1 gem database is not an object"]
    if set(built) != set(source):
        errors.append("generated PoE1 gem database changed its top-level keys")
    for key in source:
        if key.startswith("_"):
            if built.get(key) != source[key]:
                errors.append(f"{key}: metadata changed")
            continue
        if key not in built or not isinstance(built[key], dict):
            errors.append(f"{key}: entry missing or not an object")
            continue
        expected_entry = {k: v for k, v in source[key].items() if k != "name"}
        actual_entry = {k: v for k, v in built[key].items() if k != "name"}
        if actual_entry != expected_entry:
            errors.append(f"{key}: non-name data changed")
        if built[key].get("name") != names.get(key):
            errors.append(f"{key}: bilingual name missing or out of sync")
    return errors


def normalize_area_name(name: str) -> str:
    value = name.casefold().replace("’", "'").strip()
    value = re.sub(r"^the\s+", "", value)
    value = re.sub(r"\s+level\s+(\d+)$", r" (\1)", value)
    value = re.sub(r"\s+", " ", value)
    return value


def build_areas(locale: str, destination: Path) -> tuple[int, int, list[str]]:
    """Localize runtime area names used when rendering areaid tokens."""
    target_key = "name_zh"
    lookup: dict[str, str] = {}
    scores: dict[str, int] = {}
    for row in load_glossary():
        source, target = row.get("name_en", "").strip(), row.get(target_key, "").strip()
        category = row.get("category", "").casefold()
        if not source or not target or category not in ("area", "areas"):
            continue
        # areas.csv is the current runtime area table and wins over older or
        # context-derived WorldAreas names in guide_entities.csv.
        score = 2 if category == "areas" else 1
        for key in (source.casefold(), normalize_area_name(source)):
            if score > scores.get(key, -1):
                lookup[key], scores[key] = target, score

    value = read_json(ENGLISH / "[leveltracker] areas.json")
    translated, total, unresolved = 0, 0, []
    for act in value:
        for area in act:
            for field in ("name", "map_name"):
                source = area.get(field)
                if not source:
                    continue
                total += 1
                target = lookup.get(source.casefold()) or lookup.get(normalize_area_name(source))
                if target:
                    area[field] = target
                    translated += 1
                else:
                    unresolved.append(source)
    write_json(destination, value)
    return translated, total, sorted(set(unresolved))


def command_build(args: argparse.Namespace) -> None:
    records, errors = valid_records(args.locale)
    if errors:
        raise SystemExit("\n".join(errors))
    pack = PACKS / args.locale
    pack.mkdir(parents=True, exist_ok=True)
    summary = {}
    for name in sorted({x["file"] for x in records}):
        target = pack / name
        done, total = (build_json(name, records, target, args.allow_partial) if name.endswith(".json") else build_txt(name, records, target, args.allow_partial))
        summary[name] = {"translated": done, "total": total, "built": target.exists()}
    gem_target = pack / "[leveltracker] gems.json"
    done, total = build_gems(gem_target)
    summary["[leveltracker] gems.json"] = {"translated": done, "total": total, "built": gem_target.exists()}
    area_target = pack / "[leveltracker] areas.json"
    done, total, unresolved = build_areas(args.locale, area_target)
    summary["[leveltracker] areas.json"] = {"translated": done, "total": total, "built": True, "unresolved": unresolved}
    write_json(REPORTS / f"build-{args.locale}.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def txt_key_counts(path: Path) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip() or line.lstrip().startswith(";"):
            continue
        match = KEY_VALUE_RE.match(line)
        if match:
            counts[match.group(1).strip()] += 1
    return counts


def command_validate(args: argparse.Namespace) -> None:
    errors, warnings = [], []
    guide_render_antipatterns = (
        (re.compile(r"__XUI_TOKEN"), "unrestored placeholder"),
        (re.compile(r"<[a-z][^>]*>"), "untranslated visible angle label"),
        (re.compile(r"取得 \(img:waypoint\)"), "waypoint rendered as an obtainable item"),
        (re.compile(r"(?:放置|设置) \(img:portal\)"), "portal rendered with a literal placement verb"),
        (re.compile(r"向 \(img:[0-7]\) (?:前往|取得|前进寻找)"), "direction icon used as a grammatical object"),
        (re.compile(r"章\d"), "act prefix rendered in the wrong word order"),
    )
    for locale in SUPPORTED:
        records, record_errors = valid_records(locale)
        errors.extend(f"{locale}: {x}" for x in record_errors)
        by_file = Counter(x["file"] for x in records if x.get("status") in ("translated", "reviewed") and x.get("translation"))
        errors.extend(f"{locale}: {x}" for x in validate_gems(PACKS / locale / "[leveltracker] gems.json"))
        for path in sorted((PACKS / locale).glob("*")) if (PACKS / locale).exists() else []:
            try:
                if path.suffix == ".json":
                    read_json(path)
                elif path.suffix == ".txt":
                    target = txt_key_counts(path)
                    source = txt_key_counts(ENGLISH / path.name)
                    for key, count in target.items():
                        if count > source[key]:
                            errors.append(f"{locale}/{path.name}: extra occurrence of key {key}")
                if by_file[path.name] == 0 and path.name not in ("[leveltracker] areas.json", "[leveltracker] gems.json"):
                    warnings.append(f"{locale}/{path.name}: built file has no translated records")
                if path.name == "[leveltracker] default guide.json":
                    guide_text = path.read_text(encoding="utf-8-sig")
                    for pattern, message in guide_render_antipatterns:
                        if pattern.search(guide_text):
                            errors.append(f"{locale}/{path.name}: {message}")
            except Exception as exc:
                errors.append(f"{locale}/{path.name}: {exc}")
    result = {"errors": errors, "warnings": warnings, "ok": not errors}
    write_json(REPORTS / "validate.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


def command_install(args: argparse.Namespace) -> None:
    source = PACKS / args.locale
    if not source.exists():
        raise SystemExit(f"pack not built: {source}")
    folder = args.folder_name or args.locale
    destination = ROOT / "data" / folder
    destination.mkdir(parents=True, exist_ok=True)
    copied = []
    for path in source.iterdir():
        if path.is_file():
            shutil.copy2(path, destination / path.name)
            copied.append(path.name)
    print(f"installed {len(copied)} files to {destination}: {', '.join(copied)}")


def command_progress(args: argparse.Namespace) -> None:
    report: dict[str, Any] = {}
    for locale in SUPPORTED:
        records = read_jsonl(TRANSLATIONS / f"{locale}.jsonl")
        files: dict[str, Any] = {}
        for name in sorted({x["file"] for x in records}):
            selected = [x for x in records if x["file"] == name]
            statuses = Counter(x.get("status", "untranslated") for x in selected)
            entry: dict[str, Any] = {"total": len(selected), "statuses": dict(statuses)}
            if name.startswith("[leveltracker] default guide"):
                acts = {}
                for act in sorted({x["path"][0] for x in selected}):
                    act_rows = [x for x in selected if x["path"][0] == act]
                    acts[str(act + 1)] = {"total": len(act_rows), "statuses": dict(Counter(x.get("status", "untranslated") for x in act_rows))}
                entry["acts"] = acts
            files[name] = entry
        report[locale] = files
    write_json(REPORTS / "progress.json", report)
    print(f"wrote {REPORTS / 'progress.json'}")


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    sync = sub.add_parser("sync", help="snapshot English baseline and merge translation memory")
    sync.set_defaults(func=command_sync)
    glossary = sub.add_parser("glossary", help="build the PoE1 glossary")
    glossary.add_argument("--poe-trans-data", required=True)
    glossary.set_defaults(func=command_glossary)
    export = sub.add_parser("export", help="export/update JSONL translation units")
    export.add_argument("--locale", choices=SUPPORTED, required=True)
    export.add_argument("--files", nargs="+", default=list(DEFAULT_FILES))
    export.set_defaults(func=command_export)
    legacy = sub.add_parser("import-legacy", help="import an existing language folder as unreviewed translation memory")
    legacy.add_argument("--locale", choices=SUPPORTED, required=True)
    legacy.add_argument("--source-dir", required=True)
    legacy.add_argument("--trust", action="store_true", help="mark imports translated instead of needs-review")
    legacy.set_defaults(func=command_import_legacy)
    curated = sub.add_parser("apply-curated", help="merge a reviewed translation batch into translation memory")
    curated.add_argument("--file", required=True)
    curated.set_defaults(func=command_apply_curated)
    build = sub.add_parser("build", help="build a language pack from reviewed units")
    build.add_argument("--locale", choices=SUPPORTED, required=True)
    build.add_argument("--allow-partial", action="store_true")
    build.set_defaults(func=command_build)
    validate = sub.add_parser("validate", help="validate placeholders and generated files")
    validate.set_defaults(func=command_validate)
    progress = sub.add_parser("progress", help="write per-file and per-act translation progress")
    progress.set_defaults(func=command_progress)
    install = sub.add_parser("install", help="copy a built pack into Exile UI data")
    install.add_argument("--locale", choices=SUPPORTED, required=True)
    install.add_argument("--folder-name")
    install.add_argument("--allow-incomplete", action="store_true")
    install.set_defaults(func=command_install)
    return result


def main() -> None:
    args = parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
