"""Playable quest NPC pins agree with installed Forever QuestieDB where present."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_questie_npc_locations import audit

report = audit()
assert report['counts']['quests'] >= 700
assert report['counts']['checkedSpawns'] >= 3100
unsupported = [row for row in report['issues'] if row['kind'] not in
               ('npc-absent-from-questie', 'npc-has-no-questie-spawn', 'classic-fallback')]
assert not unsupported, unsupported[:10]
assert report['counts']['classicFallbackPins'] == 14
print(f"PASS: {report['counts']['checkedSpawns']} NPC pins match Questie; "
      f"{report['counts']['classicFallbackPins']} have labeled Classic fallback evidence")
