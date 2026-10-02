"""Critical actions render as separate warning-marked rows, with manual skips."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
namespace = {"__file__": str(root / "tests/validate.py")}
setup = (root / "tests/validate.py").read_text().split("lua.execute(r'''\nF.LoadDatabase()", 1)[0]
exec(setup, namespace)
namespace["lua"].execute(r'''
function UnitClass() return 'Shaman','SHAMAN' end
function UnitRace() return 'Dwarf','Dwarf' end
function UnitLevel() return 15 end
C_QuestLog={GetNumQuestLogEntries=function() return 0 end,
 IsQuestFlaggedCompleted=function(id) return id==94375 end}
F.LoadDatabase()
F.Tracker:Create(UIParent)
F.Tracker.frame:SetHeight(5000)
F.GuideLibrary:Select('alliance-loch-modan-10-20')
F.Tracker:Refresh()
local E=F.GuideEngine
local step=F.Guide.steps[F.db.step]
assert(step.type=='pickup' and step.questID==94449 and step.critical)
for _,row in ipairs(F.Tracker.rows) do
 if row.stepIndex then
  local s=F.Guide.steps[row.stepIndex]
  local text=row.body.text
  assert(not text:find('Kept during catch-up',1,true))
  if s.recovery then
   assert(text:find('UI-Dialog-Icon-Alert:',1,true))
   assert(not text:find('Review Forever class unlocks',1,true))
   assert(not text:find('Required during catch-up',1,true))
   assert(not s.tasks,'each recovered action must have its own numbered row')
  end
 end
end
local id=step.id
E:Move(1,true)
F.GuideLibrary:SaveCurrent(); F.GuideLibrary:Select('alliance-loch-modan-10-20')
local found
for i,s in ipairs(F.Guide.steps) do if s.id==id then found=i end end
assert(found and E:StepState(found)=='skipped' and F.db.manualSkippedSteps[id])
-- Completion still wins over a manual skip, and reset clears the bypass.
F.db.completed[94449]=true
assert(E:StepState(found)=='complete')
F.db.completed[94449]=nil
E:ResetFrom(found)
assert(not F.db.manualSkippedSteps[id] and not F.db.skipped[found])
-- Authored quest rows must show the marker without recovery annotations.
F.db.completed[94373]=nil
F.Guide.steps={{id='authored-earth',type='pickup',questID=94373}}
F.db.step=1; E.selectedStep=nil; E.catchUpReasons={}; F.db.skipped={}
F.Tracker:Refresh()
assert(F.Tracker.rows[1].body.text:find('UI-Dialog-Icon-Alert:',1,true))
assert(F.QuestPolicy:Critical(F.Guide.steps[1]))
''')
print("PASS: individual critical rows, warning icon, compact text, persistent manual skip and reset")
