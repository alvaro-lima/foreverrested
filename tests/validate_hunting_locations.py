"""Identified hunting objectives have usable areas; fixes stay sourced and local."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from audit_01_10 import guides
base=root/'tests/validate.py';setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
F=ns['lua'].globals().F
a=json.loads((root/'Data/HUNTING_LOCATION_AUDIT.json').read_text())
assert a['chapters']==33 and not a['missingHuntingObjectives']
for r in a['objectives']:
 q=F.AllianceQuestData[r['questID']]
 points=[p for _,p in q.locations.items() if p.role in ('requirement','sourcerequirement') and p.zone and p.x is not None and p.y is not None and 0<=p.x<=1 and 0<=p.y<=1]
 matches=[p for p in points if r['type']=='kill' and p.entityID==r['objectiveID'] or r['type']=='collect' and p.item==r['objective'] and p.entityType==1]
 record=F.QuestTargets[r['questID']]
 assert matches or record and record.location,(r['questID'],r['objective'])
supp=json.loads((root/'Data/HUNTING_LOCATION_SUPPLEMENTS.json').read_text())
assert not any(q==1073 for q,p in supp),'potions are not invented hunting destinations'
assert all(p['zone']=='Loch Modan' for q,p in supp if q==385),'lodge hunt remains local'
assert any(q==412 and p['name']=='Leper Gnome' for q,p in supp)
print('PASS: hunting coverage, source coordinates, collection matching and local destinations')
