"""Alliance 20-30 route structure, dependencies, completion and Water Totem."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
lua = namespace["lua"]
lua.execute(r'''
local level,class,race=20,'MAGE','Human'
function UnitLevel() return level end
function UnitClass() return class,class end
function UnitRace() return race,race end
F.LoadDatabase(); F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create()
local L,E=F.GuideLibrary,F.GuideEngine
local ids={'alliance-duskwood-20-30','alliance-wetlands-20-30','alliance-ashenvale-20-30'}
assert(#L:GuidesForBracket(3)==11)
live={}; C_QuestLog.IsQuestFlaggedCompleted=function() return false end
for _,id in ipairs(ids) do
 L:Select(id)
 local guide=F.Guide
 assert(guide.minLevel==20 and guide.maxLevel==30 and #guide.steps>60)
 local seen,turnins={},{}
 for index,step in ipairs(guide.steps) do
  assert(not seen[step.id]);seen[step.id]=true
  for _,task in ipairs(step.tasks or {step}) do
   if task.questID then
    local data=E:Metadata(task.questID)
    assert(data and data.side~=2,'required Alliance quest must have sourced facts')
    assert(not task.slot,'no live-log fixture bindings')
    local record=F.QuestPolicy:Record(task.questID)
    if task.type=='pickup' and not task.optional and not step.recovery and not step.unlockChain then
     for _,prior in ipairs(record.prerequisites or {}) do
      assert(turnins[prior] or F.QuestPolicy:Satisfied(prior),'missing/late prerequisite '..prior..' for '..task.questID)
     end
     if record.prerequisitesAny and #record.prerequisitesAny>0 then
      local available=false
      for _,prior in ipairs(record.prerequisitesAny) do available=available or turnins[prior]~=nil or F.QuestPolicy:Satisfied(prior) end
      assert(available,'missing alternative prerequisite for '..task.questID)
     end
    end
    if task.type=='turnin' then turnins[task.questID]=index end
   end
  end
  if step.confirmOnNext then
   for _,task in ipairs(step.alongside or {}) do assert(task.optional,'optional branches must not block') end
  end
 end
 -- Simulate completed required quests and verify only manual notes remain.
 level=30; F.db.completed={}; F.db.skipped={}; F.db.confirmedSteps={}; F.db.step=1
 for _,step in ipairs(guide.steps) do
  for _,task in ipairs(step.tasks or {step}) do if task.questID then F.db.completed[task.questID]=true end end
 end
 E:ResumeAuto()
 local advances=0
 while F.db.step<#guide.steps do
  assert(guide.steps[F.db.step].confirmOnNext,'unexpected completed-route blocker')
  E:Move(1); E:ResumeAuto(); advances=advances+1; assert(advances<100)
 end
 assert(guide.steps[F.db.step].confirmOnNext)
 level=20
end
-- Shaman starts at the actual first unfinished Water stage, across regions.
class='SHAMAN';race='Dwarf';level=20
F.db.completed={[94375]=true,[94468]=true}
L:Select(ids[2])
local water={94495,94497,94499,94500,94501,94502,94503,94505}
local seen={}
for index,step in ipairs(F.Guide.steps) do
 for _,id in ipairs(water) do
  if step.questID==id then
   local key=id..':'..step.type; assert(not seen[key]); seen[key]=true
   assert(F.UI:StepPriority(step,index)=='Critical' and step.note)
  end
 end
end
local count=0;for _ in pairs(seen) do count=count+1 end;assert(count==24)
for _,id in ipairs({94495,94497}) do F.db.completed[id]=true end
F.db.confirmedSteps['entry-class']=true
E:ResumeAuto()
assert(F.Guide.steps[F.db.step].questID==94499,'resume first unfinished water stage')
assert(F.Navigation:ReferencePoint(E:Metadata(94503),'end')==nil,'no inherited Horde elemental coordinates')
F.db.completed[94505]=true
L:Select(ids[1]);L:Select(ids[2])
assert(F.UI:TaskPriority({questID=94505})=='Critical','completed water reward retains key marker')
race='Gnome';assert(not F.QuestPolicy:UnlockApplies(F.QuestPolicy.foreverUnlocks['forever-shaman-water']))
class='MAGE';race='NightElf';level=20
assert(L:Recommended()=='alliance-kalimdor-20-24')
race='Human';assert(L:Recommended()=='alliance-eastern-20-22')
race='Dwarf';assert(L:Recommended()=='alliance-eastern-20-22')
-- Reaching 20 inserts the new class detour without needing a guide switch.
class='SHAMAN'; level=19
local fresh={id='level-up-fixture',title='Level-up route',faction='Alliance',minLevel=20,maxLevel=30,
 revision=1,quests={},steps={{id='start',type='note',confirmOnNext=true},{id='finish',type='note',confirmOnNext=true}}}
L:Register(fresh); L:Select(fresh.id)
for _,step in ipairs(fresh.steps) do assert(step.questID~=94495) end
local viewedID=fresh.steps[#fresh.steps].id
E.selectedStep=#fresh.steps
level=20; E.unlockRefreshPending=true; F.Refresh()
local found=false
for _,step in ipairs(fresh.steps) do if step.questID==94495 then found=true end end
assert(found,'level-up adds Water Totem without reload')
assert(fresh.steps[E.selectedStep].id==viewedID,'level-up preserves viewed step by ID')
''')
print("PASS: three 20-30 guides, sourced identities, ordered prerequisites, optional branches, progression, recommendations and persistent Water Totem actions.")
