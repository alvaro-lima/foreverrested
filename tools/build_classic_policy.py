"""Compile factual catch-up data from pinned Questie literal tables.

Only the literal data block is parsed, in an empty Lua environment. Upstream
module code is never run. No quest prose, route ordering or runtime dependency
on Questie is imported. Requires lupa.lua51, like the addon's validation tools.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://github.com/Questie/Questie/tree/dd4b24e392e5bdd5d04d6dfb0c5c201e9de3d876/Database/Classic"
CLASSES = {1: "WARRIOR", 2: "PALADIN", 4: "HUNTER", 8: "ROGUE", 16: "PRIEST", 64: "SHAMAN", 128: "MAGE", 256: "WARLOCK", 1024: "DRUID"}
ZONES = {1: "Dun Morogh", 12: "Elwynn Forest", 38: "Loch Modan", 40: "Westfall", 44: "Redridge Mountains", 85: "Tirisfal Glades", 141: "Teldrassil", 148: "Darkshore", 215: "Mulgore", 14: "Durotar", 17: "The Barrens", 331: "Ashenvale", 406: "Stonetalon Mountains", 493: "Moonglade", 1519: "Stormwind City", 1537: "Ironforge", 1657: "Darnassus"}


def parse_literals(body, lua):
    tokens = re.sub(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' ''', "", body, flags=re.X)
    tokens = re.sub(r"\b(return|nil|true|false)\b", "", tokens)
    if re.search(r"[^\d\s\[\]{},.=;+-]", tokens):
        raise ValueError("Upstream data contains nonliteral code")
    parse = lua.eval("function(s) local fn=assert(loadstring(s)); setfenv(fn,{}); return fn() end")
    return parse(body)


def literal_table(path, field, lua):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"QuestieDB\." + field + r"\s*=\s*\[\[(return\s*\{.*?)\]\]", text, re.S)
    if not match:
        raise ValueError(f"Missing literal table {field}")
    body = match[1]
    return parse_literals(body, lua)


def balanced_table(text, start):
    depth, index = 0, start
    while index < len(text):
        if text[index] in "\"'":
            match = re.match(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' ''', text[index:], re.X)
            if not match:
                raise ValueError("Unclosed string in correction data")
            index += match.end()
            continue
        if text[index:index+2] == "--":
            index = text.find("\n", index)
            if index < 0:
                raise ValueError("Unclosed correction table")
            continue
        if text[index] == "{":
            depth += 1
        if text[index] == "}":
            depth -= 1
            if not depth:
                return text[start:index+1]
        index += 1
    raise ValueError("Unclosed correction table")


def apply_corrections(path, quests, lua):
    text = path.read_text(encoding="utf-8")
    # Extract only static, relevant fields. Ignore module code and runtime calls.
    main = text.split("function QuestieQuestFixes:LoadFactionFixes()")[0]
    alliance = text.split("local questFixesAlliance =", 1)[1] if "local questFixesAlliance =" in text else ""
    fields = {"name": 1, "startedBy": 2, "finishedBy": 3, "requiredLevel": 4,
              "questLevel": 5, "requiredRaces": 6, "requiredClasses": 7,
              "preQuestGroup": 12, "preQuestSingle": 13, "exclusiveTo": 16,
              "nextQuestInChain": 22, "parentQuest": 25}
    constants = {"raceIDs.HUMAN": 1, "raceIDs.ORC": 2, "raceIDs.DWARF": 4,
                 "raceIDs.NIGHT_ELF": 8, "raceIDs.UNDEAD": 16, "raceIDs.TAUREN": 32,
                 "raceIDs.GNOME": 64, "raceIDs.TROLL": 128,
                 "raceIDs.ALL_ALLIANCE": 77, "raceIDs.ALL_HORDE": 178, "raceIDs.ALL": 255, "raceIDs.NONE": 0}
    constants.update({"classIDs." + name: mask for mask, name in CLASSES.items()})
    constants["classIDs.NONE"] = 0
    applied, unsupported = 0, []
    for section in (main, alliance):
        for entry in re.finditer(r"^        \[(\d+)\]\s*=\s*(\{)", section, re.M):
            id = int(entry[1])
            block = balanced_table(section, entry.start(2))
            for field in re.finditer(r"\[questKeys\.(\w+)\]\s*=\s*", block):
                if field[1] not in fields:
                    continue
                start = field.end()
                if block[start] == "{":
                    value = balanced_table(block, start)
                else:
                    value = block[start:].split("\n", 1)[0].split("--", 1)[0].rstrip().rstrip(",")
                value = re.sub(r"--[^\n]*", "", value)
                for name, numeric in constants.items():
                    value = re.sub(r"\b" + re.escape(name) + r"\b", str(numeric), value)
                try:
                    parsed = parse_literals("return " + value, lua)
                except ValueError:
                    unsupported.append({"id": id, "field": field[1], "value": value})
                    continue
                if quests[id] is None:
                    quests[id] = lua.table()
                quests[id][fields[field[1]]] = parsed
                applied += 1
    # Questie's race-swap fix updates starters and next-chain links for 26/27;
    # reconcile the corresponding lake prerequisites with those corrected IDs.
    quests[29][13] = lua.table_from([26])
    quests[28][13] = lua.table_from([27])
    return applied, unsupported


def sequence(value):
    return [value[i] for i in range(1, len(value) + 1)] if value else []


def lua_literal(value):
    if isinstance(value, dict):
        return "{" + ",".join(f"[{lua_literal(k)}]={lua_literal(v)}" for k, v in value.items()) + "}"
    if isinstance(value, list):
        return "{" + ",".join(map(lua_literal, value)) + "}"
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r") + '"'
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def build(quest_path, npc_path, fixes_path):
    lua = LuaRuntime(unpack_returned_tuples=True)
    quests = literal_table(quest_path, "questData", lua)
    npcs = literal_table(npc_path, "npcData", lua)
    corrections, unsupported = apply_corrections(fixes_path, quests, lua)
    reference = json.loads((ROOT / "Data/alliance-reference.json").read_text())
    manifest = json.loads((ROOT / "Data/classic-unlocks.json").read_text())
    seeds = set(map(int, reference["quests"]))
    for unlock in manifest["unlocks"]:
        seeds.update(unlock["terminals"])
    # Include the full Alliance class-quest inventory by 20 for audit coverage,
    # without treating equipment rewards as essential ability unlocks.
    seeds.update(int(id) for id, q in quests.items() if q[7] and (q[4] or 99) <= 20 and (not q[6] or int(q[6]) & 77))
    records, missing = {}, set()

    def collect(id):
        if id in records or id in missing:
            return
        q = quests[id]
        if q is None:
            missing.add(id)
            return
        record = {"title": q[1], "minLevel": q[4] or 1, "level": q[5] or 1,
                  "requiredRaces": q[6] or 0,
                  "classes": [name for mask, name in CLASSES.items() if int(q[7] or 0) & mask],
                  "prerequisites": sequence(q[12]), "prerequisitesAny": sequence(q[13]),
                  "exclusiveTo": sequence(q[16]), "parentQuest": q[25] or 0,
                  "startItemIDs": sequence(q[2][3] if q[2] else None),
                  "rewards": [], "locations": [], "confidence": "vanilla-baseline"}
        records[id] = record
        for role, entities in (("start", q[2]), ("end", q[3])):
            for npc_id in sequence(entities[1] if entities else None):
                npc = npcs[npc_id]
                if npc and npc[7]:
                    for zone_id, points in sorted(npc[7].items()):
                        if zone_id in ZONES and len(points):
                            xy = points[1]
                            record["locations"].append({"role": role, "entityID": npc_id, "entityType": 1,
                                "name": npc[1], "zone": ZONES[zone_id], "areaID": zone_id,
                                "x": round(xy[1] / 100, 5), "y": round(xy[2] / 100, 5), "approximate": True})
        for prior in record["prerequisites"] + record["prerequisitesAny"] + record["exclusiveTo"]:
            collect(prior)
        if record["parentQuest"] > 0:
            collect(record["parentQuest"])

    for id in sorted(seeds):
        collect(id)
    relevant_unsupported = [entry for entry in unsupported if entry["id"] in records]
    if relevant_unsupported:
        raise ValueError(f"Review nonliteral corrections before importing: {relevant_unsupported}")
    output = "local _, F = ...\n-- Generated factual subset; see Data/QUEST_POLICY.md for attribution and rebuild.\n"
    output += "F.ClassicQuestPolicy = {source=" + lua_literal(SOURCE) + ",records={\n"
    output += "\n".join(f"[{id}]={lua_literal(records[id])}," for id in sorted(records))
    output += "\n},unlocks=" + lua_literal(manifest["unlocks"]) + "}\n"
    (ROOT / "Data/ClassicQuestPolicy.lua").write_text(output, encoding="utf-8")
    report = {"scope": manifest["scope"], "source": SOURCE,
              "questDBSHA256": hashlib.sha256(quest_path.read_bytes()).hexdigest(),
              "npcDBSHA256": hashlib.sha256(npc_path.read_bytes()).hexdigest(),
              "correctionsSHA256": hashlib.sha256(fixes_path.read_bytes()).hexdigest(),
              "correctionFieldsImported": corrections,
              "unsupportedCorrectionsOutsideScope": unsupported,
              "records": len(records), "unlockGroups": len(manifest["unlocks"]),
              "referenceQuests": len(reference["quests"]),
              "noVanillaRecord": sorted(missing),
              "sources": manifest["sources"]}
    (ROOT / "Data/classic-policy-coverage.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Compiled {len(records)} factual records and {len(manifest['unlocks'])} unlock groups; {len(missing)} IDs have no Vanilla record")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quest-db", type=Path, required=True)
    parser.add_argument("--npc-db", type=Path, required=True)
    parser.add_argument("--corrections", type=Path, required=True)
    args = parser.parse_args()
    build(args.quest_db, args.npc_db, args.corrections)
