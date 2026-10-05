"""Audit all 20-30 routes using installed Forever facts plus current objective tables."""
import argparse,hashlib,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
from audit_01_10 import guides,objectives,normal_kill_xp
from read_installed_questie import InstalledDB
from build_alliance_reference import extract
from refresh_quest_data import lua as serialize
ROOT=Path(__file__).resolve().parents[1]
ZONES={11:'Wetlands',10:'Duskwood',331:'Ashenvale',406:'Stonetalon Mountains',44:'Redridge Mountains'}

def main():
 p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--apply',action='store_true');p.add_argument('--use-recorded',action='store_true',help='Retain existing sourced facts when a cached page is unavailable');a=p.parse_args()
 previous=json.loads((ROOT/'Data/20_30_AUDIT.json').read_text(encoding='utf-8')) if a.use_recorded else {}
 db=InstalledDB(ROOT.parent/'QuestieDB/QuestieDB_Forever.toc');route=guides(20,30)
 refpath=ROOT/'Data/alliance-reference.json';ref=json.loads(refpath.read_text(encoding='utf-8'))
 ids=sorted({s['questID'] for g in route for s in g['steps'] if s.get('questID')})
 from lupa.lua51 import LuaRuntime
 from build_classic_policy import parse_literals
 dropfile=ROOT.parent/'QuestieDB/support/Forever/DropTables/classicItemDrops.lua'
 droptext=dropfile.read_text(encoding='utf-8');body=re.search(r'\[\[(return\s*\{.*?)\]\]',droptext,re.S)[1]
 rates=parse_literals(re.sub(r'--[^\n]*','',body),LuaRuntime(unpack_returned_tuples=True))
 records={};combat={};gaps=[];entities={};differences=[]
 for i in ids:
  page=a.cache/f'quest-{i}.html';local=db.entity('Quest',i)
  if a.use_recorded and str(i) in previous.get('quests',{}):
   records[str(i)]=dict(ref['quests'][str(i)]);records[str(i)]['sha256']=ref['checksums'][str(i)]
   combat[str(i)]=previous['combat'][str(i)];continue
  if not page.exists():
   if str(i) in previous.get('quests',{}):
    records[str(i)]=previous['quests'][str(i)];combat[str(i)]=previous['combat'][str(i)];continue
   raise ValueError(f'Missing current quest page {i}')
  raw=page.read_text(encoding='utf-8-sig');record=extract(i,raw,{i:set(ref['quests'].get(str(i),{}).get('classes',[]))})
  assert record['objectives']==objectives(raw)
  record['sha256']=hashlib.sha256(page.read_bytes()).hexdigest();record['retrievedAt']=datetime.fromtimestamp(page.stat().st_mtime,timezone.utc).isoformat()
  record['installedQuestieComparison']={'present':bool(local),'minLevel':local.get(4),'questLevel':local.get(5),'objectiveCountsAvailable':False}
  if local and record.get('minLevel')!=local.get(4):differences.append({'questID':i,'field':'minLevel','page':record.get('minLevel'),'local':local.get(4)})
  records[str(i)]=record
  obs=[]
  for obj in record['objectives']:
   out=dict(obj)
   if obj['action']=='kill':
    n=db.entity('Npc',obj['id']);out['mob']={'name':n.get(1),'minlevel':n.get(4),'maxlevel':n.get(5),'rank':n.get(6,0),'zones':[ZONES.get(int(z),str(z)) for z in (n.get(7,{}) or {})]};entities[f'Npc:{obj["id"]}']=n
   elif obj['action']=='collect':
    item=db.entity('Item',obj['id']);entities[f'Item:{obj["id"]}']=item
    out['objectSourceIDs']=item.get(3,[]);out['dropSources']=[];out['providedItem']=local.get(11)==obj['id']
    for npc in item.get(2,[]):
     n=db.entity('Npc',npc);r=rates[obj['id']];pct=r[npc] if r is not None else None
     out['dropSources'].append({'npcID':npc,'name':n.get(1),'minlevel':n.get(4),'maxlevel':n.get(5),'rank':n.get(6,0),'zones':[ZONES.get(int(z),str(z)) for z in (n.get(7,{}) or {})],'publishedLegacyDropChance':pct/100 if isinstance(pct,(int,float)) and 0<pct<=100 else None})
   obs.append(out)
  combat[str(i)]=obs
 budgets=[];seen={}
 for g in route:
  branch='kalimdor' if 'kalimdor' in g['id'] else 'eastern';done=seen.setdefault(branch,set());reward=0;optional=set();shared={};missing=[];warnings=[];required=set()
  for s in g['steps']:
   i=s.get('questID')
   if not i:continue
   if s.get('optional') or s.get('classes'):
    if s['type']=='turnin':optional.add(i)
    continue
   local=db.entity('Quest',i)
   if s['type']=='pickup':
    for prev in local.get(12,[]):
     if prev>0 and prev not in done:gaps.append({'guideID':g['id'],'questID':i,'missingPriorTurnin':prev})
    ps=[v for v in local.get(13,[]) if v>0]
    if ps and not any(v in done for v in ps):gaps.append({'guideID':g['id'],'questID':i,'missingAnyPriorTurnin':ps})
   if s['type']=='turnin':reward+=records[str(i)].get('listedXP',0);done.add(i);required.add(i)
   if s['type']!='objective':continue
   for obj in combat[str(i)]:
    if obj['action']=='interact':continue
    if obj['action']=='kill':mob=obj['mob'];npc=obj['id'];count=obj['count']
    else:
     if obj.get('providedItem'):
      warnings.append(f"Quest {i}, {obj['name']}: noncombat acquisition exists; no kills assumed");continue
     if obj.get('objectSourceIDs'):
      missing.append(f"Quest {i}, {obj['name']}: object sources require acquisition verification; incidental containers do not prove zero combat");continue
     candidates=[m for m in obj.get('dropSources',[]) if m.get('publishedLegacyDropChance') and m.get('rank')==0 and m.get('minlevel') and any(z in (g['zone'],'Stonetalon Mountains' if g['zone']=='Ashenvale' else g['zone']) for z in m['zones'])]
     if not candidates:missing.append(f"Quest {i}, {obj['name']}: usable local drop/acquisition evidence");continue
     suitable=[m for m in candidates if m['minlevel']<=g['minLevel']+3] or candidates
     mob=max(suitable,key=lambda m:m['publishedLegacyDropChance']);npc=mob['npcID'];count=__import__('math').ceil(obj['count']/mob['publishedLegacyDropChance'])
    if not mob.get('minlevel') or not mob.get('maxlevel') or mob.get('rank')!=0:missing.append(f'Quest {i}: normal-mob XP model');continue
    xp=[normal_kill_xp(g['minLevel'],l) for l in (mob['minlevel'],mob['maxlevel'])]
    key=(s.get('legacyGroupID',s['id']),npc)
    shared[key]={'npcID':npc,'kills':max(count,shared.get(key,{}).get('kills',0)),'approxXPPerKillRange':xp}
  totals=[reward+sum(m['kills']*m['approxXPPerKillRange'][j] for m in shared.values()) for j in (0,1)]
  budgets.append({'guideID':g['id'],'title':g['title'],'requiredTurninIDs':sorted(required),'excludedOptionalTurninIDs':sorted(optional),'listedRequiredQuestXP':reward,'knownCombatGroups':list(shared.values()),'roughTotalXPRange':None if missing else totals,'knownRewardAndCombatXPRange':totals,'missing':sorted(set(missing)),'warnings':sorted(set(warnings)),'recoverySteps':[s for s in g['steps'] if s.get('levelRecovery')]})
 output={'schemaVersion':1,'source':'QuestieDB/QuestieDB_Forever.toc (installed beta addon)','installedVersion':db.meta['Version'],'buildCommit':db.meta['X-BUILD-COMMIT'],'localSHA256':db.sha256,'dropTableSHA256':hashlib.sha256(dropfile.read_bytes()).hexdigest(),'guides':route,'quests':records,'installedEntities':entities,'combat':combat,'differences':differences,'requiredPrerequisiteGaps':gaps,'budgets':budgets,'optionalXPExcluded':True,'limits':['Installed Forever objective quantities are unavailable; objective text may retain Classic counts. Current page tables supply quantities.','Installed Forever support drop/XP tables are Classic-derived; samples are not verified current-build conditional drop rates.','Mob XP is a Classic normal solo estimate at chapter entry; actual level, modifiers, scripted combat and acquisition can differ.','Shared group/NPC kills use the maximum count; multi-source expected drop overlap is not simulated in this model. Unknown inputs remain unknown.']}
 (ROOT/'Data/20_30_AUDIT.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 lines=['# Levels 20–30 audit','',f'Checked {len(route)} playable chapters and {len(records)} distinct current Forever quest pages. Required prerequisite gaps: {len(gaps)}.','',
 '## Changes','',
 '- Every chapter has a concrete normal-enemy recovery location and an actual-level exit check. Pickup level gates get recovery checks where needed.',
 '- Optional and class-specific quest XP contributes zero to the required budget.',
 '- Rare Sida bag loot and the Bronze Tube / high-level ogre star branch are optional.',
 '- Final Duskwood requires quests 222 and 223, completing the ordinary worgen chain at level 29. Stable action IDs are retained.',
 '- Objective tables were refreshed without importing third-party route prose. Young Crocolisk Skins requires six skins; installed text still says four.',
 '- Collection objectives remain owned by the chapter scheduling them.','',
 '## Chapter results','',
 '| Chapter | Required listed quest XP | Rough reward + combat XP | Unresolved acquisition inputs |',
 '|---|---:|---|---:|']
 for b in budgets:
  estimate='Unknown' if b['roughTotalXPRange'] is None else '–'.join(str(v) for v in b['roughTotalXPRange'])
  lines.append(f"| {b['title']} | {b['listedRequiredQuestXP']:,} | {estimate} | {len(b['missing'])} |")
 lines+=['','These routes can require substantial additional combat. The recovery checks make this explicit; quest work alone is not guaranteed to fill each bracket.','',
 '## Evidence and limits','',
 f'Installed QuestieDB {db.meta["Version"]}, baked Forever flavor, build {db.meta["X-BUILD-COMMIT"]}. Local database supplies IDs, prerequisite relationships, normal enemy levels and spawn locations. Objective quantities come from current Forever pages; local objective tuples omit quantities.',
 '', '[Current Young Crocolisk Skins objective table](https://www.wowhead.com/forever/quest=484/young-crocolisk-skins). Full per-quest source URLs, retrieval dates and hashes are in `20_30_AUDIT.json`.', '']
 lines+=['- '+limit for limit in output['limits']]
 lines+=['- Collection estimates assume one item per successful drop; quest-specific multi-item drops and stack sizes have not been verified.']
 lines+=['','## Unresolved acquisition evidence','']
 for b in budgets:
  if b['missing']:
   lines.append('### '+b['title']);lines.append('');lines+=['- '+m for m in b['missing']];lines.append('')
 (ROOT/'Data/20_30_AUDIT.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
 if a.apply:
  if gaps:raise ValueError(f'Unresolved required prerequisites: {gaps}')
  for i,r in records.items():ref['quests'].setdefault(i,{}).update({k:v for k,v in r.items() if k!='sha256'});ref['checksums'][i]=r['sha256']
  refpath.write_text(json.dumps(ref,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
  runtime=ROOT/'Guides/AllianceQuestData.lua';header=runtime.read_text(encoding='utf-8').split('F.AllianceQuestData = ',1)[0]
  runtime.write_text(header+'F.AllianceQuestData = {'+',\n'.join(f'[{i}]={serialize(r)}' for i,r in sorted(ref['quests'].items(),key=lambda x:int(x[0])))+'}\n',encoding='utf-8')
 print(len(route),'chapters',len(records),'quests; prerequisite gaps',gaps)
 for g,b in zip(route,budgets):print(g['title'],len(g['steps']),b['listedRequiredQuestXP'],b['roughTotalXPRange'],len(b['missing']))

if __name__=='__main__':main()
