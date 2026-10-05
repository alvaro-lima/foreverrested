"""Compare playable quest NPC pins with the installed Forever QuestieDB.

Questie quest starter/finisher IDs and NPC spawn coordinates are authoritative.
Coordinates are approximate, so positional warnings use a generous map radius.
"""
import argparse
import json
from pathlib import Path

from audit_01_10 import guides
from read_installed_questie import InstalledDB

ROOT = Path(__file__).resolve().parents[1]


def npc_ids(actors):
    if not isinstance(actors, list) or not actors:
        return set()
    return set(actors[0]) if isinstance(actors[0], list) else set()


def spawn_points(npc, area):
    spawns = npc.get(7) or {}
    if isinstance(spawns, dict):
        points = spawns.get(area, [])
    else:
        points = spawns[0] if isinstance(spawns, list) and npc.get(9) == area and spawns else []
    paths = npc.get(8) or {}
    if isinstance(paths, dict):
        for path in paths.get(area, []):
            points = points + path
    return points


def runtime_quests():
    base = ROOT / 'tests/validate.py'
    setup = base.read_text().split("lua.execute(r'''", 2)
    ns = {'__file__': str(base)}
    exec(setup[0] + "lua.execute(r'''" + setup[1], ns)
    lua = ns['lua']
    lua.execute('F.LoadDatabase()')
    f = lua.globals().F
    ids = {task['questID'] for guide in guides(1, 30) for step in guide['steps']
           for task in step.get('tasks', [step]) if task.get('questID')}
    ids.update(identity for identity, _ in f.AllianceQuestData.items())
    ids.update(identity for identity, _ in f.ForeverUnlockFacts.items())
    records = {}
    for identity in sorted(ids):
        row = f.AllianceQuestData[identity] or f.ClassicQuestPolicy.records[identity]
        if not row:
            continue
        records[identity] = [
            {key: value for key, value in point.items() if isinstance(key, str)}
            for _, point in row.locations.items()
        ]
    return records


def audit(radius=0.06):
    db = InstalledDB(ROOT.parent / 'QuestieDB/QuestieDB_Forever.toc')
    records = runtime_quests()
    issues, counts = [], {'quests': len(records), 'questsAbsentFromQuestie': 0,
                          'npcLocations': 0, 'checkedSpawns': 0, 'classicFallbackPins': 0}
    seen = set()
    for quest_id, locations in records.items():
        quest = db.entity('Quest', quest_id)
        if not quest:
            counts['questsAbsentFromQuestie'] += 1
        expected = {'start': npc_ids(quest.get(2)), 'end': npc_ids(quest.get(3))}
        for role, actors in expected.items():
            if actors and not any(p.get('role') == role and p.get('entityType') == 1
                                  and p.get('entityID') in actors for p in locations):
                issues.append({'questID': quest_id, 'questTitle': quest.get(1),
                               'role': role, 'kind': 'missing-questie-actor-pin',
                               'expectedNPCs': sorted(actors)})
        for point in locations:
            if point.get('entityType') != 1 or not isinstance(point.get('entityID'), int):
                continue
            role, npc_id, area = point.get('role'), point['entityID'], point.get('areaID')
            if role not in ('start', 'end', 'requirement', 'sourcerequirement'):
                continue
            key = (quest_id, role, npc_id, area, point.get('x'), point.get('y'))
            if key in seen:
                continue
            seen.add(key)
            counts['npcLocations'] += 1
            npc = db.entity('Npc', npc_id)
            common = {'questID': quest_id, 'questTitle': quest.get(1), 'role': role,
                      'npcID': npc_id, 'recordedName': point.get('name'),
                      'questieName': npc.get(1), 'areaID': area,
                      'recordedXY': [point.get('x'), point.get('y')],
                      'source': point.get('source')}
            if point.get('evidenceKind') in ('sod-npc-baseline', 'classic-era-faction-correction'):
                counts['classicFallbackPins'] += 1
                issues.append(dict(common, kind='classic-fallback',
                                   evidenceKind=point['evidenceKind'],
                                   sourceSHA256=point.get('sourceSHA256')))
                continue
            if not npc:
                issues.append(dict(common, kind='npc-absent-from-questie'))
                continue
            if role in expected and expected[role] and npc_id not in expected[role]:
                issues.append(dict(common, kind='wrong-quest-actor',
                                   expectedNPCs=sorted(expected[role])))
            if not isinstance(area, int) or not isinstance(point.get('x'), (int, float)) or not isinstance(point.get('y'), (int, float)):
                issues.append(dict(common, kind='unlocated-npc-pin'))
                continue
            spawns = spawn_points(npc, area)
            if not spawns:
                areas = npc.get(7) or {}
                issues.append(dict(common, kind='no-questie-spawn-in-area' if areas else 'npc-has-no-questie-spawn',
                                   questieAreas=sorted(areas) if isinstance(areas, dict) else [npc.get(9)] if areas else []))
                continue
            counts['checkedSpawns'] += 1
            nearest = min(spawns, key=lambda xy: (point['x'] - xy[0]/100)**2 + (point['y'] - xy[1]/100)**2)
            distance = ((point['x'] - nearest[0]/100)**2 + (point['y'] - nearest[1]/100)**2)**0.5
            if distance > radius:
                issues.append(dict(common, kind='distant-from-questie-spawn',
                                   nearestQuestieXY=[round(nearest[0]/100, 4), round(nearest[1]/100, 4)],
                                   mapDistance=round(distance, 4)))
    return {'questieSHA256': db.sha256, 'radius': radius, 'counts': counts,
            'limits': [
                'Questie NPC spawn points are approximate; a coordinate within six map-percent units is accepted.',
                'NPC and quest records absent from the installed beta database cannot be verified against Questie.',
                'A spawn match does not prove that an NPC currently offers a quest in the live client.'
            ], 'issues': issues}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    report = audit()
    if args.report:
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    groups = {}
    for row in report['issues']:
        groups[row['kind']] = groups.get(row['kind'], 0) + 1
    print(report['counts'], groups)
    for row in report['issues'][:35]:
        print(row['questID'], row['role'], row['npcID'], row['kind'], row.get('recordedXY'),
              row.get('nearestQuestieXY'), row.get('expectedNPCs'))
