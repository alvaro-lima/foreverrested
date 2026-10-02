"""Hand-calculated estimator scenarios and meaningful failure cases."""
import copy
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("estimator", ROOT / "tools/estimate_routes.py")
estimator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(estimator)
example = json.loads((ROOT / "Data/estimate-example.json").read_text())
result = estimator.compare(example)
shared, isolated = result["clusters"]
assert shared["id"] == "shared"
assert shared["expected"]["expectedKills"] == {"example-mob": 12}
assert shared["expected"]["seconds"] == 720
assert shared["expected"]["totalXP"] == 2400
assert shared["expected"]["xpPerMinute"] == 200
assert isolated["expected"]["xpPerMinute"] == 60
assert shared["slow"]["expectedKills"] == {"example-mob": 18}
assert shared["slow"]["seconds"] == 1212
assert shared["expected"]["notes"]

def modified():
    return copy.deepcopy(example)

unshared = modified()
for quest in unshared["clusters"][1]["quests"]:
    quest["objectives"][0].pop("shareGroup")
assert estimator.estimate(unshared["clusters"][1], unshared["profile"])["expectedKills"]["example-mob"] == 30
multi = modified()
multi["clusters"][1]["quests"][1]["objectives"][0]["itemsPerDrop"] = 2
assert estimator.estimate(multi["clusters"][1], multi["profile"])["expectedKills"]["example-mob"] == 10
travel = modified()
leg = {"id": "path", "distanceYards": 700, "pathKind": "walkable"}
travel["clusters"][0]["travel"] = [leg, leg]
assert estimator.estimate(travel["clusters"][0], travel["profile"])["breakdownSeconds"]["travel"] == 100
assert estimator.estimate(travel["clusters"][0], travel["profile"], "slow")["breakdownSeconds"]["travel"] == 140
travel["clusters"][0]["travel"][0]["pathKind"] = "straight-line"
assert estimator.estimate(travel["clusters"][0], travel["profile"])["xpPerMinute"] is None
missing = modified()
missing["clusters"][1]["quests"][1]["objectives"][0].pop("dropChance")
assert estimator.compare(missing)["clusters"][-1]["expected"]["totalXP"] is None
level = modified()
level["profile"]["level"] = 8
assert all(row["expected"]["xpPerMinute"] is None for row in estimator.compare(level)["clusters"])
completed = modified()
for quest in completed["clusters"][1]["quests"]:
    quest["objectives"][0]["remaining"] = 0
assert estimator.estimate(completed["clusters"][1], completed["profile"])["killXP"] == 0
for mutation in ("stale", "zero-drop", "negative-time", "wrong-share", "duplicate-quest", "reverse-scenario"):
    bad = modified()
    cluster = bad["clusters"][1]
    if mutation == "stale":
        cluster["buildKey"] = "old"
    elif mutation == "zero-drop":
        cluster["quests"][1]["objectives"][0]["dropChance"] = 0
    elif mutation == "negative-time":
        bad["profile"]["mobs"]["example-mob"]["combatSeconds"] = -1
    elif mutation == "wrong-share":
        cluster["quests"][1]["objectives"][0]["mob"] = "different"
    elif mutation == "duplicate-quest":
        cluster["quests"].append(cluster["quests"][0])
    else:
        bad["profile"]["movementYardsPerSecond"] = {"expected": 7, "slow": 8}
        cluster["travel"] = [{"id": "path", "distanceYards": 700, "pathKind": "walkable"}]
    try:
        estimator.compare(bad)
    except ValueError:
        pass
    else:
        raise AssertionError(f"Accepted invalid {mutation} input")
assert "Unranked" in estimator.report(estimator.compare(missing))
print("PASS: XP/time arithmetic, shared objectives/travel, collection drops, slow scenarios, remaining progress, level/build guards and missing-data handling.")
