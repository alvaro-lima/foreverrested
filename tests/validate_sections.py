"""Playable section transitions, exit checkpoints and estimate uncertainty guards."""
from pathlib import Path
import copy
import importlib.util
import json
import runpy
import sys

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(root / "tests/validate_guides.py"))["lua"]
lua.execute(r'''
local L,E=F.GuideLibrary,F.GuideEngine
local ids={'alliance-westfall-10-20','alliance-loch-modan-10-20','alliance-darkshore-10-20','alliance-zephras-10-14'}
assert(#L:GuidesForBracket(2)==4)
function UnitLevel() return 20 end
function UnitClass() return 'Mage','MAGE' end
function UnitRace() return 'Skyborne','Skyborne' end
for _,id in ipairs(ids) do
 local g=L.guides[id];assert(g and g.minLevel==10 and g.maxLevel==20 and #g.steps>40)
 local seen={}
 for _,step in ipairs(g.steps) do
  assert(not seen[step.id]);seen[step.id]=true
  for _,tasks in ipairs({step.tasks or {},step.alongside or {}}) do
   for _,task in ipairs(tasks) do
    local q=F.AllianceQuestData[task.questID]
    assert(q and q.side~=2,'required and alongside entries must use sourced Alliance-compatible IDs')
    assert(not task.slot)
   end
  end
 end
 L:Select(id);F.db.completed={};F.db.confirmedSteps={};live={};objectives={}
 for _,step in ipairs(g.steps) do
  for _,task in ipairs(step.tasks or {}) do F.db.completed[task.questID]=true end
 end
 E:ResumeAuto();local stops=0
 while F.db.step<#g.steps do
  assert(g.steps[F.db.step].confirmOnNext,'finished quests and level checkpoints must reconcile')
  E:Move(1);stops=stops+1;assert(stops<25)
 end
 assert(g.steps[F.db.step].confirmOnNext)
end
-- Island reviews remain explicit choices even after quests are finished.
L:Select(ids[4]);F.db.confirmedSteps={};E:ResumeAuto()
assert(F.Guide.steps[F.db.step].id=='entry-class')
E:Move(1);assert(F.Guide.steps[F.db.step].id=='exit-at10')
E:Move(1);assert(F.Guide.steps[F.db.step].id=='exit-at12')
L:SaveCurrent();L:Select(ids[1]);L:Select(ids[4]);E:ResumeAuto()
assert(F.Guide.steps[F.db.step].id=='exit-at12','manual exit confirmations persist per guide')
-- Current source summaries intentionally have no fabricated fallback coordinates.
for _,reference in pairs(F.AllianceQuestData) do
 if reference.confidence=='sourced-summary' then assert(#reference.locations==0) end
end
local savedLocations=F.AllianceQuestData[92640].locations
F.AllianceQuestData[92640].locations={}
assert(L:Recommended()=='alliance-zephras-10-14','level-10+ island newcomers should see the extension')
-- Native quest waypoints still work for a summary-only objective.
local index
for i,s in ipairs(F.Guide.steps) do if s.id=='desperate-times-objectives' then index=i end end
F.db.step=index;F.db.completed[92640]=nil
live={{questID=92640,title='Desperate Times',isComplete=false}}
objectives[92640]={{text='Live beta objective: 0/5',type='monster',numRequired=5,numFulfilled=0,finished=false}}
C_QuestLog.GetNextWaypoint=function(id) if id==92640 then return 99999,.4,.5 end end
F.Refresh();local map,x,y=F.Navigation:Waypoint();assert(map==99999 and x==.4 and y==.5)
objectives[92640][1].numRequired=7;F.Refresh();assert(F.db.step==index)
objectives[92640][1].finished=true;F.Refresh();assert(F.Guide.steps[F.db.step].id=='desperate-times-return')
F.AllianceQuestData[92640].locations=savedLocations
''')
spec = importlib.util.spec_from_file_location("comparison", root / "tools/compare_zephras.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
data = json.loads((root / "Data/zephras-comparison-input.json").read_text())
reference = json.loads((root / "Data/alliance-reference.json").read_text())["quests"]
result = module.compare(data, reference)
for policy in result["policies"]:
    expected = policy["scenarios"]["expected"]
    assert abs(expected["minutes"] - (expected["islandMinutes"] + expected["travelMinutes"] + expected["mainlandMinutes"])) < 1e-8
    assert expected["travelMinutes"] == data["travelMinutes"]["expected"]
assert result["policies"][1]["scenarios"]["expected"]["minutes"] < result["policies"][0]["scenarios"]["expected"]["minutes"]
assert result["policies"][0]["scenarios"]["slow"]["minutes"] < result["policies"][1]["scenarios"]["slow"]["minutes"]
bad = copy.deepcopy(data);bad["clusters"][1]["questIDs"].append(bad["clusters"][0]["questIDs"][0])
try:
    module.compare(bad, reference)
    raise AssertionError("duplicate rewards accepted")
except ValueError:
    pass
missing = copy.deepcopy(reference);missing["92840"]["listedXP"] = None
try:
    module.compare(data, missing)
    raise AssertionError("unknown XP ranked")
except ValueError:
    pass
print("PASS: three mainland sections, island exit choices, native waypoints for missing locations, tuned live counts, saved checkpoints and scenario comparisons.")
