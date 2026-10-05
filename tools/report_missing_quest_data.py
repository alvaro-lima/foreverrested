"""List playable quests whose records or NPC spawns lack Questie confirmation."""
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
classic = json.loads((ROOT / 'Data/CLASSIC_NPC_FALLBACK_AUDIT.json').read_text(encoding='utf-8'))
npc = json.loads((ROOT / 'Data/QUESTIE_NPC_LOCATION_AUDIT.json').read_text(encoding='utf-8'))
missing_records = {row['questID']: row for row in classic['questCandidates']}
missing_pins = defaultdict(list)
titles = {}
for row in npc['issues']:
    titles[row['questID']] = row.get('questTitle') or titles.get(row['questID'])
    if row['kind'] == 'npc-absent-from-questie':
        missing_pins[row['questID']].append(row)

lines = [
    '# Playable quests missing Questie confirmation', '',
    'A missing Questie record is **not** proof that the quest is absent from Forever. '
    'These quests have authored guide records; their game availability and details need live confirmation. '
    'A missing NPC pin means the installed Forever QuestieDB cannot confirm that recorded NPC spawn.', '',
    f'## No installed Forever Questie quest record ({len(missing_records)})', '',
    '| Quest ID | Authored title | Unverified NPC pins |', '| ---: | --- | ---: |',
]
for quest_id, row in sorted(missing_records.items()):
    title = row.get('recordedTitle') or titles.get(quest_id) or 'Title absent from reference export'
    lines.append(f"| {quest_id} | {title.replace('|', '&#124;')} | {len(missing_pins.get(quest_id, []))} |")
lines += ['', f'## Quest with unverified NPC spawns ({len(missing_pins)})', '',
          '| Quest ID | Authored title | Missing pins |', '| ---: | --- | ---: |']
for quest_id, rows in sorted(missing_pins.items()):
    title = missing_records.get(quest_id, {}).get('recordedTitle') or titles.get(quest_id) or 'Title absent from reference export'
    lines.append(f"| {quest_id} | {title.replace('|', '&#124;')} | {len(rows)} |")
lines += ['', 'The full pin-level details, including NPC IDs and roles, are in '
          '`QUESTIE_NPC_LOCATION_AUDIT.json`. Anniversary fallback evidence is listed separately '
          'in `CLASSIC_NPC_FALLBACK_EVIDENCE.json`.', '']
output = ROOT / 'Data/MISSING_QUEST_SOURCE_DATA.md'
output.write_text('\n'.join(lines), encoding='utf-8')
print(f'{len(missing_records)} quests without Forever Questie quest records; '
      f'{len(missing_pins)} quests with {sum(map(len, missing_pins.values()))} unverified NPC pins')
