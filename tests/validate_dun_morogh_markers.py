"""Browse actual Dun Morogh rows as a level-20 shaman, including collapsed detours."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for completed in (False, True):
    namespace = {'__file__': str(root / 'tests/validate.py')}
    setup = (root / 'tests/validate.py').read_text().split("lua.execute(r'''\nF.LoadDatabase()", 1)[0]
    exec(setup, namespace)
    lua = namespace['lua']
    lua.globals().totemsDone = completed
    lua.execute(r'''
function UnitClass() return 'Shaman','SHAMAN' end
function UnitRace() return 'Dwarf','Dwarf' end
function UnitLevel() return 20 end
C_QuestLog={GetNumQuestLogEntries=function() return 0 end,
 IsQuestFlaggedCompleted=function(id) return totemsDone and (id==94375 or id==94468) end}
F.LoadDatabase()
F.Tracker:Create(UIParent)
F.Tracker.frame:SetHeight(600)
F.GuideLibrary:Select('alliance-dun-morogh-01-10')
local count,seen={},{}
for index,step in ipairs(F.Guide.steps) do
 F.Tracker.offset=index-1
 F.Tracker:Refresh()
 for _,row in ipairs(F.Tracker.rows) do
  if row.stepIndex==index then
   seen[step.id]=true
   local text=row.body.text or ''
   if step.id=='vagash-gear-option' or step.id=='pilot-gear-option' then
    assert(not text:find('UI-StateIcon:',1,true),'unknown gear data must not advertise an upgrade')
   elseif step.id=='mug-option' then
    assert(not text:find('PriorityOptional.tga:',1,true),'generic optional markers removed')
   elseif step.id=='coldridge-exit-pickup' then
    assert(not text:find('PriorityOptional.tga:',1,true),'generic side quest markers removed')
   end
   if step.recovery and step.questID then
    assert(text:find('PriorityCritical.tga:',1,true),'missing critical marker')
    count[step.questID]=true
   end
  end
 end
end
for _,id in ipairs({'vagash-gear-option','pilot-gear-option','mug-option','coldridge-exit-pickup'}) do
 assert(seen[id],'row not reached while browsing: '..id)
end
if not totemsDone then
 for _,id in ipairs({94373,94374,94375,94449,94465,94466,94467,94468}) do
  assert(count[id],'critical chain missing while browsing: '..id)
 end
end
''')
print('PASS: level-20 Dun Morogh browsing, critical chains, collapsed side quests and optional gear notes')
