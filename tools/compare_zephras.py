"""Compare island exit policies using sourced listed XP and explicit rough assumptions.

This is an advisory offline calculation, not a level projection or live optimizer.
"""
import argparse
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def positive(value, name, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or (not allow_zero and value == 0):
        raise ValueError(f"Invalid {name}")
    return value


def compare(data, reference):
    if len(data["clusters"]) != 2:
        raise ValueError("Exit comparison requires exactly two island clusters")
    horizon = positive(data["evaluationXP"], "evaluationXP")
    factor = positive(data["rewardFactor"], "rewardFactor", True)
    seen, clusters = set(), []
    for cluster in data["clusters"]:
        xp = 0
        for quest_id in cluster["questIDs"]:
            if quest_id in seen:
                raise ValueError("Quest reward counted twice")
            seen.add(quest_id)
            quest = reference[str(quest_id)]
            if quest.get("side") == 2:
                raise ValueError("Horde quest in Alliance comparison")
            if quest.get("listedXP") is None:
                raise ValueError(f"Missing XP for {quest_id}; cannot rank this cluster")
            xp += positive(quest["listedXP"], "listedXP", True)
        kill_xp = positive(cluster["estimatedKills"], "estimatedKills", True) * positive(cluster["assumedXPPerKill"], "assumedXPPerKill", True)
        clusters.append({**cluster, "rewardXP": xp * factor, "killXP": kill_xp, "totalXP": xp * factor + kill_xp})
    if sum(c["totalXP"] for c in clusters) > horizon:
        raise ValueError("Evaluation XP must cover the complete compared island work")
    policies = []
    for count, label in enumerate(("Leave now (level-10 review)", "Leave after first cluster (level-12 review)", "Stay for later cluster (up-to-14 review)")):
        used = clusters[:count]
        earned = sum(c["totalXP"] for c in used)
        policy = {"policy": label, "islandXP": earned, "scenarios": {}}
        for mode in ("expected", "slow"):
            rate = positive(data["mainlandXPPerMinute"][mode], "mainlandXPPerMinute")
            travel = positive(data["travelMinutes"][mode], "travelMinutes", True)
            minutes = sum(positive(c["activeMinutes"][mode], "activeMinutes") for c in used)
            policy["scenarios"][mode] = {"minutes": minutes + travel + (horizon-earned)/rate,
                "islandMinutes": minutes, "mainlandMinutes": (horizon-earned)/rate, "travelMinutes": travel}
        policies.append(policy)
    return {"assumptions": data, "clusters": clusters, "policies": policies,
        "limits": ["No measured optimal exit level.", "Reviews at 10/12/14 do not predict the level reached by a cluster.",
                   "Listed XP uses an explicit reward factor, not verified beta level scaling.",
                   "Kills, active times and mainland XP/minute are assumed; class, gear, competition and deaths change the result.",
                   "Transport must actually be available; its common cost is charged once in each policy.",
                   "Optional chain availability and equipment upgrades are not valued by this calculation."]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "Data/zephras-comparison-input.json")
    parser.add_argument("--output", type=Path, default=ROOT / "Data/ZEPHRAS_COMPARISON.json")
    args = parser.parse_args()
    result = compare(json.loads(args.input.read_text()), json.loads((ROOT / "Data/alliance-reference.json").read_text())["quests"])
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for policy in result["policies"]:
        print(f"{policy['policy']}: expected {policy['scenarios']['expected']['minutes']:.1f} min; slow {policy['scenarios']['slow']['minutes']:.1f} min")
    for cluster in result["clusters"]:
        print(f"{cluster['title']}: listed reward XP {cluster['rewardXP']:.0f}, assumed kill XP {cluster['killXP']:.0f}; break-even mainland rate {cluster['totalXP']/cluster['activeMinutes']['expected']:.0f} XP/min")


if __name__ == "__main__":
    main()
