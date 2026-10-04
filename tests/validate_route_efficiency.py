"""All chapter actions survive, retain ownership and use the reviewed orders."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'tools'))
from audit_01_10 import guides
a=json.loads((root/'Data/ROUTE_EFFICIENCY_AUDIT.json').read_text())
before=json.loads((root/'Data/ROUTE_EFFICIENCY_BEFORE.json').read_text())
live={g['id']:g for g in guides(1,30)}
assert len(live)==a['chaptersReviewed']==33
assert sum(g['changed'] for g in a['chapters'])==a['changedChapters']
for old,r in zip(before,a['chapters']):
 g=live[old['id']]
 assert [s['id'] for s in g['steps']]==r['after']
 assert {s['id']:(s['type'],s.get('questID')) for s in old['steps']}=={s['id']:(s['type'],s.get('questID')) for s in g['steps']}
 assert g['nextGuideID']==old['nextGuideID']
 positions={(s.get('questID'),s['type']):i for i,s in enumerate(g['steps']) if s.get('questID')}
 oldpositions={(s.get('questID'),s['type']):i for i,s in enumerate(old['steps']) if s.get('questID')}
 oldByID={s['id']:i for i,s in enumerate(old['steps'])}
 for s in g['steps']:
  q=s.get('questID');i=g['steps'].index(s)
  if s['type']=='objective' and (q,'pickup') in positions:assert positions[q,'pickup']<i
  if s['type']=='turnin' and (q,'objective') in positions and oldpositions[q,'objective']<oldByID[s['id']]:assert positions[q,'objective']<i
 if g['id']=='alliance-eastern-25-26':
  assert positions[57,'objective']<positions[156,'turnin']
 if g['id']=='alliance-eastern-26-27':
  assert positions[299,'objective']<positions[295,'turnin']
print('PASS: all 33 chapters, stable actions, chapter ownership and batched regional circuits')
