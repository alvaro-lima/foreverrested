"""Validate/merge Forever observation exports; generate a small Lua catalog offline.

Uses Python's standard library. No executable Lua or remote downloads are accepted.
Existing entries survive partial refreshes, with their original build stamp.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {
    "questID", "title", "questLevel", "requiredLevel", "requiredRaces", "requiredClasses",
    "zone", "buildKey", "confidence", "lastSeen", "objectives", "rewardXPObserved",
    "guaranteedRewards", "choiceRewards", "prerequisites", "followups", "locations",
    "baseRewardXP", "evidence",
}


def number(value, label, minimum=0, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label}: expected a finite number")
    if value < minimum or (integer and value != int(value)):
        raise ValueError(f"{label}: invalid value {value}")
    return value


def bounded(value, depth=0):
    if depth > 12:
        raise ValueError("Data nested too deeply")
    if isinstance(value, str) and len(value) > 2048:
        raise ValueError("String exceeds 2048 characters")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Non-finite number")
    if isinstance(value, dict):
        if len(value) > 200:
            raise ValueError("Record too large")
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("JSON object keys must be strings")
            bounded(key, depth + 1)
            bounded(item, depth + 1)
    elif isinstance(value, list):
        if len(value) > 200:
            raise ValueError("Record array too large")
        for item in value:
            bounded(item, depth + 1)


def validate(document):
    if not isinstance(document, dict):
        raise ValueError("Input document must be an object")
    if type(document.get("schemaVersion")) is not int or document.get("schemaVersion") != 1:
        raise ValueError("Unsupported schemaVersion")
    source = document.get("source", {})
    if not isinstance(source, dict) or source.get("game") != "forever":
        raise ValueError("Source must explicitly identify game=forever")
    build = source.get("buildKey")
    if not isinstance(build, str) or not build or "unknown" in build.lower():
        raise ValueError("Source must provide a known client buildKey")
    bounded(source)
    quests = document.get("quests")
    if not isinstance(quests, list) or len(quests) > 10000:
        raise ValueError("quests must be an array with at most 10000 entries")
    result = {}
    for record in quests:
        if not isinstance(record, dict):
            raise ValueError("Quest records must be objects")
        bounded(record)
        unknown = set(record) - FIELDS
        if unknown:
            raise ValueError(f"Unknown quest fields: {sorted(unknown)}")
        quest_id = number(record.get("questID"), "questID", 1, True)
        if str(int(quest_id)) in result:
            raise ValueError(f"Duplicate questID {quest_id}")
        if record.get("buildKey") != build:
            raise ValueError(f"Quest {quest_id}: buildKey does not match input source")
        if record.get("confidence") not in ("observed", "sourced", "estimated", "verified"):
            raise ValueError(f"Quest {quest_id}: missing confidence")
        if record.get("confidence") != "observed" and not record.get("evidence"):
            raise ValueError(f"Quest {quest_id}: non-observed data requires evidence")
        for field in ("questLevel", "requiredLevel", "requiredRaces", "requiredClasses", "baseRewardXP"):
            if field in record:
                number(record[field], field, -1 if field == "questLevel" else 0, True)
        if "baseRewardXP" in record and not record.get("evidence"):
            raise ValueError("Base XP requires evidence; observed reward XP is level-specific")
        for field in ("objectives", "guaranteedRewards", "choiceRewards", "locations", "prerequisites", "followups"):
            if field in record and not isinstance(record[field], list):
                raise ValueError(f"{field} must be an array")
        for objective in record.get("objectives", []):
            if not isinstance(objective, dict):
                raise ValueError("Objective must be an object")
            number(objective.get("index"), "objective index", 1, True)
            if "required" in objective:
                number(objective["required"], "objective required", 0, True)
        for field in ("guaranteedRewards", "choiceRewards"):
            for item in record.get(field, []):
                if not isinstance(item, dict):
                    raise ValueError("Reward must be an object")
                number(item.get("itemID"), "itemID", 1, True)
                for key in ("quality", "quantity", "itemLevel", "requiredLevel"):
                    if key in item:
                        number(item[key], key, 0, True)
        for location in record.get("locations", []):
            if not isinstance(location, dict):
                raise ValueError("Location must be an object")
            number(location.get("mapID"), "mapID", 1, True)
            for axis in ("x", "y"):
                if number(location.get(axis), axis) > 1:
                    raise ValueError("Coordinates must be normalized 0–1")
        for field in ("prerequisites", "followups"):
            for quest in record.get(field, []):
                number(quest, field, 1, True)
        reward = record.get("rewardXPObserved")
        if reward is not None:
            if not isinstance(reward, dict) or reward.get("buildKey") != build:
                raise ValueError("Reward XP requires matching build evidence")
            number(reward.get("value"), "observed reward XP")
            if "playerLevel" in reward:
                number(reward["playerLevel"], "reward playerLevel", 1, True)
        result[str(int(quest_id))] = record
    return source, result


def lua(value):
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        number(value, "Lua number", -math.inf)
        return str(value)
    if isinstance(value, str):
        # Decimal byte escapes preserve UTF-8 and cannot inject Lua source.
        return '"' + ''.join(f"\\{byte:03d}" for byte in value.encode("utf-8")) + '"'
    if isinstance(value, list):
        return "{" + ",".join(lua(item) for item in value) + "}"
    if isinstance(value, dict):
        return "{" + ",".join(f"[{lua(key)}]={lua(item)}" for key, item in sorted(value.items())) + "}"
    raise ValueError("Unsupported value")


def merge(document, previous=None):
    source, incoming = validate(document)
    previous = previous or {"revision": 0, "quests": {}}
    quests = dict(previous["quests"])
    changes = []
    for quest_id, record in sorted(incoming.items(), key=lambda item: int(item[0])):
        old = quests.get(quest_id)
        # Within the same build, preserve unobserved fields from earlier evidence.
        merged = {**old, **record} if old and old.get("buildKey") == record["buildKey"] else record
        if old != merged:
            fields = sorted(key for key in set(old or {}) | set(merged) if (old or {}).get(key) != merged.get(key))
            changes.append(f"- Quest {quest_id}: {'added' if old is None else 'changed ' + ', '.join(fields)}")
        quests[quest_id] = merged
    changed = bool(changes) or previous.get("source") != source
    result = {"schemaVersion": 1, "revision": previous["revision"] + int(changed),
              "source": source, "quests": quests}
    stale = sum(record.get("buildKey") != source["buildKey"] for record in quests.values())
    report = "# Quest data refresh\n\n" + f"Revision: {result['revision']}\n\nClient: {source['buildKey']}\n\n"
    report += f"Imported: {len(incoming)}; retained total: {len(quests)}; stale: {stale}.\n\n"
    report += "Missing quests in a partial export are retained, not assumed removed. Stale records are not current-build evidence.\n\n"
    report += "\n".join(changes) if changes else "No quest records changed.\n"
    return result, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--check", action="store_true", help="Validate and preview changes without writing")
    args = parser.parse_args()
    if args.input.stat().st_size > 20_000_000:
        raise ValueError("Input exceeds 20 MB")
    document = json.loads(args.input.read_text(encoding="utf-8-sig"))
    destination = ROOT / "Data"
    state = destination / "quest-catalog.json"
    previous = json.loads(state.read_text(encoding="utf-8")) if state.exists() else None
    catalog, report = merge(document, previous)
    print(report)
    if args.check:
        return
    destination.mkdir(exist_ok=True)
    outputs = {
        state: json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        destination / "QuestCatalog.lua": "local _, F = ...\n-- Generated offline; no runtime dependency.\nF.QuestCatalog = " + lua(catalog) + "\n",
        destination / "REFRESH_REPORT.md": report + "\n",
    }
    for path, contents in outputs.items():
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(contents, encoding="utf-8")
        temporary.replace(path)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        raise SystemExit(f"Refresh rejected: {error}")
