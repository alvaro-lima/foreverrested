"""Find Classic Era Questie evidence for NPC pins missing Forever Questie evidence."""
import json
import re
import hashlib
from pathlib import Path

from read_installed_questie import InstalledDB
from audit_questie_npc_locations import runtime_quests, npc_ids

ROOT = Path(__file__).resolve().parents[1]
CLASSIC = (ROOT.parents[3] / '_anniversary_' / 'Interface' / 'AddOns' / 'QuestieDB' / 'QuestieDB_Vanilla.toc')
SOD_NPCS = CLASSIC.parent / 'src' / 'corrections' / 'Sod' / 'sodBaseNPCs.lua'
ERA_FIXES = CLASSIC.parent / 'src' / 'corrections' / 'Era' / 'classicNPCFixes.lua'


def sod_npcs():
    """Read generated SoD NPC literals as data; do not execute addon Lua."""
    text = SOD_NPCS.read_text(encoding='utf-8')
    records = {}
    for match in re.finditer(r'^        \[(\d+)\] = \{\s*\n(.*?)^        \},', text, re.M | re.S):
        body = match.group(2)
        name = re.search(r'\[npcKeys\.name\]\s*=\s*"([^"]+)"', body)
        spawn = re.search(r'\[npcKeys\.spawns\]\s*=\s*\{(.*?)^            \},', body, re.M | re.S)
        if not name or not spawn:
            continue
        locations = {}
        for zone, values in re.findall(r'^                \[(\d+)\]\s*=\s*\{(.*?)\},\s*$', spawn.group(1), re.M):
            locations[int(zone)] = [(float(x)/100, float(y)/100)
                                    for x, y in re.findall(r'\{([\d.]+),\s*([\d.]+)\}', values)]
        if locations:
            records[int(match.group(1))] = {'name': name.group(1), 'locations': locations}
    return records


def era_faction_spawns(npc_id):
    text = ERA_FIXES.read_text(encoding='utf-8')
    zones = {'STORMWIND_CITY': 1519, 'UNDERCITY': 1497, 'ORGRIMMAR': 1637}
    found = {}
    for section in ('npcFixesHorde', 'npcFixesAlliance'):
        part = text.split('local ' + section + ' = {', 1)[-1]
        entry = re.search(r'^        \[' + str(npc_id) + r'\] = \{(.*?)^        \},', part, re.M | re.S)
        if not entry:
            continue
        for zone, x, y in re.findall(r'\[zoneIDs\.(\w+)\]\s*=\s*\{\{([\d.]+),\s*([\d.]+)\}\}', entry.group(1)):
            if zone in zones:
                found[zones[zone]] = (float(x)/100, float(y)/100)
    return found


def points(npc):
    spawns = npc.get(7) or {}
    if isinstance(spawns, list):
        spawns = {npc.get(9): spawns[0]} if spawns and npc.get(9) else {}
    for area, xy in spawns.items():
        for x, y in xy:
            yield area, x/100, y/100
    paths = npc.get(8) or {}
    if isinstance(paths, dict):
        for area, routes in paths.items():
            for route in routes:
                for x, y in route:
                    yield area, x/100, y/100


def main():
    forever = InstalledDB(ROOT.parent / 'QuestieDB/QuestieDB_Forever.toc')
    classic = InstalledDB(CLASSIC, expected_flavor='Vanilla')
    sod = sod_npcs()
    audit = json.loads((ROOT / 'Data/QUESTIE_NPC_LOCATION_AUDIT.json').read_text(encoding='utf-8'))
    candidates = []
    for row in audit['issues']:
        if row['kind'] not in ('npc-absent-from-questie', 'npc-has-no-questie-spawn', 'classic-fallback'):
            continue
        npc = classic.entity('Npc', row['npcID'])
        spawn = list(points(npc))
        cq = classic.entity('Quest', row['questID'])
        fq = forever.entity('Quest', row['questID'])
        title = row.get('questTitle') or fq.get(1)
        title_match = bool(cq and title and cq.get(1) == title)
        same_area = [p for p in spawn if p[0] == row['areaID']]
        sod_npc = sod.get(row['npcID'], {})
        sod_spawns = sod_npc.get('locations', {}).get(row['areaID'], [])
        sod_name_match = bool(sod_npc.get('name') == row.get('recordedName'))
        era_xy = era_faction_spawns(row['npcID']).get(row['areaID']) if row['npcID'] == 5676 else None
        candidates.append({'questID': row['questID'], 'role': row['role'], 'npcID': row['npcID'],
                           'recordedName': row.get('recordedName'), 'classicName': npc.get(1),
                           'areaID': row['areaID'], 'recordedXY': row['recordedXY'],
                           'classicQuestPresent': bool(cq), 'classicQuestTitle': cq.get(1),
                           'questTitleMatches': title_match, 'foreverQuestPresent': bool(fq),
                           'classicNPCPresent': bool(npc), 'classicSpawnAreas': sorted({p[0] for p in spawn}),
                           'sameAreaSpawns': len(same_area),
                           'sodNPCPresent': bool(sod_npc), 'sodNameMatches': sod_name_match,
                           'sodSameAreaSpawns': len(sod_spawns),
                           'sodNearestXY': list(min(sod_spawns, key=lambda p:
                               (p[0]-row['recordedXY'][0])**2+(p[1]-row['recordedXY'][1])**2))
                               if sod_spawns else None,
                           'eraFactionCorrectionXY': list(era_xy) if era_xy else None,
                           'nearestSameAreaXY': list(min(same_area, key=lambda p:
                               (p[1]-row['recordedXY'][0])**2+(p[2]-row['recordedXY'][1])**2)[1:])
                               if same_area else None})
    counts = {'missingForeverPins': len(candidates),
              'classicNPCRecords': sum(c['classicNPCPresent'] for c in candidates),
              'classicSameAreaSpawns': sum(bool(c['sameAreaSpawns']) for c in candidates),
              'classicQuestTitleMatches': sum(c['questTitleMatches'] for c in candidates),
              'sodNPCRecords': sum(c['sodNPCPresent'] for c in candidates),
              'sodExactNameAndArea': sum(c['sodNameMatches'] and bool(c['sodSameAreaSpawns'])
                                         for c in candidates),
              'eraFactionCorrectionSpawns': sum(bool(c['eraFactionCorrectionXY']) for c in candidates)}
    reference = json.loads((ROOT / 'Data/alliance-reference.json').read_text(encoding='utf-8'))['quests']
    quest_candidates = []
    for quest_id, locations in runtime_quests().items():
        if forever.entity('Quest', quest_id):
            continue
        classic_quest = classic.entity('Quest', quest_id)
        title = reference.get(str(quest_id), {}).get('title')
        match = bool(title and classic_quest.get(1) == title)
        phases = {}
        if match:
            for role, field in (('start', 2), ('end', 3)):
                actors = npc_ids(classic_quest.get(field))
                recorded = {p.get('entityID') for p in locations
                            if p.get('role') == role and p.get('entityType') == 1}
                actors_with_spawns = {actor for actor in actors if list(points(classic.entity('Npc', actor)))}
                phases[role] = {'classicNPCs': sorted(actors), 'recordedNPCs': sorted(recorded),
                                'sameActorWithSpawn': sorted(recorded & actors_with_spawns),
                                'differentActorWithSpawn': sorted(actors_with_spawns - recorded)}
        quest_candidates.append({'questID': quest_id, 'recordedTitle': title,
                                 'classicTitle': classic_quest.get(1), 'exactTitleMatch': match,
                                 'phases': phases})
    counts.update({'missingForeverQuestRecords': len(quest_candidates),
                   'classicExactQuestMatches': sum(q['exactTitleMatch'] for q in quest_candidates),
                   'exactMatchesWithSameActorSpawn': sum(bool(p['sameActorWithSpawn'])
                       for q in quest_candidates for p in q['phases'].values()),
                   'exactMatchesWithDifferentActorSpawn': sum(bool(p['differentActorWithSpawn'])
                       for q in quest_candidates for p in q['phases'].values())})
    output = {'foreverSHA256': forever.sha256, 'classicSHA256': classic.sha256,
              'classicSource': 'QuestieDB/QuestieDB_Vanilla.toc (installed Anniversary addon)', 'sodBaseNPCsSHA256': hashlib.sha256(SOD_NPCS.read_bytes()).hexdigest(),
              'eraFixesSHA256': hashlib.sha256(ERA_FIXES.read_bytes()).hexdigest(),
              'counts': counts,
              'candidates': candidates, 'questCandidates': quest_candidates}
    path = ROOT / 'Data/CLASSIC_NPC_FALLBACK_AUDIT.json'
    path.write_text(json.dumps(output, indent=2)+'\n', encoding='utf-8')
    print(counts)
    for row in candidates[:20]:
        print(row['questID'], row['role'], row['npcID'], row['classicName'], row['sameAreaSpawns'],
              row['questTitleMatches'])


if __name__ == '__main__':
    main()
