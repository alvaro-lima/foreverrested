"""Current objectives, conservative budgets and level-based recovery across both routes."""
import json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from audit_01_10 import guides,normal_kill_xp
a=json.loads((root/'Data/20_30_AUDIT.json').read_text(encoding='utf-8'))
r=json.loads((root/'Data/alliance-reference.json').read_text(encoding='utf-8'))
assert len(a['guides'])==11 and len(a['quests'])==138
assert not a['requiredPrerequisiteGaps']
assert a['quests']['484']['objectives'][0]['count']==6
assert normal_kill_xp(29,29)==190 and normal_kill_xp(30,30)==195
assert normal_kill_xp(29,21)==0
for i,q in a['quests'].items():
 assert q['objectives']==r['quests'][i]['objectives']
 assert q['sha256']==r['checksums'][i]
for g,b in zip(a['guides'],a['budgets']):
 ids={s['questID'] for s in g['steps'] if s.get('questID') and s['type']=='turnin' and not s.get('optional') and not s.get('classes')}
 assert b['listedRequiredQuestXP']==sum(a['quests'][str(i)].get('listedXP',0) for i in ids)
 assert not {470,174,175,177,181}&ids
 assert b['recoverySteps'][-1]['targetLevel']==g['maxLevel']
 assert all(s.get('zone') and s.get('x') and s.get('y') for s in b['recoverySteps'])
 assert not b['missing'] or b['roughTotalXPRange'] is None
final=next(b for b in a['budgets'] if b['guideID']=='alliance-eastern-29-30')
assert {222,223}<=set(final['requiredTurninIDs'])
base=root/'tests/validate.py';setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local level=20
function UnitLevel() return level end
for _,id in ipairs(F.GuideLibrary.order) do
 local g=F.GuideLibrary.guides[id]
 if g.sourceGuideID and g.minLevel>=20 and g.minLevel<30 then
  for _,s in ipairs(g.steps) do
   if s.levelRecovery then
    level=s.targetLevel-1
    assert(not F.GuideEngine:Done(s),'recovery cannot complete below target')
    level=s.targetLevel
    assert(F.GuideEngine:Done(s),'recovery completes at target')
   end
  end
 end
end
local coast=F.GuideLibrary.guides['alliance-kalimdor-20-24']
local positions={}
for i,s in ipairs(coast.steps) do
 if s.questID then positions[s.questID..':'..s.type]=i end
end
assert(positions['1007:pickup']<positions['1007:objective'])
assert(positions['1007:turnin']<positions['1009:pickup'],'statuette unlocks Ruuzel')
assert(positions['1009:objective']<positions['1008:turnin'],'coastal objectives precede Astranaar return')
assert(positions['1009:turnin']<positions['1008:turnin'],'local Talen hand-in precedes Astranaar')
''')
print('PASS: all eleven 20-30 chapters, evidence, required XP and live recovery')

