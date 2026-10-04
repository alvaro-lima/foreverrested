"""Audit every scheduled objective; supplement proven mob spawns, never NPC hand-ins."""
import json,sys
from pathlib import Path
from audit_01_10 import guides
from read_installed_questie import InstalledDB
ROOT=Path(__file__).resolve().parents[1]

def main():
 gs=guides(1,30)
 ref=json.loads((ROOT/'Data/alliance-reference.json').read_text())['quests']
 base=ROOT/'tests/validate.py';setup=base.read_text().split("lua.execute(r'''",2)
 ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
 F=ns['lua'].globals().F
 db=InstalledDB(ROOT.parent/'QuestieDB/QuestieDB_Forever.toc')
 zones={406:'Stonetalon Mountains',17:'The Barrens',493:'Moonglade',215:'Mulgore',130:'Silverpine Forest'}
 for _,q in F.AllianceQuestData.items():
  for _,p in q.locations.items():
   if p.areaID and p.zone:zones[int(p.areaID)]=p.zone
 rows=[];additions=[];unknown=[]
 scheduled={s['questID'] for g in gs for s in g['steps'] if s.get('questID') and s['type']=='objective'}
 public={}
 for filename in ('STARTER_COMBAT.json','10_20_COMBAT.json'):
  a=json.loads((ROOT/'Data'/filename).read_text())
  public.update(a.get('quests',{}))
 for qid in sorted(scheduled):
  raw=ref.get(str(qid),{});live=F.AllianceQuestData[qid]
  if not live:continue
  for index,o in enumerate(raw.get('objectives',[]),1):
   if o['action'] not in ('kill','collect'):continue
   source_ids=[o['id']] if o['action']=='kill' else []
   if o['action']=='collect':
    item=db.entity('Item',o['id']);source_ids=list(item.get(2,[]))
    source_ids += [int(p.entityID) for _,p in live.locations.items() if p.role=='sourcerequirement' and p.entityType==1 and p.entityID and p.item==o['name'] and p.source!='installed Forever QuestieDB']
    quest=db.entity('Quest',qid)
    if quest.get(11)==o['id'] or item.get(4) or item.get(6) or len(set(source_ids))>30:
     unknown.append({'questID':qid,'objective':o['name'],'reason':'Provided, vendor/crafted, or widespread incidental loot; not a dedicated hunting objective'})
     continue
    for po in public.get(str(qid),{}).get('objectives',[]):
     if po.get('id')==o['id']:
      source_ids+= [s['npcID'] for s in po.get('dropSources',[]) if s.get('npcID')]
    if not source_ids:
     unknown.append({'questID':qid,'objective':o['name'],'reason':'No proven mob source; may be gathering, delivery, item use or incomplete source data'})
     continue
   points=[p for _,p in live.locations.items() if p.role in ('requirement','sourcerequirement') and p.x is not None and p.y is not None and p.zone]
   match=[p for p in points if o['action']=='kill' and p.entityID==o['id'] or o['action']=='collect' and p.item==o['name'] and p.entityType==1]
   target=F.QuestTargets[qid]
   if target and target.location:
    if any(s.itemID==o['id'] for _,s in target.objectives.items()):match.append(target.location)
   row={'questID':qid,'title':raw.get('title'),'objectiveID':o['id'],'objective':o['name'],'type':o['action'],'sourceNPCIDs':sorted(set(source_ids)),'status':'Present' if match else 'Missing','addedLocations':[]}
   if source_ids:
    for npc in sorted(set(source_ids)):
     n=db.entity('Npc',npc)
     if o['action']=='collect' and n.get(6,0)!=0:continue
     spawns=n.get(7,{})
     if isinstance(spawns,list):spawns={i+1:v for i,v in enumerate(spawns) if v}
     if not isinstance(spawns,dict):continue
     for area,positions in spawns.items():
      usable=[p for p in positions if len(p)>=2 and 0<=p[0]<=100 and 0<=p[1]<=100 and p[:2]!=[0,0]]
      if area not in zones or not usable:continue
      # An actual recorded spawn, not an average that could fall off terrain.
      selected=[]
      for p in usable:
       if not any((p[0]-a[0])**2+(p[1]-a[1])**2<8.5**2 for a in selected):selected.append(p)
      for p in selected:
       point={'role':'requirement' if o['action']=='kill' else 'sourcerequirement','entityType':1,'entityID':npc,'name':n.get(1),'zone':zones[area],'areaID':area,'x':p[0]/100,'y':p[1]/100,'approximate':True,'source':'installed Forever QuestieDB'}
       if o['action']=='collect':point['item']=o['name']
       if not point['name']:continue
       additions.append((qid,point));row['addedLocations'].append(point)
    preferred={p.zone for p in match if p.zone}
    if not preferred:preferred={p.zone for _,p in live.locations.items() if p.role in ('requirement','sourcerequirement') and p.zone}
    if not preferred:preferred={p.zone for _,p in live.locations.items() if p.role=='start' and p.zone}
    local_points=[p for p in row['addedLocations'] if p['zone'] in preferred]
    if local_points:
     rejected=[p for p in row['addedLocations'] if p not in local_points]
     additions=[(q,p) for q,p in additions if q!=qid or p not in rejected]
     row['addedLocations']=local_points
    if row['addedLocations'] and not match:row['status']='Fixed'
   rows.append(row)
 # A second run must retain existing supplements and remain reproducible.
 existing=ROOT/'Data/HUNTING_LOCATION_SUPPLEMENTS.json'
 old=[(q,p) for q,p in (json.loads(existing.read_text()) if existing.exists() else []) if q!=1073 and (q!=385 or p['zone']=='Loch Modan')]
 merged={json.dumps([q,p],sort_keys=True):(q,p) for q,p in old+additions}
 supplements=list(merged.values())
 existing.write_text(json.dumps(supplements,indent=2)+'\n')
 def lua(v):
  if isinstance(v,str):return json.dumps(v)
  if isinstance(v,bool):return 'true' if v else 'false'
  return str(v)
 lines=['local _,F=...','-- Recorded Forever QuestieDB mob spawns. Approximate hunting areas.','-- Generated by tools/audit_hunting_locations.py; no runtime Questie dependency.']
 for q,p in supplements:lines.append(f'table.insert(F.AllianceQuestData[{q}].locations,{{'+','.join(k+'='+lua(v) for k,v in p.items())+'})')
 (ROOT/'Guides/Alliance_HuntingLocations.lua').write_text('\n'.join(lines)+'\n')
 out={'chapters':len(gs),'scheduledObjectiveQuests':len(scheduled),'huntingObjectives':len(rows),'fixedObjectives':sum(r['status']=='Fixed' for r in rows),'supplementedQuestIDs':sorted({q for q,p in supplements}),'missingHuntingObjectives':[r for r in rows if r['status']=='Missing'],'objectives':rows,'acquisitionNeedsClassification':unknown,'databaseSHA256':db.sha256}
 (ROOT/'Data/HUNTING_LOCATION_AUDIT.json').write_text(json.dumps(out,indent=2)+'\n')
 text=['# Hunting location audit','',f"Reviewed {len(gs)} playable chapters and {len(scheduled)} scheduled objective quests. {len(rows)} identified hunting objectives; {len(out['missingHuntingObjectives'])} missing proven hunting locations after supplementation.",'',f"Supplemented quests: {', '.join(map(str,out['supplementedQuestIDs']))}.",'','Spawn coordinates come from installed Forever QuestieDB or existing sourced quest metadata. Pins represent approximate hunting areas, not guaranteed current positions of moving mobs. Nearby object gathering, supplied quest items, vendor/crafted goods and delivery objectives are not treated as hunts.','',f'{len(unknown)} collection inputs are recorded separately for acquisition classification. This does not establish that every unknown collection item is noncombat; items with no proven mob source remain unverified.','', '## Unverified acquisition inputs','']
 text += [f"- Quest {r['questID']}: {r['objective']} — {r['reason']}" for r in unknown]
 (ROOT/'Data/HUNTING_LOCATION_AUDIT.md').write_text('\n'.join(text)+'\n')
 print({k:v for k,v in out.items() if k not in ('objectives','acquisitionNeedsClassification')})
 print('Non-hunting/unknown acquisitions:',len(unknown),'new locations:',len(additions))
if __name__=='__main__':main()
