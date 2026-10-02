"""Offline Forever quest-cluster estimates; no implicit XP formulas or client APIs."""
import argparse
import json
import math
from pathlib import Path


def numeric(value, name, positive=False, integer=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{name}: expected a finite number")
    if value < 0 or (positive and value == 0) or (integer and int(value) != value):
        raise ValueError(f"{name}: invalid value")
    return value


def scenario(value, mode, name, lower_is_slower=False, positive=False):
    if isinstance(value, dict):
        expected = numeric(value.get("expected"), name + ".expected", positive)
        slow = numeric(value.get("slow"), name + ".slow", positive)
        if (slow > expected if lower_is_slower else slow < expected):
            raise ValueError(f"{name}: slow scenario has the wrong direction")
        return expected if mode == "expected" else slow
    return numeric(value, name, positive)


def estimate(cluster, profile, mode="expected"):
    missing, notes = [], []
    mobs = profile.get("mobs", {})
    groups, quests, legs = {}, set(), {}
    reward_xp, kill_xp, travel, combat, overhead, interaction = 0, 0, 0, 0, 0, 0
    level = numeric(profile.get("level"), "profile.level", positive=True, integer=True)
    for quest in cluster.get("quests", []):
        quest_id = quest["questID"]
        numeric(quest_id, "questID", positive=True, integer=True)
        if quest_id in quests:
            raise ValueError(f"Duplicate quest {quest_id} within cluster")
        quests.add(quest_id)
        reward = quest.get("reward")
        if not isinstance(reward, dict) or reward.get("playerLevel") != level:
            missing.append(f"Quest {quest_id}: reward XP at player level {level}")
        elif "xp" not in reward:
            missing.append(f"Quest {quest_id}: reward XP")
        else:
            reward_xp += numeric(reward["xp"], "quest reward XP")
        if "interactionSeconds" not in quest:
            missing.append(f"Quest {quest_id}: pickup/turn-in interaction time")
        else:
            interaction += scenario(quest["interactionSeconds"], mode, "interactionSeconds")
        for index, objective in enumerate(quest.get("objectives", [])):
            remaining = numeric(objective.get("remaining"), "remaining", integer=True)
            if remaining == 0:
                continue
            mob = objective.get("mob")
            if not isinstance(mob, str) or not mob:
                raise ValueError("Unfinished combat objectives need a mob key")
            kind = objective.get("kind")
            if kind not in ("kill", "collect"):
                raise ValueError("Only kill/collect objectives are currently supported")
            kills = remaining
            if kind == "collect":
                if "dropChance" not in objective or "itemsPerDrop" not in objective:
                    missing.append(f"Quest {quest_id}: drop chance/items per drop for {mob}")
                    continue
                chance = scenario(objective["dropChance"], mode, "dropChance", True, True)
                if chance > 1:
                    raise ValueError("dropChance must be between 0 and 1")
                items = numeric(objective["itemsPerDrop"], "itemsPerDrop", positive=True)
                kills = math.ceil(remaining / (chance * items))
            shared = objective.get("shareGroup")
            if shared is not None and (not isinstance(shared, str) or not shared):
                raise ValueError("shareGroup must be a nonempty string")
            key = ("shared", shared) if shared else ("individual", quest_id, index)
            previous = groups.get(key)
            if previous and previous["mob"] != mob:
                raise ValueError("Shared objective group cannot combine different mobs")
            groups[key] = {"mob": mob, "kills": max(kills, previous["kills"] if previous else 0)}
            if shared and kind == "collect":
                notes.append("Shared collection kills use the maximum individual estimate; this is approximate, not an exact joint-drop expectation.")
    kills_by_mob = {}
    for group in groups.values():
        mob, kills = group["mob"], group["kills"]
        kills_by_mob[mob] = kills_by_mob.get(mob, 0) + kills
        model = mobs.get(mob, {})
        for field in ("combatSeconds", "findLootRecoverySeconds", "xpPerKill"):
            if field not in model:
                missing.append(f"{mob}: {field} for this player profile")
        if "combatSeconds" in model:
            combat += kills * scenario(model["combatSeconds"], mode, mob + " combatSeconds", positive=True)
        if "findLootRecoverySeconds" in model:
            overhead += kills * scenario(model["findLootRecoverySeconds"], mode, mob + " findLootRecoverySeconds")
        if "xpPerKill" in model:
            kill_xp += kills * numeric(model["xpPerKill"], "xpPerKill")
    for leg in cluster.get("travel", []):
        key = leg.get("id")
        if not isinstance(key, str) or not key:
            raise ValueError("Travel legs need stable IDs")
        if key in legs:
            if legs[key] != leg:
                raise ValueError("Repeated travel leg has conflicting data")
            continue
        legs[key] = leg
        if "seconds" in leg and "distanceYards" in leg:
            raise ValueError("Travel legs accept time or distance, not both")
        if "seconds" in leg:
            travel += scenario(leg["seconds"], mode, "travel seconds")
        elif "distanceYards" in leg:
            if leg.get("pathKind") != "walkable":
                missing.append(f"Travel {key}: walkable path distance")
                continue
            if "movementYardsPerSecond" not in profile:
                missing.append("Player movement speed")
                continue
            speed = scenario(profile["movementYardsPerSecond"], mode, "movement speed", True, True)
            travel += numeric(leg["distanceYards"], "distanceYards") / speed
        else:
            missing.append(f"Travel {key}: duration or walkable distance")
    # Requiring an explicit list distinguishes a genuinely travel-free cluster from missing data.
    if "travel" not in cluster:
        missing.append("Cluster pickup/objective/turn-in travel")
    if not quests:
        missing.append("Cluster quests")
    total_seconds = travel + combat + overhead + interaction
    total_xp = reward_xp + kill_xp
    missing = sorted(set(missing))
    complete = not missing and total_seconds > 0
    return {"scenario": mode, "complete": complete, "missing": missing,
            "notes": sorted(set(notes)), "expectedKills": kills_by_mob,
            "questXP": reward_xp, "killXP": kill_xp, "totalXP": total_xp if not missing else None,
            "seconds": total_seconds if not missing else None,
            "breakdownSeconds": {"travel": travel, "combat": combat, "findLootRecovery": overhead, "interaction": interaction},
            "xpPerMinute": total_xp * 60 / total_seconds if complete else None}


def compare(document):
    if not isinstance(document, dict) or type(document.get("schemaVersion")) is not int or document["schemaVersion"] != 1:
        raise ValueError("Expected schemaVersion=1")
    if document.get("game") != "forever":
        raise ValueError("Explicit game=forever is required")
    profile = document["profile"]
    if not profile.get("class") or not profile.get("buildKey"):
        raise ValueError("Player class and buildKey are required")
    output, used = [], set()
    for cluster in document["clusters"]:
        identity = cluster.get("id")
        if not isinstance(identity, str) or not identity or identity in used:
            raise ValueError("Clusters require unique string IDs")
        used.add(identity)
        if cluster.get("buildKey") != profile["buildKey"]:
            raise ValueError(f"Cluster {identity}: stale/mismatched client build")
        expected, slow = estimate(cluster, profile), estimate(cluster, profile, "slow")
        output.append({"id": identity, "title": cluster.get("title", identity), "expected": expected, "slow": slow})
    output.sort(key=lambda row: (row["expected"]["xpPerMinute"] is None, -(row["expected"]["xpPerMinute"] or 0), row["id"]))
    return {"schemaVersion": 1, "buildKey": profile["buildKey"], "playerLevel": profile["level"],
            "kind": "estimates", "clusters": output}


def report(result):
    lines = ["# Quest-cluster estimates", "", f"Build: {result['buildKey']} | Player level: {result['playerLevel']}", "",
             "Estimates only. The slow scenario uses supplied conservative inputs; it is not a statistical percentile.", "",
             "| Cluster | Expected min | Expected XP | XP/min | Slow min |", "|---|---:|---:|---:|---:|"]
    for row in result["clusters"]:
        expected, slow = row["expected"], row["slow"]
        title = str(row["title"]).replace("|", "/").replace("\n", " ")
        if expected["complete"]:
            lines.append(f"| {title} | {expected['seconds']/60:.1f} | {expected['totalXP']:.0f} | {expected['xpPerMinute']:.1f} | {slow['seconds']/60:.1f} |")
        else:
            lines.append(f"| {title} | Unknown | Unknown | Unranked | Unknown |")
    for row in result["clusters"]:
        if row["expected"]["missing"]:
            lines.extend(["", f"{row['id']} missing: " + "; ".join(row["expected"]["missing"])])
        for note in row["expected"]["notes"]:
            lines.extend(["", f"{row['id']}: {note}"])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--json", action="store_true", help="Print structured estimates instead of Markdown")
    args = parser.parse_args()
    result = compare(json.loads(args.input.read_text(encoding="utf-8-sig")))
    print(json.dumps(result, indent=2, ensure_ascii=False) if args.json else report(result), end="\n" if args.json else "")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        raise SystemExit(f"Estimate rejected: {error}")
