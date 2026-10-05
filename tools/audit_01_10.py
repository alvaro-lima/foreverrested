"""Export starter actions and audit factual Forever HTML, without importing route prose."""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(os.environ['TEMP']) / 'foreverrested-test-deps'))


def guides(min_level=1, max_level=10):
    base = ROOT / 'tests/validate.py'
    setup = base.read_text().split("lua.execute(r'''", 2)
    ns = {'__file__': str(base)}
    exec(setup[0] + "lua.execute(r'''" + setup[1], ns)
    lua = ns['lua']
    def convert(value):
        if hasattr(value, 'items'):
            pairs = list(value.items())
            if pairs and all(isinstance(k, int) for k, _ in pairs):
                return [convert(value[i]) for i in range(1, len(pairs) + 1)]
            return {str(k): convert(v) for k, v in pairs}
        return value
    result = []
    for _, identity in lua.globals().F.GuideLibrary.order.items():
        g = lua.globals().F.GuideLibrary.guides[identity]
        if g.sourceGuideID and not g.retired and min_level <= g.minLevel < max_level:
            copy = {key: convert(g[key]) for key in
                    ('id', 'title', 'zone', 'minLevel', 'maxLevel', 'sourceGuideID', 'nextGuideID', 'steps')}
            for step in copy['steps']:
                for task in step.get('tasks', [step]):
                    identity = task.get('questID')
                    if identity:
                        policy = lua.globals().F.QuestPolicy.Record(lua.globals().F.QuestPolicy, identity)
                        task['auditPrerequisites'] = convert(policy.prerequisites) if policy.prerequisites else []
                        task['auditPrerequisitesAny'] = convert(policy.prerequisitesAny) if policy.prerequisitesAny else []
            result.append(copy)
    return result


def objectives(text):
    """Read objective rows, never comments, search snippets, or the description."""
    text = text.split('<h1 ', 1)[-1].split('<h2', 1)[0]
    text = re.split(r'Provided items?\s*:', text, maxsplit=1, flags=re.I)[0]
    rows = []
    for match in re.finditer(r'<tr\b([^>]*)>(.*?)</tr>', text, re.S):
        attrs, body = match.groups()
        link = re.search(r'href="/forever/(npc|item|object)=(\d+)[^"]*"[^>]*>(.*?)</a>', body, re.S)
        qty = re.search(r'data-icon-list-quantity="(\d+)"', attrs)
        if not qty:
            continue
        if not link:
            cell = re.search(r'<td[^>]*>(.*?)</td>', body, re.S)
            label = cell.group(1).split('<span class="icon-list-quantity-wrapper"', 1)[0] if cell else ''
            label = html.unescape(re.sub('<[^>]+>', '', label)).strip()
            if label:
                rows.append({'kind': 'event', 'action': 'interact', 'count': int(qty.group(1)), 'name': label})
            continue
        kind, identity, name = link.groups()
        label = html.unescape(re.sub('<[^>]+>', '', name))
        action = 'kill' if kind == 'npc' and re.search(r'\b(slain|destroyed)\b', re.sub('<[^>]+>', '', body)) else 'collect' if kind == 'item' else 'interact'
        rows.append({'kind': kind, 'action': action, 'id': int(identity), 'count': int(qty.group(1)),
                     'name': label})
    return rows


def normal_kill_xp(player, mob):
    """Classic solo, normal-mob baseline only; not a verified Forever modifier."""
    if not 1 <= player <= 30 or mob < 1:
        raise ValueError('Beta XP model accepts player levels 1-30 only')
    base = player * 5 + 45
    if mob >= player:
        return round(base * (1 + .05 * min(mob - player, 4)))
    # CMaNGOS BaseGain uses IsTrivialLevelDifference, separately from color.
    if player - mob > (4 if player < 10 else 5 if player < 20 else 6 if player < 30 else 7):
        return 0
    zero = 5 if player < 8 else 6 if player < 10 else 7 if player < 12 else 8 if player < 16 else 9 if player < 20 else 11 if player < 30 else 12
    return round(base * (1 - (player - mob) / zero))


def budget_report(route, records, npc_path=None):
    npcs = None
    if npc_path:
        from lupa.lua51 import LuaRuntime
        from build_classic_policy import literal_table
        npcs = literal_table(npc_path, 'npcData', LuaRuntime(unpack_returned_tuples=True))
    budgets = []
    lines = ['# Level 1-10 audit and fixes', '', f'Reviewed 2026-10-03. Ten playable chapters across four starter routes; {len(records)} authored quests.', '',
             'Quest objective counts were read from the objective table of fetched Forever pages. Live client objectives remain authoritative.', '',
             '**Required routes and progression repaired; XP forecasts remain approximate.** Optional rewards and kills are excluded. Listed quest XP is reference XP, not a measured reward at the character\'s level. The initial HTTP 403 responses cleared on retry. Paced batches collected 139 mob/item pages; unavailable published loot samples remain unknown.', '',
             '| Chapter | Required turn-ins | Listed required reward XP | Direct kill objectives | Recovery steps |',
             '| --- | ---: | ---: | ---: | ---: |']
    done_by_route = {}
    for guide in route:
        required, optional, kills, gaps = set(), set(), [], []
        seen = done_by_route.setdefault(guide['sourceGuideID'], set())
        for step in guide['steps']:
            for task in step.get('tasks', [step]):
                identity = task.get('questID')
                if not identity or step['type'] == 'trainer':
                    continue
                if task['type'] == 'pickup' and not task.get('optional'):
                    for prior in task.get('auditPrerequisites', []):
                        if prior not in seen:
                            gaps.append({'questID': identity, 'missingPriorTurnin': prior})
                    alternatives = task.get('auditPrerequisitesAny', [])
                    if alternatives and not any(prior in seen for prior in alternatives):
                        gaps.append({'questID': identity, 'missingAnyPriorTurnin': alternatives})
                if task['type'] == 'turnin':
                    (optional if task.get('optional') else required).add(identity)
                    if not task.get('optional'):
                        seen.add(identity)
                if task['type'] == 'objective' and not task.get('optional'):
                    for obj in records[str(identity)].get('objectives', []):
                        if obj['action'] != 'kill':
                            continue
                        model = dict(obj, questID=identity, source=records[str(identity)]['source'])
                        npc = npcs[obj['id']] if npcs is not None else None
                        model['approxSoloNormalXPAtEntry'] = None
                        if npc is not None and npc[6] == 0 and npc[4] and npc[5]:
                            model['baselineMobLevels'] = [npc[4], npc[5]]
                            model['approxSoloNormalXPAtEntry'] = [normal_kill_xp(guide['minLevel'], level) for level in (npc[4], npc[5])]
                        kills.append(model)
        reward = sum(records[str(identity)].get('listedXP', 0) for identity in required)
        recoveries = [{'stepID': step['id'], 'targetLevel': step['targetLevel'], 'text': step['text']}
                      for step in guide['steps'] if step.get('levelRecovery')]
        budget = {'guideID': guide['id'], 'title': guide['title'], 'requiredTurninIDs': sorted(required),
                  'excludedOptionalTurninIDs': sorted(optional - required), 'listedRequiredQuestXP': reward,
                  'directKillObjectives': kills, 'requiredPrerequisiteGaps': gaps, 'levelRecoverySteps': recoveries,
                  'totalExpectedXP': None, 'missing': ['current-build Forever mob XP modifiers', 'verified conditional collection drop rates', 'level-adjusted quest rewards']}
        budgets.append(budget)
        lines.append(f"| {guide['title']} | {len(required)} | {reward:,} | {sum(k['count'] for k in kills)} | {len(recoveries)} |")
    lines.extend(['', 'Direct kill counts are objective requirements, not a full combat XP total. Item drops, supplied quest items, object looting and talk/escort credit are not silently converted into kills. Shared work must be resolved before summing kill XP.', '',
                  'Known prerequisite ordering passes for the required route using the existing policy; undocumented Forever prerequisites remain unverified. Objective collection stays in the chapter that schedules it.', '',
                  'Each chapter now has a sourced local combat recovery step at its exit, plus checks before required pickups above its entry level. These use actual player level and live XP to the next level, complete automatically, and can be bypassed explicitly with Skip. They do not add later-chapter quest objectives or turn optional quests mandatory.', '',
                  'The required route now includes the Stonefield/Maclure necklace chain, eastern logging/Defias work, the western Shimmerweed quest, Zenn\'s collection/redemption, Denalan\'s delivery, the road ambushers and the properly ordered Sleeping Druid / Druid of the Claw stages. Named/elite group detours and dropped-item starts remain optional. Former optional action IDs are retained for promoted work so saved positions and explicit skips survive.', '',
                  'The importer now excludes provided items from collected objectives and retains scripted objective rows. Navigation excludes 81 incidental loot locations using a documented inference: where a source has at least 5% published drop frequency, targets more than ten times less likely are unsuitable fallback farming targets. Full raw source evidence is preserved in the cache and STARTER_COMBAT.json.', '',
                  'STARTER_COMBAT.json contains sourced Forever mob levels and loot samples, including tiny-sample and incidental-drop flags. STARTER_ROUGH_ESTIMATES.json combines required rewards and approximate combat XP, selecting local normal mobs and counting shared work once. Estimates use the chapter entry level and the Classic solo XP formula; actual XP changes with level, modifiers, drops and scripted encounters. These are planning estimates, not promised finish levels. Provided items, talk and escort credit are not silently counted as kills.', '',
                  'Sources: individual quest URLs and page checksums in STARTER_AUDIT.json; [QuestieDB NPC baseline](https://github.com/Questie/QuestieDB/blob/cac1eff815923f896d082764d023cf812454a023/data/Forever/foreverNpcDB.lua); [Classic XP formula reference](https://github.com/cmangos/mangos-classic/blob/master/src/game/Tools/Formulas.h).', '',
                  'Remaining field verification: conditional quest drop rates, actual Forever XP modifiers and scripted combat. Further route expansion may reduce recovery grinding. The runtime fix does not establish that quests alone fill the advertised bands.', '',
                  'Validation: starter source/parser checks, all ten live level handoffs, prerequisite ordering, early-section migration, optional-XP arithmetic, objective queue, linked catch-up, entry travel and optional tooltips pass. The broader legacy validate.py harness fails at its secure-target macro assertion both before and after these audit edits; it is not a passing full-suite result.', '',
                  'Rebuild from the saved cache with tools/build_starter_combat.py, then tools/audit_01_10.py --apply --combat Data/STARTER_COMBAT.json, supplying --cache to both. The paced fetch helper stops at the first failed request. No third-party quest prose or route ordering is imported.', ''])
    estimates_path = ROOT / 'Data/STARTER_ROUGH_ESTIMATES.json'
    if estimates_path.exists():
        estimates = json.loads(estimates_path.read_text(encoding='utf-8'))
        lines.extend(['## Rough required-work XP', '', 'Fixed entry-level comparison only; no rested, class, exploration, optional or incidental XP. Ranges reflect mob levels, not the probability of lucky or unlucky drops.', '',
                      '| Chapter | Approximate required reward + combat XP |', '| --- | ---: |'])
        for estimate in estimates['chapters']:
            total = estimate['roughTotalXPRange']
            value = f'{total[0]:,}–{total[1]:,}' if total else 'Unknown: missing input data'
            lines.append(f"| {estimate['title']} | {value} |")
        lines.append('')
    assert not any(budget['requiredPrerequisiteGaps'] for budget in budgets), 'Required prerequisite ordering needs repair'
    (ROOT / 'Data/STARTER_XP_BUDGET.json').write_text(json.dumps({'schemaVersion': 1, 'optionalXPExcluded': True, 'chapters': budgets}, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (ROOT / 'Data/STARTER_AUDIT.md').write_text('\n'.join(lines), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cache', type=Path, required=True)
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--apply', action='store_true', help='Merge audited starter facts into the existing reference')
    parser.add_argument('--npc-baseline', type=Path, help='Optional literal QuestieDB NPC table for labelled rough XP')
    parser.add_argument('--combat', type=Path, help='Reviewed combat reference for excluding incidental loot navigation sources')
    args = parser.parse_args()
    route = guides()
    ids = set()
    for guide in route:
        for step in guide['steps']:
            if step['type'] == 'trainer':
                continue
            for task in step.get('tasks', [step]):
                if task.get('questID'):
                    ids.add(task['questID'])
    if args.export:
        args.cache.mkdir(parents=True, exist_ok=True)
        (args.cache / 'manifest.json').write_text(json.dumps({'guides': route, 'questIDs': sorted(ids)}, indent=2))
        print(f'{len(route)} chapters; {len(ids)} authored quest identities')
        return
    from build_alliance_reference import extract
    reference_path = ROOT / 'Data/alliance-reference.json'
    reference = json.loads(reference_path.read_text(encoding='utf-8'))
    combat = json.loads(args.combat.read_text(encoding='utf-8')) if args.combat else {}
    records = {}
    for identity in sorted(ids):
        path = args.cache / f'quest-{identity}.html'
        if not path.exists():
            records[str(identity)] = {'missing': ['current-page']}
            continue
        text = path.read_text(encoding='utf-8-sig')
        old = reference['quests'].get(str(identity), {})
        record = extract(identity, text, {identity: set(old.get('classes', []))})
        assert record['objectives'] == objectives(text), 'Objective extractors disagree'
        incidental = {(obj['name'], source['npcID']) for obj in combat.get('quests', {}).get(str(identity), {}).get('objectives', [])
                      for source in obj.get('dropSources', []) if source.get('incidentalLootCandidate')}
        if incidental:
            before = len(record['locations'])
            record['locations'] = [point for point in record['locations'] if not
                                   (point.get('role') == 'sourcerequirement' and (point.get('item'), point.get('entityID')) in incidental)]
            record['incidentalLootLocationsExcluded'] = before - len(record['locations'])
            record['locationFilterInference'] = 'Exclude loot sources more than ten times less likely than an available source with at least 5% published drop frequency.'
        record['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        record['retrievedAt'] = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
        records[str(identity)] = record
    if args.apply:
        if any(record.get('missing') for record in records.values()):
            raise ValueError('Cannot apply an incomplete starter reference refresh')
        from refresh_quest_data import lua as serialize
        for identity, record in records.items():
            merged = dict(reference['quests'].get(identity, {}))
            merged.update({key: value for key, value in record.items() if key != 'sha256'})
            reference['quests'][identity] = merged
            reference['checksums'][identity] = record['sha256']
        reference['compiledAt'] = datetime.now(timezone.utc).isoformat()
        reference_path.write_text(json.dumps(reference, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        runtime_path = ROOT / 'Guides/AllianceQuestData.lua'
        header = runtime_path.read_text(encoding='utf-8').split('F.AllianceQuestData = ', 1)[0]
        runtime_path.write_text(header + 'F.AllianceQuestData = {' + ',\n'.join(
            f'[{identity}]={serialize(record)}' for identity, record in sorted(reference['quests'].items(), key=lambda pair: int(pair[0]))) + '}\n', encoding='utf-8')
    output = {'schemaVersion': 1, 'kind': 'Forever-public-reference-audit', 'guides': route, 'quests': records}
    (ROOT / 'Data/STARTER_AUDIT.json').write_text(json.dumps(output, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    budget_report(route, records, args.npc_baseline)
    requests = set()
    for record in records.values():
        for obj in record.get('objectives', []):
            if obj['kind'] in ('npc', 'item'):
                requests.add((obj['kind'], obj['id']))
    (args.cache / 'entities.json').write_text(json.dumps([{'kind': kind, 'id': identity} for kind, identity in sorted(requests)]))
    print(f'Audited {len(records)} quests; {len(requests)} objective entities need loot/level references')


if __name__ == '__main__':
    main()
