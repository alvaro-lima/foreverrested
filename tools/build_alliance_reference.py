"""Extract factual quest/reward/location fields from cached public Forever pages.

No guide prose or route ordering is imported. The Lua routes are authored separately.
Fetch pages into a cache outside the addon, then pass --cache. No remote code executes.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CLASSES = {"warrior": "WARRIOR", "paladin": "PALADIN", "hunter": "HUNTER", "rogue": "ROGUE",
           "priest": "PRIEST", "shaman": "SHAMAN", "mage": "MAGE", "warlock": "WARLOCK", "druid": "DRUID"}
STAT_KEYS = {"armor", "agi", "int", "sta", "spi", "str", "dps", "mlespeed", "dmgmin1", "dmgmax1",
             "reqlevel", "slotbak", "reqclass", "reqrace", "reqskill", "reqskillrank", "classs", "subclass"}


def decode_after(text, marker):
    position = text.find(marker)
    if position < 0:
        return None
    return json.JSONDecoder().raw_decode(text[position + len(marker):].lstrip())[0]


def quest_list(text):
    result = []
    for match in re.finditer("new Listview", text):
        header = text[match.start():match.start() + 120]
        if "template: 'quest'" in header or 'template: "quest"' in header:
            data = decode_after(text[match.start():], "data:")
            if isinstance(data, list):
                result.extend(data)
    return result


def extract(quest_id, text, class_index):
    raw = decode_after(text, f"$.extend(g_quests[{quest_id}], ")
    if not isinstance(raw, dict) or raw.get("id") != quest_id:
        raise ValueError(f"Quest {quest_id}: missing Forever quest metadata")
    record = {"questID": quest_id, "title": raw["name"], "level": raw.get("level"),
              "minLevel": raw.get("reqlevel"), "side": raw.get("side"),
              "requiredClasses": raw.get("reqclass", 0), "classes": sorted(class_index.get(quest_id, [])),
              "requiredRaces": raw.get("reqrace", raw.get("race", 0)),
              "listedXP": raw.get("xp"), "locations": [], "rewards": [],
              "source": f"https://www.wowhead.com/forever/quest={quest_id}", "confidence": "sourced"}
    scaling = decode_after(text, "WH.Wow.Quest.setupScalingRewards(")
    if scaling:
        record["xpScaling"] = scaling.get("xp")
    mapper = decode_after(text, "new Mapper(") or {}
    for area, value in mapper.get("objectives", {}).items():
        for floor in value.get("levels", []):
            for point in floor:
                coord = point.get("coord")
                if not isinstance(coord, list) or len(coord) != 2:
                    continue
                location = {"areaID": int(area), "zone": value.get("zone"), "role": point.get("point"),
                            "name": point.get("name"), "entityID": point.get("id"), "entityType": point.get("type"),
                            "x": coord[0] / 100, "y": coord[1] / 100, "approximate": True}
                if point.get("item"):
                    location["item"] = point["item"]
                if location["role"] in ("start", "end", "requirement", "sourcerequirement"):
                    record["locations"].append(location)
    item_data = {}
    for match in re.finditer(r"WH\.Gatherer\.addData\(3,\s*16,\s*", text):
        data = json.JSONDecoder().raw_decode(text[match.end():].lstrip())[0]
        item_data.update(data)
    for field, kind in (("itemchoices", "choice"), ("itemrewards", "guaranteed")):
        for item_id, quantity in raw.get(field, []):
            item = item_data.get(str(item_id), {})
            stats = {key: value for key, value in item.get("jsonequip", {}).items() if key in STAT_KEYS}
            record["rewards"].append({"itemID": item_id, "quantity": quantity, "kind": kind,
                                      "name": item.get("name_enus"), "quality": item.get("quality"), "stats": stats})
    # Listed series is retained as evidence, not asserted to be a complete prerequisite graph.
    position = text.find("Series")
    if position >= 0:
        section = text[position:text.find("Screenshots", position)]
        record["series"] = list(dict.fromkeys(int(match) for match in re.findall(r'/forever/quest=(\d+)', section)))
    return {key: value for key, value in record.items() if value is not None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, required=True)
    args = parser.parse_args()
    class_index = {}
    for name, token in CLASSES.items():
        path = args.cache / (name + "-list.html")
        if path.exists():
            for quest in quest_list(path.read_text(encoding="utf-8")):
                if quest.get("side") in (1, 3):
                    class_index.setdefault(quest["id"], set()).add(token)
    records, checksums = {}, {}
    for path in sorted(args.cache.glob("*.html")):
        if not path.stem.isdigit():
            continue
        quest_id = int(path.stem)
        records[quest_id] = extract(quest_id, path.read_text(encoding="utf-8"), class_index)
        records[quest_id]["retrievedAt"] = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
        checksums[str(quest_id)] = hashlib.sha256(path.read_bytes()).hexdigest()
    # Zone summaries remain useful when an individual page is unavailable. Never
    # fabricate objective locations, chains or equipment stats from a summary.
    for name in ("westfall", "loch-modan", "darkshore", "redridge-mountains", "zephras"):
        path = args.cache / (name + "-list.html")
        if not path.exists():
            continue
        for raw in quest_list(path.read_text(encoding="utf-8")):
            quest_id = raw["id"]
            if quest_id in records or raw.get("side") not in (1, 3) or not 1 <= raw.get("level", 99) <= 23:
                continue
            rewards = []
            for field, kind in (("itemchoices", "choice"), ("itemrewards", "guaranteed")):
                for item_id, quantity in raw.get(field, []):
                    rewards.append({"itemID": item_id, "quantity": quantity, "kind": kind, "stats": {}})
            records[quest_id] = {"questID": quest_id, "title": raw["name"], "level": raw.get("level"),
                "minLevel": raw.get("reqlevel", 1), "side": raw["side"],
                "requiredClasses": raw.get("reqclass", 0), "classes": sorted(class_index.get(quest_id, [])),
                "requiredRaces": raw.get("reqrace", 0), "listedXP": raw.get("xp"),
                "locations": [], "rewards": rewards, "source": "https://www.wowhead.com/forever/zone=" + str(raw.get("category", 0)),
                "confidence": "sourced-summary", "missing": ["individual-page", "locations", "reward-stats"],
                "retrievedAt": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}
            checksums[str(quest_id)] = hashlib.sha256(path.read_bytes()).hexdigest()
    spec = importlib.util.spec_from_file_location("refresh", ROOT / "tools/refresh_quest_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    output = {"schemaVersion": 1, "compiledAt": datetime.now(timezone.utc).isoformat(),
              "game": "forever", "kind": "public-reference-not-live-build-verified",
              "checksums": checksums, "quests": {str(key): value for key, value in sorted(records.items())}}
    (ROOT / "Data/alliance-reference.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lua_records = "{" + ",\n".join(f"[{key}]={module.lua(value)}" for key, value in sorted(records.items())) + "}"
    (ROOT / "Guides/AllianceQuestData.lua").write_text(
        "local _, F = ...\n-- Public Forever factual reference; coordinates/XP are approximate and build-unverified.\n"
        "F.AllianceZoneMaps = {['Dun Morogh']=1426, ['Elwynn Forest']=1429, Teldrassil=1438, Westfall=1436, ['Loch Modan']=1432, Darkshore=1439, ['Redridge Mountains']=1433}\n"
        "F.AllianceQuestData = " + lua_records + "\n", encoding="utf-8")
    print(f"Extracted {len(records)} quest references. No third-party route ordering or quest prose imported.")


if __name__ == "__main__":
    main()
