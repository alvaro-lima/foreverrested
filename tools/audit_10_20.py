"""Audit the 10-20 chapters using objective-table facts and explicit missing inputs."""
import argparse, hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
from audit_01_10 import guides, objectives
from build_alliance_reference import extract
from build_starter_combat import compile_reference, chapter_estimates
from refresh_quest_data import lua as serialize
ROOT = Path(__file__).resolve().parents[1]

def report(audit, combat, estimates):
    records=audit['quests']
    seen_by_source={}
    budgets=[]
    for g,e in zip(audit['guides'],estimates['chapters']):
        required,optional,classes=set(),set(),set()
        seen=seen_by_source.setdefault(g['sourceGuideID'],set())
        gaps=[]
        for s in g['steps']:
            i=s.get('questID')
            if not i:continue
            if s.get('classes') or records[str(i)].get('requiredClasses'):
                classes.add(i);continue
            if s.get('optional'):
                if s['type']=='turnin':optional.add(i)
                continue
            if s['type']=='pickup':
                gaps += [{'questID':i,'missingPriorTurnin':p} for p in s.get('auditPrerequisites',[]) if p not in seen]
                alternatives=s.get('auditPrerequisitesAny',[])
                if alternatives and not any(p in seen for p in alternatives):gaps.append({'questID':i,'missingAnyPriorTurnin':alternatives})
            if s['type']=='turnin':required.add(i);seen.add(i)
        budgets.append({'guideID':g['id'],'title':g['title'],'requiredTurninIDs':sorted(required),'excludedOptionalTurninIDs':sorted(optional-required),'excludedClassQuestIDs':sorted(classes),'listedRequiredQuestXP':e['listedRequiredRewardXP'],'roughTotalXPRange':e['roughTotalXPRange'],'requiredPrerequisiteGaps':gaps,'levelRecoverySteps':[{'stepID':s['id'],'targetLevel':s['targetLevel'],'zone':s['zone'],'x':s['x'],'y':s['y']} for s in g['steps'] if s.get('levelRecovery')],'verifiedTotalExpectedXP':None,'limits':['Current-build mob XP modifiers and level-adjusted quest rewards are unverified.','Published loot frequencies are not conditional on having the quest.','Scripted, exploration and incidental combat XP is not assumed.']})
    if any(b['requiredPrerequisiteGaps'] for b in budgets):raise ValueError('Required prerequisite ordering requires repair')
    (ROOT/'Data/10_20_XP_BUDGET.json').write_text(json.dumps({'schemaVersion':1,'optionalXPExcluded':True,'classXPExcluded':True,'chapters':budgets},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    drops=[s for q in combat['quests'].values() for o in q['objectives'] for s in o.get('dropSources',[])]
    lines=['# Level 10-20 audit and fixes','','Reviewed 2026-10-03. All twelve playable chapters across Westfall/Redridge, Loch Modan/Redridge, Darkshore and the optional Zephras continuation.','',f'{len(records)} quest pages and {len(combat["pages"])} NPC/item pages were read from the public Forever database. Objective quantities come from quest objective tables; each record retains its source, retrieval time and SHA-256 checksum. Live client objectives remain authoritative.','',f'{sum(s["dropChance"] is not None for s in drops)}/{len(drops)} relevant NPC/item sample ratios are available. Missing ratios stay unknown. {sum(q.get("incidentalLootLocationsExcluded",0) for q in records.values())} incidental loot locations were removed from navigation; full raw evidence remains in the combat reference.','',
    '**The routes are repaired, but quests alone do not establish their advertised finish levels.** Required quest rewards and combat forecasts exclude optional and class-specific work. The mainland chapters now check actual level before acceptance gaps, the riskiest early combat and their next-guide handoffs. Recoveries name a sourced local mob area, display live XP to the next level, and complete automatically; explicit Skip still bypasses them. Remaining grind gaps can be substantial, especially in the later bands.','',
    '| Chapter | Steps | Required turn-ins | Listed required quest XP | Rough quest + combat XP | Recovery checks |','| --- | ---: | ---: | ---: | ---: | ---: |']
    for g,b in zip(audit['guides'],budgets):
        total=b['roughTotalXPRange'];value=f'{total[0]:,}–{total[1]:,}' if total else 'Unknown'
        lines.append(f'| {g["title"]} | {len(g["steps"])} | {len(b["requiredTurninIDs"])} | {b["listedRequiredQuestXP"]:,} | {value} | {len(b["levelRecoverySteps"])} |')
    lines += ['','## Route repairs','',
    '- Westfall farms: Poor Old Blanchy, Goretusk Liver Pie, Patrolling Westfall and Red Leather Bandanas are now required local work. The lower-level objectives come before the level 14-15 Harvest Watchers; a live level-12 recovery precedes that hunt. The level 17-18 final militia ranks have a level-15 recovery.',
    '- Western Loch Modan: Mountaineer Stormpike\'s Task starts in Thelsamar and is delivered at the northern guard tower. Filthy Paws collects four containers of Miners\' Gear; it is not a kobold-ear hunt. Stormpike\'s Order is an optional Stormwind delivery, not an Ironforge hand-in.',
    '- Eastern Loch Modan: the two timed challenges and the named Grawmug/Gnasher/Brawler pack are explicitly optional, with their XP excluded. Crocolisk Hunting requires five meat and six skins; shared crocolisk kills count once. Existing action IDs survive the optional conversion.',
    '- Both Redridge arrivals: Hilary\'s Necklace is required during the tools dive. Selling Fish is accepted only after the level-16 acceptance check, then scheduled in the later local circuit. Existing action IDs survive group size and location changes.',
    '- Darkshore coast and ruins: Tools of the Highborne, For Love Eternal and Washed Ashore are required, with the underwater follow-up and southern turtle added. Anaya is level 16, so the pendant objective has a level-13 recovery. Fishing-dependent work remains optional.',
    '- Darkshore northern circuits: the northern beached creature is included on the shore visit. River sampling and moonwell water are item-use objectives; they never generate fictitious kill XP. The handoff checks actual level 17.',
    '- Darkshore final work: southern carcasses, Fruit of the Sea, the Tower of Althalaxx introduction and four-parchment hunt supplement Mathystra. The dangerous tower interior and Ashenvale continuation stay outside this chapter. The exit checks actual level 20.',
    '- Zephras: Catching Wind asks for six data interactions; Avenged Tenfold collects ten charms. The continuation chapters are labelled 10+ and remain available from level 10. They do not claim that short story clusters reach level 12 or 14. The final optional chapter contributes zero required XP and imposes no island grind.',
    '', '## What the combat forecast means','',
    'Mob levels, classifications, acquisition relations and sample counts come from Forever NPC/item pages. The per-kill XP formula is a labelled Classic solo normal-mob approximation, evaluated at each chapter\'s entry level. It is not measured current-build Forever XP and does not simulate every level-up, rested/group effects, elite multipliers or damage attribution. Listed quest rewards are reference rewards, not measured level-adjusted turn-ins.',
    '', 'Collection forecasts prefer local normal mobs within a suitable entry-level range. Direct kills are established first; expected published-rate drops from shared planned kills reduce remaining collection kills. One item per successful drop is assumed only when stack information permits it. Rates may include kills without the quest and small samples; random outcomes can differ substantially. Shared groups count NPC kills once, rather than adding a full hunt per quest.',
    '', 'Quest containers, provided items and item-use objectives have no invented baseline combat. Incidental chest loot is not treated as a dependable alternative; a quest chest such as the Sunken Chest is retained when the published sample supports it. Four acquisition annotations were manually checked against quest instructions and are bound to page checksums. Unknown acquisition/rate/XP inputs produce an unknown total rather than silently supplying zero.',
    '', '## Evidence and validation','',
    '[10_20_AUDIT.json](10_20_AUDIT.json) contains objective, reward, source and route facts; [10_20_COMBAT.json](10_20_COMBAT.json) contains NPC levels, sample ratios and acquisition evidence; [10_20_ROUGH_ESTIMATES.json](10_20_ROUGH_ESTIMATES.json) contains groups, warnings and assumptions; [10_20_XP_BUDGET.json](10_20_XP_BUDGET.json) separates required, optional and class work. [10_20_ACQUISITION.json](10_20_ACQUISITION.json) records reviewed item-use/object facts. [10_20_ACTION_IDS.json](10_20_ACTION_IDS.json) preserves the previous action identities for migration verification.',
    '', 'Sources: individual [Forever quest pages](https://www.wowhead.com/forever/quests), NPC/item URLs retained in the evidence files; [Classic XP formula](https://github.com/cmangos/mangos-classic/blob/master/src/game/Tools/Formulas.h). Prerequisite ordering is checked against the installed factual policy; this does not prove undocumented beta conditions or current-client availability.',
    '', 'Targeted checks cover all 147 source records, twelve chapters, optional/class XP exclusion, delivery/interaction semantics, shared drop credit, action identity retention, chapter-scoped objectives, nine live mainland handoffs and three optional island exits. Early-section, starter-regression, entry-travel, linked catch-up and optional-tooltip checks are also run. The broader legacy validate.py harness has a pre-existing secure-target macro assertion failure; this is not a passing full-suite claim.',
    '', 'Rebuild: `python tools/audit_10_20.py --cache <saved-cache> --apply`. Export quest requests first with `--export`; `tools/fetch_starter_audit.ps1 -Cache <saved-cache>` performs paced bounded batches and stops on the first failed request. Reviewed acquisition annotations require re-review if their source page changes. No third-party quest prose or route ordering is imported.', '']
    (ROOT/'Data/10_20_AUDIT.md').write_text('\n'.join(lines),encoding='utf-8')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cache',type=Path,required=True)
    p.add_argument('--export',action='store_true')
    p.add_argument('--apply',action='store_true')
    a=p.parse_args()
    route=guides(10,20)
    ids=sorted({t['questID'] for g in route for s in g['steps'] if s['type']!='trainer' for t in s.get('tasks',[s]) if t.get('questID')})
    a.cache.mkdir(parents=True,exist_ok=True)
    manifest={'guides':route,'questIDs':ids}
    (a.cache/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    if a.export:
        (a.cache/'entities.json').write_text(json.dumps([{'kind':'quest','id':i} for i in ids]),encoding='utf-8')
        print(f'{len(route)} chapters; {len(ids)} quest pages');return
    reference_path=ROOT/'Data/alliance-reference.json'
    reference=json.loads(reference_path.read_text(encoding='utf-8'))
    records={}
    for i in ids:
        path=a.cache/f'quest-{i}.html'
        if not path.exists(): raise ValueError(f'Missing quest page {i}')
        raw=path.read_text(encoding='utf-8-sig')
        old=reference['quests'].get(str(i),{})
        record=extract(i,raw,{i:set(old.get('classes',[]))})
        assert record['objectives']==objectives(raw), f'Objective disagreement {i}'
        record['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        record['retrievedAt']=datetime.fromtimestamp(path.stat().st_mtime,timezone.utc).isoformat()
        records[str(i)]=record
    audit={'schemaVersion':1,'kind':'Forever-public-reference-audit','guides':route,'quests':records}
    combat=compile_reference(a.cache,audit)
    acquisition_path=ROOT/'Data/10_20_ACQUISITION.json'
    if acquisition_path.exists():
        for i,fact in json.loads(acquisition_path.read_text(encoding='utf-8'))['quests'].items():
            if records[i]['sha256']!=fact['sha256']:
                raise ValueError(f'Quest {i} acquisition annotation requires review after page change')
            for obj in combat['quests'][i]['objectives']:
                if obj.get('id')==fact['itemID']:
                    obj['acquisition']=fact['acquisition']
                    obj['acquisitionReview']=fact
    for i,record in records.items():
        excluded={(obj['name'],s['npcID']) for obj in combat['quests'][i]['objectives'] for s in obj.get('dropSources',[]) if s.get('incidentalLootCandidate') and s.get('dropChance') is not None}
        before=len(record['locations'])
        record['locations']=[point for point in record['locations'] if not(point.get('role')=='sourcerequirement' and (point.get('item'),point.get('entityID')) in excluded)]
        record['incidentalLootLocationsExcluded']=before-len(record['locations'])
    if a.apply:
        for i,r in records.items():
            reference['quests'].setdefault(i,{}).update({k:v for k,v in r.items() if k!='sha256'})
            reference['checksums'][i]=r['sha256']
        reference['compiledAt']=datetime.now(timezone.utc).isoformat()
        reference_path.write_text(json.dumps(reference,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        runtime=ROOT/'Guides/AllianceQuestData.lua'
        header=runtime.read_text(encoding='utf-8').split('F.AllianceQuestData = ',1)[0]
        runtime.write_text(header+'F.AllianceQuestData = {'+',\n'.join(f'[{i}]={serialize(r)}' for i,r in sorted(reference['quests'].items(),key=lambda pair:int(pair[0])))+'}\n',encoding='utf-8')
    estimates=chapter_estimates(audit,combat)
    report(audit,combat,estimates)
    for name,data in [('10_20_AUDIT',audit),('10_20_COMBAT',combat),('10_20_ROUGH_ESTIMATES',estimates)]:
        (ROOT/f'Data/{name}.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    entities=[]
    for g in sorted(route,key=lambda g:g['minLevel']):
        for s in g['steps']:
            if not s.get('questID') or s.get('classes'):continue
            for o in records[str(s['questID'])]['objectives']:
                pair=(o['kind'],o.get('id'))
                if o['kind'] in ('npc','item') and pair not in entities:entities.append(pair)
    for r in records.values():
        for o in r['objectives']:
            pair=(o['kind'],o.get('id'))
            if o['kind'] in ('npc','item') and pair not in entities:entities.append(pair)
    (a.cache/'entities.json').write_text(json.dumps([{'kind':k,'id':i} for k,i in entities]),encoding='utf-8')
    print(f'{len(route)} chapters, {len(records)} quests, {len(entities)} objective entities; {len(combat["pages"])} entity pages available')
    for g,e in zip(route,estimates['chapters']):print(g['id'],len(g['steps']),e['listedRequiredRewardXP'],e['roughTotalXPRange'],len(e['missing']))

if __name__=='__main__': main()
