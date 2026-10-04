"""Starter source integrity, required XP separation, acceptance levels and live handoffs."""
from pathlib import Path
import json
import sys
sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
base = root / 'tests/validate.py'
setup = base.read_text().split("lua.execute(r'''", 2)
ns = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], ns)
audit = json.loads((root / 'Data/STARTER_AUDIT.json').read_text(encoding='utf-8'))
reference = json.loads((root / 'Data/alliance-reference.json').read_text(encoding='utf-8'))
assert len(audit['guides']) == 10 and len(audit['quests']) == 142
for identity, quest in audit['quests'].items():
    assert quest['objectives'] == reference['quests'][identity]['objectives']
    assert quest['sha256'] == reference['checksums'][identity]
assert audit['quests']['179']['objectives'][0]['count'] == 8
assert audit['quests']['170']['objectives'][0]['count'] == 6
assert audit['quests']['92849']['objectives'][0]['action'] == 'interact'
sys.path.insert(0, str(root / 'tools'))
from audit_01_10 import objectives, normal_kill_xp
from build_starter_combat import chapter_estimates
fake = '''<div>Comment: 99 skins</div><h1 class="heading">Quest</h1>
<table><tr data-icon-list-quantity="6"><td><a href="/forever/item=1/skin">Skin</a></td></tr>
<tr data-icon-list-quantity="1"><td><a href="/forever/npc=2/friend">Speak to Friend</a></td></tr></table>
<h2>Description</h2><tr data-icon-list-quantity="99"><td><a href="/forever/item=1/skin">Skin</a></td></tr>'''
assert [obj['count'] for obj in objectives(fake)] == [6, 1]
assert objectives(fake)[1]['action'] == 'interact'
provided = fake.split('<h2', 1)[0] + '''Provided item:
<table><tr data-icon-list-quantity="1"><td><a href="/forever/item=99/charm">Charm</a></td></tr></table><h2>Description</h2>'''
assert all(obj.get('id') != 99 for obj in objectives(provided)), 'Supplied items are not collected objectives'
assert audit['quests']['2561']['objectives'] == [{'kind': 'event', 'action': 'interact', 'count': 1, 'name': "Release Oben Rageclaw's spirit"}]
wolf_sources = [point['entityID'] for point in audit['quests']['179']['locations'] if point['role'] == 'sourcerequirement']
assert set(wolf_sources) == {704, 705}, 'Incidental trogg/boar/elite drops are not wolf-meat navigation targets'
assert normal_kill_xp(5, 5) == 70
assert normal_kill_xp(5, 3) == 42
assert normal_kill_xp(8, 2) == 0
combat = json.loads((root / 'Data/STARTER_COMBAT.json').read_text(encoding='utf-8'))
assert combat['quests']['315']['objectives'][0]['acquisition'] == 'object-or-mob'
assert combat['quests']['315']['objectives'][0]['objectSourceIDs'], 'Basket collection must not assume troll farming'
rough = chapter_estimates(audit, combat)
assert rough['optionalXPExcluded'] and len(rough['chapters']) == 10
budgets = json.loads((root / 'Data/STARTER_XP_BUDGET.json').read_text(encoding='utf-8'))
assert budgets['optionalXPExcluded'] and len(budgets['chapters']) == 10
for chapter in budgets['chapters']:
    assert not chapter['requiredPrerequisiteGaps']
    assert not set(chapter['requiredTurninIDs']) & set(chapter['excludedOptionalTurninIDs'])
    assert chapter['totalExpectedXP'] is None and chapter['missing']
ns['lua'].execute(r'''
F.LoadDatabase()
local L,E=F.GuideLibrary,F.GuideEngine
local currentLevel=1
function UnitLevel() return currentLevel end
function UnitXP() return 200 end
function UnitXPMax() return 900 end
local count=0
for _,identity in ipairs(L.order) do
 local g=L.guides[identity]
 if g.sourceGuideID and g.minLevel<10 then
  count=count+1
  local threshold=g.minLevel
  for _,s in ipairs(g.steps) do
   if s.levelRecovery then
    assert(s.zone and s.x and s.y and not s.questID and not s.alongside)
    threshold=math.max(threshold,s.targetLevel)
   elseif s.type=='pickup' and s.questID and not s.optional then
    assert(F.AllianceQuestData[s.questID].minLevel<=threshold,'acceptance gap '..s.questID)
   end
  end
  local final=g.steps[#g.steps]
  assert(final.levelRecovery and final.targetLevel==g.maxLevel,'live exit check')
  currentLevel=g.maxLevel-1
  F.Guide=g;F.db.guideID=g.id;F.db.step=#g.steps
  F.db.skipped={};F.db.confirmedSteps={};E.manualHold=nil
  assert(not E:Done(final))
  E:AdvanceSafe();assert(F.Guide==g,'under-level chapter must not hand off')
  local text=F.UI:TaskText(final)
  assert(text:find('700 XP to next level (live)',1,true))
  currentLevel=g.maxLevel
  assert(E:Done(final),'recovery uses actual level')
  local destination=g.nextGuideID
  E:AdvanceSafe();assert(F.Guide.id==destination,'at-level handoff')
 end
end
assert(count==10)
''')
print('PASS: all 142 sourced quests, objective semantics, acceptance guards, live XP and all ten chapter handoffs')
