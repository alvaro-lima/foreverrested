"""Review every playable chapter; emit conservative, explicit action orders.

Only move pickups at an already visited hub, or defer returns for nearby work.
Never cross a nonquest checkpoint, move objectives between chapters, or reorder
an unlock. Approximate map distances identify opportunities, not travel times.
"""
import json,math,sys
from pathlib import Path
from audit_01_10 import guides
from read_installed_questie import InstalledDB
ROOT=Path(__file__).resolve().parents[1]

def main():
 before=json.loads((ROOT/'Data/ROUTE_EFFICIENCY_BEFORE.json').read_text())
 ref=json.loads((ROOT/'Data/alliance-reference.json').read_text())['quests']
 db=InstalledDB(ROOT.parent/'QuestieDB/QuestieDB_Forever.toc')
 local={i:db.entity('Quest',i) for i in {s['questID'] for g in before for s in g['steps'] if s.get('questID')}}
 def priors(s):
  q=local.get(s.get('questID'),{})
  return set(s.get('auditPrerequisites',[]))|set(s.get('auditPrerequisitesAny',[]))|set(q.get(12,[]))|set(q.get(13,[]))|{i for i,r in local.items() if r.get(22)==s.get('questID')}
 def points(s,role):
  return [p for p in ref.get(str(s.get('questID')),{}).get('locations',[]) if p.get('role') in role and p.get('x') is not None and p.get('y') is not None]
 def near(a,b,radius):
  return any(x['zone']==y['zone'] and math.hypot(x['x']-y['x'],x['y']-y['y'])<=radius for x in a for y in b)
 def barrier(s):
  q=ref.get(str(s.get('questID')),{});title=q.get('title','').lower()
  return not s.get('questID') or not local.get(s.get('questID')) or s.get('classes') or s.get('critical') or s.get('unlockChain') or any(t in title for t in ('escort','challenge','call of ','protecting the'))
 def depends(s,prior):
  return prior in priors(s)
 reports=[];orders={}
 for g in before:
  steps=list(g['steps']);moves=[]
  # Pull independent pickups into an earlier visit to the same small hub.
  for original in list(steps):
   if original['type']!='pickup' or barrier(original):continue
   index=steps.index(original)
   for anchor in range(max(0,index-24),index):
    a=steps[anchor];between=steps[anchor:index]
    if a['type']!='pickup' or barrier(a) or not near(points(a,{'start'}),points(original,{'start'}),.035):continue
    if any(barrier(s) for s in between):continue
    if any(s['type']=='turnin' and depends(original,s['questID']) for s in between):continue
    if not any(s['type']=='objective' for s in between):continue
    steps.pop(index);steps.insert(anchor+1,original)
    moves.append({'id':original['id'],'reason':'Accept independent nearby hub work before leaving','before':a['id']});break
  # Defer a return only for objectives already accepted on the same circuit.
  for original in list(steps):
   if original['type']!='turnin' or barrier(original):continue
   index=steps.index(original)
   own=[s for s in steps[:index] if s.get('questID')==original['questID'] and s['type']=='objective']
   if not own:continue
   area=points(own[-1],{'requirement','sourcerequirement'})
   if not area:continue
   target=None
   for j in range(index+1,min(len(steps),index+18)):
    s=steps[j]
    if barrier(s) or depends(s,original['questID']):break
    if s['type']=='pickup':break
    if s['type']=='turnin' and not near(points(original,{'end'}),points(s,{'end'}),.035):break
    if s['type']=='objective':
     if not near(area,points(s,{'requirement','sourcerequirement'}),.12):break
     target=j
   if target is not None:
    dest=steps[target]['id'];steps.pop(index);steps.insert(target,original)
    moves.append({'id':original['id'],'reason':'Finish nearby accepted objectives before returning to the hub','after':dest})
  # Explicit same-area Raven Hill and Darkshire circuits, including carry-in
  # objectives accepted in their earlier chapter. No objective ownership moves.
  manual={
   'alliance-eastern-22-24':[(56,'turnin',245,'objective')],
   'alliance-eastern-25-26':[(57,'objective',156,'objective'),(90,'objective',57,'objective'),(57,'turnin',156,'turnin'),(90,'turnin',57,'turnin')],
   'alliance-eastern-26-27':[(299,'objective',295,'objective'),(299,'turnin',295,'turnin')],
   'alliance-eastern-29-30':[(222,'pickup',58,'pickup'),(222,'objective',58,'objective'),(101,'objective',222,'objective'),(58,'turnin',101,'objective'),(101,'turnin',58,'turnin')],
  }
  for q,kind,afterq,afterkind in manual.get(g['id'],[]):
   a=next(s for s in steps if s.get('questID')==q and s['type']==kind)
   b=next(s for s in steps if s.get('questID')==afterq and s['type']==afterkind)
   steps.remove(a);steps.insert(steps.index(b)+1,a)
   moves.append({'id':a['id'],'after':b['id'],'reason':'Reviewed regional circuit: shared work before hub returns'})
  assert {s['id'] for s in steps}=={s['id'] for s in g['steps']}
  # Required prerequisites and each quest's own actions must retain ordering.
  position={(s.get('questID'),s['type']):i for i,s in enumerate(steps) if s.get('questID') and not s.get('optional')}
  originalPosition={(s.get('questID'),s['type']):i for i,s in enumerate(g['steps']) if s.get('questID') and not s.get('optional')}
  for s in steps:
   i=steps.index(s);q=s.get('questID')
   if s['type'] in ('objective','turnin') and (q,'pickup') in position:assert position[q,'pickup']<i
   if s['type']=='turnin' and (q,'objective') in position:assert position[q,'objective']<i
   if s['type']=='pickup':
    for prev in priors(s):
     if (prev,'turnin') in position and originalPosition[prev,'turnin']<g['steps'].index(s):
      assert position[prev,'turnin']<i,(g['id'],prev,q,s['id'])
  changed=[s['id'] for s in steps]!=[s['id'] for s in g['steps']]
  if changed:orders[g['id']]=[s['id'] for s in steps]
  uncertain=sorted({s['questID'] for s in steps if s.get('questID') and not local.get(s['questID'])})
  reports.append({'guideID':g['id'],'title':g['title'],'changed':changed,'moves':moves,'incompleteLocalDependencyQuestIDs':uncertain,'before':[s['id'] for s in g['steps']],'after':[s['id'] for s in steps]})
 output={'chaptersReviewed':len(reports),'changedChapters':len(orders),'limits':['Hub and objective locations are approximate. No travel-time savings are claimed.','Unknown geography and dependency chains retain their authored order; remaining serial work is not automatically a defect.','Quests absent from installed QuestieDB are not reordered automatically. Zephras story stages still need stronger dependency evidence before further batching.','No objective changes chapter and no action IDs are removed.'],'chapters':reports}
 (ROOT/'Data/ROUTE_EFFICIENCY_AUDIT.json').write_text(json.dumps(output,indent=2)+'\n')
 lines=['# Route efficiency review','',f'All {len(reports)} playable chapters reviewed; {len(orders)} chapters reordered.','',
 'Collect available nearby quests before leaving, complete compatible objectives on the same circuit, then combine hub returns. Prerequisite hand-ins remain before their follow-ups.','',
 '| Chapter | Result | Action moves |','|---|---|---:|']
 lines += [f"| {r['title']} | {'Reordered' if r['changed'] else 'Dependency evidence incomplete' if 'zephras' in r['guideID'] else 'Existing batches / gated stages retained'} | {len(r['moves'])} |" for r in reports]
 lines+=['','## Limits','']+['- '+s for s in output['limits']]
 (ROOT/'Data/ROUTE_EFFICIENCY_AUDIT.md').write_text('\n'.join(lines)+'\n')
 # Plain readable Lua strings, preserving existing stable action identities.
 rows=['local _,F=...','-- Reviewed chapter orders; no actions or chapter ownership changes.','local orders={']
 rows += ['['+json.dumps(k)+']={'+','.join(json.dumps(s) for s in v)+'},' for k,v in orders.items()]
 rows += ['}','for id,order in pairs(orders) do',' local g=assert(F.GuideLibrary.guides[id]);local byID={}',' for _,s in ipairs(g.steps) do byID[s.id]=s end',' local steps={}',' for _,key in ipairs(order) do steps[#steps+1]=assert(byID[key],key);byID[key]=nil end',' assert(not next(byID),"Unscheduled action in "..id)',' g.steps=steps;g.revision=g.revision+1','end']
 (ROOT/'Guides/Alliance_RouteOrder.lua').write_text('\n'.join(rows)+'\n')
 print(len(reports),'reviewed;',len(orders),'reordered')
 for r in reports:print(r['title'],len(r['moves']))
if __name__=='__main__':main()

