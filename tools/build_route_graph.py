"""Physical NPC/objective nodes plus prerequisite-constrained action graphs.

Distances are map-coordinate proxies, never travel times. Cross-zone connections
and unavailable objective destinations deliberately have unknown weights.
"""
import json,math
from pathlib import Path
from audit_01_10 import guides
from read_installed_questie import InstalledDB
ROOT=Path(__file__).resolve().parents[1]

def main():
 route=guides(1,30)
 ref=json.loads((ROOT/'Data/alliance-reference.json').read_text())['quests']
 db=InstalledDB(ROOT.parent/'QuestieDB/QuestieDB_Forever.toc')
 nodes={};chapters=[];edges={}
 def node(p):
  key=f"{p['zone']}:{p.get('entityType')}:{p.get('entityID')}:{p['x']:.4f}:{p['y']:.4f}"
  nodes.setdefault(key,{'id':key,'zone':p['zone'],'x':p['x'],'y':p['y'],'name':p.get('name'),'entityID':p.get('entityID'),'entityType':p.get('entityType'),'approximate':p.get('approximate',True)})
  return key
 def distance(a,b):
  x,y=nodes[a],nodes[b]
  return math.hypot(x['x']-y['x'],x['y']-y['y']) if x['zone']==y['zone'] else None
 for g in route:
  actions=[];constraints=[];questactions={};physical=set()
  for s in g['steps']:
   q=s.get('questID');kind=s['type']
   roles={'pickup':{'start'},'turnin':{'end'},'objective':{'requirement','sourcerequirement'}}.get(kind,set())
   destinations=[node(p) for p in ref.get(str(q),{}).get('locations',[]) if p.get('role') in roles and p.get('x') is not None and p.get('y') is not None]
   if not q and s.get('zone') and s.get('x') is not None and s.get('y') is not None:
    destinations=[node({'zone':s['zone'],'x':s['x'],'y':s['y'],'name':s.get('text'),'entityID':s['id'],'entityType':'checkpoint'})]
   physical.update(destinations)
   actions.append({'id':s['id'],'questID':q,'type':kind,'optional':bool(s.get('optional')),'candidateNodeIDs':destinations,'destinationKnown':bool(destinations),'levelGate':s.get('targetLevel'),'destinationSemantics':'Reference candidates; mob-drop sources are alternatives, not a requirement to visit every spawn'})
   if q:questactions[q,kind]=s['id']
  for (q,kind),action in questactions.items():
   if kind=='objective' and (q,'pickup') in questactions:constraints.append({'from':questactions[q,'pickup'],'to':action,'reason':'accept before objective'})
   if kind=='turnin' and (q,'objective') in questactions:
    # Delivery-only entries sometimes retain a legacy interaction action.
    if ref.get(str(q),{}).get('objectives'):constraints.append({'from':questactions[q,'objective'],'to':action,'reason':'objective before hand-in'})
   if kind=='pickup':
    local=db.entity('Quest',q)
    for prev in local.get(12,[]):
     if (prev,'turnin') in questactions:constraints.append({'from':questactions[prev,'turnin'],'to':action,'reason':'all required prerequisite'})
    alternatives=[questactions[prev,'turnin'] for prev in local.get(13,[]) if (prev,'turnin') in questactions]
    if alternatives:constraints.append({'anyFrom':alternatives,'to':action,'reason':'one prerequisite alternative'})
  # Nearest physical neighbors are candidate walking links. Terrain remains
  # unknown, so this graph must not be presented as an executable shortest path.
  for a in physical:
   nearest=sorted([(distance(a,b),b) for b in physical if a!=b and distance(a,b) is not None])[:5]
   for cost,b in nearest:edges[a,b]={'from':a,'to':b,'coordinateDistance':cost,'travelSeconds':None,'terrainVerified':False}
  chapters.append({'id':g['id'],'title':g['title'],'actionOrder':[s['id'] for s in g['steps']],'actions':actions,'precedenceConstraints':constraints,'nextGuideID':g.get('nextGuideID')})
 output={'schemaVersion':1,'kind':'prerequisite-constrained route graph','chapters':chapters,'nodes':list(nodes.values()),'candidateTravelEdges':list(edges.values()),'limits':['Normalized map distances are not comparable between differently sized zones.','No road, obstacle, flight, boat, hearthstone or danger costs have been measured.','Cross-zone travel times and unverified destinations remain unknown.','Quest-log capacity and acquisition overlap must be modeled before optimizing a full route.','This graph records facts and candidate connections; it does not claim a globally fastest itinerary.']}
 (ROOT/'Data/ROUTE_GRAPH.json').write_text(json.dumps(output,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 print(len(chapters),'chapters;',len(nodes),'physical nodes;',len(edges),'candidate travel connections')
if __name__=='__main__':main()
