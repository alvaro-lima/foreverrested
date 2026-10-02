"""Known class unlocks stay visible across regional guides and saved states."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
profiles = [("WARRIOR", "Human"), ("PALADIN", "Dwarf"), ("HUNTER", "NightElf"),
            ("DRUID", "NightElf"), ("WARLOCK", "Gnome"), ("ROGUE", "Human"),
            ("PRIEST", "Dwarf"), ("SHAMAN", "Dwarf"), ("MAGE", "Human")]
for class_token, race in profiles:
    namespace = {"__file__": str(base)}
    exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
    lua = namespace["lua"]
    lua.globals().profileClass, lua.globals().profileRace = class_token, race
    lua.execute(r'''
function UnitClass() return profileClass,profileClass end
function UnitRace() return profileRace,profileRace end
function UnitLevel() return 20 end
F.LoadDatabase(); F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create()
live={}; C_QuestLog.IsQuestFlaggedCompleted=function() return false end
for _,id in ipairs(F.GuideLibrary.order) do
 if F.GuideLibrary.guides[id].status~='test' then
  F.db.completed={}; F.GuideLibrary:Select(id)
  local expected,total={},0
  for _,step in ipairs(F.Guide.steps) do
   if step.unlockChain then expected[step.id]=step.questID; total=total+1 end
  end
  if profileClass~='MAGE' then assert(total>0,'known class unlocks must appear') end
  local function verify()
   local seen={}
   for index,step in ipairs(F.Guide.steps) do
    assert(not seen[step.id],'duplicate stable ID'); seen[step.id]=true
    if expected[step.id] then assert(F.UI:StepPriority(step,index)=='Critical') end
   end
   for key in pairs(expected) do assert(seen[key],'unlock vanished: '..key) end
  end
  verify()
  for _,questID in pairs(expected) do F.db.completed[questID]=true end
  F.GuideLibrary:SaveCurrent(); F.GuideLibrary:Select(id); verify()
  F.db.guides[id].restartStepID=F.Guide.steps[#F.Guide.steps].id
  F.GuideLibrary:Select(id); verify()
  for index,step in ipairs(F.Guide.steps) do
   if expected[step.id] then
    F.db.skipped[index]=true
    F.db.manualSkippedSteps[step.id]=true
    assert(F.UI:StepPriority(step,index)=='Critical','skip retains key marker')
   end
  end
 end
end
''')
print("PASS: nine class profiles across installed guides retain unlock rows and key markers after completion, From and skips.")
