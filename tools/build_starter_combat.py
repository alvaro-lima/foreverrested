"""Compile relevant mob/drop facts from cached Forever pages; never invent rates."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
from build_alliance_reference import decode_after, extract
from audit_01_10 import normal_kill_xp

ROOT = Path(__file__).resolve().parents[1]


def listview_rows(text, template='npc', identity='dropped-by'):
    for match in re.finditer(r'new Listview\(\{', text):
        tail = text[match.end():]
        data = re.search(r'\bdata\s*:', tail)
        if not data:
            continue
        header = tail[:data.start()]
        if re.search(r"template:\s*['\"]" + re.escape(template) + r"['\"]", header) and re.search(r"id:\s*['\"]" + re.escape(identity) + r"['\"]", header):
            return json.JSONDecoder().raw_decode(tail[data.end():].lstrip())[0]
    return []


def loot_rows(text):
    return listview_rows(text)


def npc_data(identity, text):
    for marker in (f'$.extend(g_npcs[{identity}], ', f'g_npcs[{identity}] = ', f'g_npcs[{identity}]='):
        record = decode_after(text, marker)
        if isinstance(record, dict):
            return record
    # The main NPC data may instead be in a page-scoped gatherer block.
    for match in re.finditer(r'WH\.Gatherer\.addData\(1,\s*16,\s*', text):
        rows = json.JSONDecoder().raw_decode(text[match.end():].lstrip())[0]
        if str(identity) in rows:
            return rows[str(identity)]
    return {}


def source_stamp(path, kind, identity):
    return {'source': f'https://www.wowhead.com/forever/{kind}={identity}',
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'retrievedAt': datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()}


def compile_reference(cache, audit):
    items, mobs, pages, containers, supplied = {}, {}, [], {}, {}
    for path in cache.glob('item-*.html'):
        identity = int(path.stem.split('-')[1])
        stamp = source_stamp(path, 'item', identity)
        pages.append(stamp)
        item_text = path.read_text(encoding='utf-8-sig')
        rows = loot_rows(item_text)
        containers[identity] = listview_rows(item_text, 'object', 'contained-in-object')
        supplied[identity] = {row['id'] for row in listview_rows(item_text, 'quest', 'provided-for')}
        items[identity] = {row['id']: row for row in rows}
        for row in rows:
            if row.get('minlevel') and row.get('maxlevel'):
                mobs.setdefault(row['id'], dict(row, **stamp))
    for path in cache.glob('npc-*.html'):
        identity = int(path.stem.split('-')[1])
        stamp = source_stamp(path, 'npc', identity)
        pages.append(stamp)
        row = npc_data(identity, path.read_text(encoding='utf-8-sig'))
        if row:
            mobs[identity] = dict(row, **stamp)
    records = {}
    for identity, quest in audit['quests'].items():
        # Reconstruct raw source locations so rerunning after navigation curation
        # still retains evidence for every excluded incidental loot candidate.
        quest_page = cache / f'quest-{identity}.html'
        locations = extract(int(identity), quest_page.read_text(encoding='utf-8-sig'), {}).get('locations', []) if quest_page.exists() else quest.get('locations', [])
        objectives = []
        for obj in quest.get('objectives', []):
            result = dict(obj)
            if obj['action'] == 'kill':
                row = mobs.get(obj['id'], {})
                result['mob'] = {key: row[key] for key in ('name', 'minlevel', 'maxlevel', 'classification', 'source') if key in row}
            elif obj['action'] == 'collect':
                sources = {point['entityID'] for point in locations
                           if point.get('role') == 'sourcerequirement' and point.get('entityType') == 1 and point.get('item') == obj['name']}
                linked = {point['entityID'] for point in locations
                          if point.get('role') in ('requirement','sourcerequirement') and point.get('entityType') == 1
                          and point['entityID'] in items.get(obj['id'], {})} - sources
                sources |= linked
                result['dropSources'] = []
                for npc in sorted(sources):
                    row = items.get(obj['id'], {}).get(npc)
                    source = {'npcID': npc, 'dropChance': None}
                    if npc in linked:
                        source['sourceLinkInference'] = 'Published item drop source matches a combat source mapped for another objective of this quest.'
                    source['zones'] = sorted({point['zone'] for point in locations if point.get('entityID') == npc and point.get('role') in ('requirement','sourcerequirement')})
                    if row:
                        source.update({key: row[key] for key in ('name', 'minlevel', 'maxlevel', 'classification', 'count', 'outof', 'pctstack') if key in row})
                        count, sample = row.get('count'), row.get('outof')
                        if isinstance(count, (int, float)) and isinstance(sample, (int, float)) and sample > 0 and 0 < count <= sample:
                            source['dropChance'] = count / sample
                            source['smallSample'] = sample < 100
                            # Explicit single-item assumption; stacked loot needs a
                            # separate quantity model before it can enter a budget.
                            if row.get('pctstack') is None:
                                source['approxKillsForObjective'] = math.ceil(obj['count'] / source['dropChance'])
                                source['itemsPerSuccessfulDropAssumed'] = 1
                        source['source'] = f"https://www.wowhead.com/forever/item={obj['id']}"
                    result['dropSources'].append(source)
                best = max((source['dropChance'] or 0 for source in result['dropSources']), default=0)
                for source in result['dropSources']:
                    source['incidentalLootCandidate'] = bool(source['dropChance'] is not None and best >= .05 and source['dropChance'] < best / 10)
                objects = sorted({point['entityID'] for point in locations
                                  if point.get('role') == 'sourcerequirement' and point.get('entityType') == 2 and point.get('item') == obj['name']})
                container_rows = containers.get(obj['id'], [])
                objects = sorted(set(objects) | {row['id'] for row in container_rows})
                result['objectSourceIDs'] = objects
                result['objectSources'] = [{'objectID': row['id'], 'name': row.get('name'), 'count': row.get('count'), 'outof': row.get('outof'), 'source': f"https://www.wowhead.com/forever/item={obj['id']}"} for row in container_rows]
                # Random treasure chests are incidental loot, not a dependable
                # ground-object alternative to the quest's combat work.
                dependable_chests = {row['id'] for row in container_rows if isinstance(row.get('count'), (int,float)) and isinstance(row.get('outof'), (int,float)) and row['outof'] > 0 and row['count']/row['outof'] >= .8}
                incidental_objects = {row['id'] for row in container_rows if re.search(r'\b(chest|footlocker)\b', row.get('name', ''), re.I) and row['id'] not in dependable_chests}
                incidental_objects |= {point['entityID'] for point in locations if point.get('entityID') in objects and re.search(r'\b(chest|footlocker)\b', point.get('name', ''), re.I) and point['entityID'] not in dependable_chests}
                # A wardrobe's tiny incidental bandana frequency must not
                # erase the Defias hunt. Dedicated named quest containers
                # (e.g. Shimmerweed baskets) remain object alternatives.
                if sources:
                    item_key = re.sub(r'[^a-z0-9]', '', obj['name'].lower())
                    for row in container_rows:
                        name_key = re.sub(r'[^a-z0-9]', '', row.get('name', '').lower())
                        if row['id'] not in dependable_chests and item_key not in name_key:
                            incidental_objects.add(row['id'])
                dependable = sorted(set(objects) - incidental_objects)
                result['dependableObjectSourceIDs'] = dependable
                result['acquisition'] = 'object-or-mob' if dependable and sources else 'object-loot' if dependable else 'mob-drop' if sources else 'not-established-as-mob-drop'
                if int(identity) in supplied.get(obj['id'], set()):
                    result['acquisition'] = 'provided-by-quest'
                    result['providedItemSource'] = f"https://www.wowhead.com/forever/item={obj['id']}"
            objectives.append(result)
        records[identity] = {'objectives': objectives}
    # Approximate XP is always labelled and evaluated at the chapter entry
    # level. It is not summed into a guaranteed level-band budget.
    for guide in audit['guides']:
        for step in guide['steps']:
            identity = step.get('questID')
            if not identity or step['type'] != 'objective':
                continue
            for obj in records[str(identity)]['objectives']:
                candidates = [obj.get('mob', {})] if obj['action'] == 'kill' else obj.get('dropSources', [])
                for candidate in candidates:
                    low, high = candidate.get('minlevel'), candidate.get('maxlevel')
                    if low and high and candidate.get('classification') == 0:
                        candidate.setdefault('approxSoloNormalXPByPlayerLevel', {})[str(guide['minLevel'])] = [normal_kill_xp(guide['minLevel'], level) for level in (low, high)]
    return {'schemaVersion': 1, 'kind': 'public-Forever-combat-reference', 'pages': pages, 'quests': records,
            'limits': ['Published loot samples may mix kills without the quest; they are not a verified conditional quest drop rate.',
                       'Small samples are flagged; missing or negative counts do not imply a drop rate.',
                       'Mob levels do not establish special XP modifiers. Rested/group XP is excluded from baseline planning.']}


def chapter_estimates(audit, combat):
    """Rough chapter estimates, preserving unknown inputs and shared kill groups."""
    rows = []
    for guide in audit['guides']:
        groups, missing, warnings, rewards = {}, [], [], 0
        # Establish all required direct kills first, so item drops from those
        # same kills do not inflate shared collection forecasts.
        for step in guide['steps']:
            identity = step.get('questID')
            if not identity or step['type'] != 'objective' or step.get('optional') or step.get('classes') or audit['quests'].get(str(identity), {}).get('requiredClasses'):
                continue
            for obj in combat['quests'][str(identity)]['objectives']:
                if obj['action'] != 'kill':continue
                xp = obj.get('mob', {}).get('approxSoloNormalXPByPlayerLevel', {}).get(str(guide['minLevel']))
                if xp is None:continue
                key = (step.get('legacyGroupID', step['id']), obj['id'])
                groups.setdefault(key, {'npcID': obj['id'], 'kills': 0, 'approxXPPerKillRange': xp})['kills'] = max(groups.get(key, {}).get('kills', 0), obj['count'])
        for step in guide['steps']:
            identity = step.get('questID')
            if not identity or step.get('optional') or step.get('classes') or audit['quests'].get(str(identity), {}).get('requiredClasses'):
                continue
            if step['type'] == 'turnin':
                rewards += audit['quests'][str(identity)].get('listedXP', 0)
            if step['type'] != 'objective':
                continue
            for obj in combat['quests'][str(identity)]['objectives']:
                if obj['action'] == 'interact':
                    continue
                if obj['action'] == 'kill':
                    mob = obj.get('mob', {})
                    count, npc = obj['count'], obj['id']
                else:
                    if obj.get('acquisition') == 'not-established-as-mob-drop':
                        missing.append(f"Quest {identity}, {obj['name']}: acquisition source not established")
                        continue
                    if obj.get('acquisition') != 'mob-drop':
                        # No explicit combat source: never assign speculative kills.
                        warnings.append(f"Quest {identity}, {obj['name']}: object loot or non-combat acquisition exists; no baseline kills assumed")
                        continue
                    candidates = [source for source in obj['dropSources'] if source.get('dropChance')
                                  and not source.get('incidentalLootCandidate') and source.get('classification') == 0
                                  and guide['zone'] in source.get('zones', []) and source.get('approxKillsForObjective') is not None]
                    if not candidates:
                        missing.append(f"Quest {identity}, {obj['name']}: usable local drop rate")
                        continue
                    suitable = [source for source in candidates if source.get('minlevel', 99) <= guide['minLevel'] + 2 and source.get('maxlevel', 99) <= guide['minLevel'] + 3]
                    if not suitable:
                        lowest = min(source.get('minlevel', 99) for source in candidates)
                        suitable = [source for source in candidates if source.get('minlevel', 99) == lowest]
                        warnings.append(f"Quest {identity}, {obj['name']}: collection mobs exceed entry level by more than two")
                    mob = max(suitable, key=lambda source: source['dropChance'])
                    count, npc = mob['approxKillsForObjective'], mob['npcID']
                    shared = step.get('legacyGroupID', step['id'])
                    rates = {source['npcID']: source['dropChance'] for source in obj['dropSources'] if source.get('dropChance') is not None}
                    credit = sum(group['kills'] * rates.get(key[1], 0) for key, group in groups.items() if key[0] == shared)
                    existing = groups.get((shared, npc), {}).get('kills', 0)
                    count = existing + math.ceil(max(0, obj['count'] - credit) / mob['dropChance'])
                    if count == 0:continue
                    if mob.get('smallSample'):
                        warnings.append(f"Quest {identity}, {obj['name']}: drop sample below 100 kills")
                xp = mob.get('approxSoloNormalXPByPlayerLevel', {}).get(str(guide['minLevel']))
                if xp is None:
                    missing.append(f'Quest {identity}, NPC {npc}: normal-mob XP model')
                    continue
                group = (step.get('legacyGroupID', step['id']), npc)
                if group in groups:
                    groups[group]['kills'] = max(groups[group]['kills'], count)
                else:
                    groups[group] = {'npcID': npc, 'kills': count, 'approxXPPerKillRange': xp}
        low = sum(group['kills'] * min(group['approxXPPerKillRange']) for group in groups.values())
        high = sum(group['kills'] * max(group['approxXPPerKillRange']) for group in groups.values())
        rows.append({'guideID': guide['id'], 'title': guide['title'], 'assumedPlayerLevel': guide['minLevel'],
                     'listedRequiredRewardXP': rewards, 'knownCombatGroups': list(groups.values()),
                     'knownCombatXPRange': [low, high], 'missing': sorted(set(missing)), 'warnings': sorted(set(warnings)),
                     'roughTotalXPRange': None if missing else [rewards + low, rewards + high]})
    return {'schemaVersion': 1, 'optionalXPExcluded': True, 'kind': 'rough-fixed-entry-level-estimates',
            'assumptions': ['No optional or incidental kills, rested XP, exploration or class detours.',
                            'Mob XP is evaluated at chapter entry level, not simulated through every level-up.',
                            'Mob-only collection estimates choose the best published local normal-mob rate; one item per successful drop is assumed. Available object-loot alternatives assume no baseline kills.',
                            'Concurrent required objectives sharing an authored group and NPC count kills once. Published-rate expected drops from all shared planned kills reduce remaining collection kills; this does not guarantee those drops.',
                            'Published drop samples and Classic XP modifiers are estimates, not verified current-build budgets.'],
            'chapters': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    args = parser.parse_args()
    audit = json.loads((ROOT / 'Data/STARTER_AUDIT.json').read_text(encoding='utf-8'))
    reference = compile_reference(args.cache, audit)
    (ROOT / 'Data/STARTER_COMBAT.json').write_text(json.dumps(reference, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    estimates = chapter_estimates(audit, reference)
    (ROOT / 'Data/STARTER_ROUGH_ESTIMATES.json').write_text(json.dumps(estimates, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    drops = [source for quest in reference['quests'].values() for obj in quest['objectives'] for source in obj.get('dropSources', [])]
    print(f"{len(reference['pages'])} entity pages; {sum(source['dropChance'] is not None for source in drops)}/{len(drops)} relevant mob/item rates available")


if __name__ == '__main__':
    main()
