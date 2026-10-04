"""10-20 quest evidence, optional XP exclusion, delivery semantics and live handoffs."""
import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from audit_01_10 import normal_kill_xp
from build_starter_combat import chapter_estimates
base=root/'tests/validate.py'
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
a=json.loads((root/'Data/10_20_AUDIT.json').read_text(encoding='utf-8'))
r=json.loads((root/'Data/alliance-reference.json').read_text(encoding='utf-8'))
c=json.loads((root/'Data/10_20_COMBAT.json').read_text(encoding='utf-8'))
latest=json.loads((root/'Data/20_30_AUDIT.json').read_text(encoding='utf-8'))
assert len(a['guides'])==12 and len(a['quests'])==147
for i,q in a['quests'].items():
 assert q['objectives']==r['quests'][i]['objectives']
 # A shared quest may have been fetched again by the later audit.
 current=latest['quests'].get(i,q)
 assert current['objectives']==q['objectives']
 assert current['sha256']==r['checksums'][i]
assert a['quests']['1339']['objectives']==[], 'Stormpike introduction is delivery, not kobold ears'
assert [o['count'] for o in a['quests']['38']['objectives']]==[3,3,3,3]
assert a['quests']['92840']['objectives'][0]['action']=='interact'
assert a['quests']['92834']['objectives'][0]['count']==10
assert a['quests']['966']['objectives'][0]['count']==4
assert normal_kill_xp(12,12)==105
assert normal_kill_xp(15,15)==120
assert normal_kill_xp(15,9)==0
assert normal_kill_xp(20,20)==145
assert len(c['pages'])==159
assert c['quests']['125']['objectives'][0]['acquisition']=='object-loot', 'Sunken quest chest is not incidental chest loot'
assert c['quests']['151']['objectives'][0]['acquisition']=='object-loot'
assert c['quests']['153']['objectives'][0]['acquisition']=='mob-drop', 'Random bandana chest drops do not remove required combat'
assert c['quests']['4762']['objectives'][0]['acquisition']=='item-use'
assert c['quests']['4812']['objectives'][0]['acquisition']=='item-use'
# Ten kills of each mob already supply ten expected shared drops at 50%.
fake={'quests':{'1':{},'2':{}},'guides':[{'id':'shared','title':'Shared','minLevel':10,'zone':'Test','steps':[{'id':'kill','legacyGroupID':'loop','questID':1,'type':'objective'},{'id':'drop','legacyGroupID':'loop','questID':2,'type':'objective'}]}]}
mob={'approxSoloNormalXPByPlayerLevel':{'10':[95,95]}}
sources=[{'npcID':i,'dropChance':.5,'classification':0,'minlevel':10,'maxlevel':10,'zones':['Test'],'approxKillsForObjective':20,**mob} for i in (1,2)]
fake_combat={'quests':{'1':{'objectives':[{'action':'kill','id':i,'count':10,'mob':mob} for i in (1,2)]},'2':{'objectives':[{'action':'collect','name':'Shared drop','count':10,'acquisition':'mob-drop','dropSources':sources}]}}}
assert chapter_estimates(fake,fake_combat)['chapters'][0]['knownCombatXPRange']==[1900,1900], 'Shared drops must not create a second full hunt'
old_ids=json.loads((root/'Data/10_20_ACTION_IDS.json').read_text())
for g in a['guides']:
 for s in g['steps']:
  previous=old_ids[g['sourceGuideID']].get(f"{s['type']}:{s.get('questID')}")
  if previous:assert previous==s['id'], f'Action identity changed: {previous}'
# Optional and class-specific actions must contribute zero baseline XP.
e=chapter_estimates(a,c)
for g,result in zip(a['guides'],e['chapters']):
 eligible={s['questID'] for s in g['steps'] if s.get('questID') and s['type']=='turnin' and not s.get('optional') and not s.get('classes') and not a['quests'][str(s['questID'])].get('requiredClasses')}
 assert result['listedRequiredRewardXP']==sum(a['quests'][str(i)].get('listedXP',0) for i in eligible)
 if g['id']=='alliance-loch-east-13-15':assert not {217,257,258}&eligible
 if g['id']=='alliance-zephras-exit-12-14':assert not eligible and result['listedRequiredRewardXP']==0
ns['lua'].execute(r'''
F.LoadDatabase()
local L,E=F.GuideLibrary,F.GuideEngine
local level=10
function UnitLevel() return level end
function UnitXP() return 200 end
function UnitXPMax() return 900 end
local count,mainland,island=0,0,0
for _,id in ipairs(L.order) do
 local g=L.guides[id]
 if g.sourceGuideID and g.minLevel>=10 and g.minLevel<20 then
  count=count+1
  local threshold=g.minLevel
  for _,s in ipairs(g.steps) do
   if s.levelRecovery then
    assert(s.zone==g.zone and s.x and s.y and not s.questID and not s.alongside)
    threshold=math.max(threshold,s.targetLevel)
   elseif s.type=='pickup' and s.questID and not s.optional and not s.classes then
    assert((F.AllianceQuestData[s.questID].minLevel or 1)<=threshold,'acceptance gap '..s.questID)
   end
  end
  if g.zone=='Zephras Isle' then
   island=island+1
   for _,s in ipairs(g.steps) do assert(not s.levelRecovery,'optional island exit must not force a level grind') end
  else
   mainland=mainland+1
   local final=g.steps[#g.steps]
   assert(final.levelRecovery and final.targetLevel==g.maxLevel)
   level=g.maxLevel-1;F.Guide=g;F.db.guideID=g.id;F.db.step=#g.steps
   F.db.skipped={};F.db.confirmedSteps={};E.manualHold=nil
   assert(not E:Done(final))
   E:AdvanceSafe();assert(F.Guide==g,'under-level handoff')
   assert(F.UI:TaskText(final):find('700 XP to next level (live)',1,true))
   level=g.maxLevel;assert(E:Done(final))
   local nextID=g.nextGuideID
   E:AdvanceSafe();assert(F.Guide.id==nextID,'level handoff')
  end
 end
end
assert(count==12 and mainland==9 and island==3)
local west=L.guides['alliance-westfall-10-15']
local guarded=false
for _,s in ipairs(west.steps) do
 if s.levelRecovery and s.targetLevel>=12 then guarded=true end
 if s.questID==9 and s.type=='objective' then assert(guarded,'Watchers need the explicit level-12 combat gate') end
end
''')
print('PASS: 147 quest records, optional/class XP exclusion, objective semantics, nine live mainland handoffs and three optional island exits')
