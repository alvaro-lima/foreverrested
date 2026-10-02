"""Partial reset preserves earlier progress and holds the selected restart point."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

lua = LuaRuntime(unpack_returned_tuples=True)
root = Path(__file__).resolve().parents[1]
lua.execute(r'''
F = {db={completed={},bindings={},skipped={}}, QuestLog={byID={[501]={}}},
 UI={frame={},Refresh=function() end}, Tracker={}}
function F.Number(n) return type(n)=="number" and n==n and n>-math.huge and n<math.huge end
function F.Print() end
function F.Call(fn, ...) if fn then return fn(...) end end
function F.QuestLog:TurnedIn() return false end
function F.Tracker:ShowCurrentAtTop()
 self.offset=F.db.step-1; self.rows={{stepIndex=F.db.step}}
end
function F.Refresh() F.GuideEngine:AdvanceSafe() end
function CreateFrame() return {RegisterEvent=function() end, SetScript=function() end} end
SlashCmdList={}
''')
for name in ("GuideEngine.lua", "Events.lua"):
    lua.execute("local F=...\n" + (root / name).read_text(encoding="utf-8").replace("local _, F = ...", "").replace("local addon, F = ...", "local addon='ForeverRested'"), lua.globals().F)
lua.execute(r'''
F.Guide = {title="Reset test", quests={}, steps={
 {id="before", type="note", text="Before", confirmOnNext=true},
 {id="restart", type="pickup", questID=501, text="Accept Legacy Quest"},
 {id="later", type="note", text="Later", confirmOnNext=true},
 {id="last", type="note", text="Last"},
}}
F.db.step=4; F.db.skipped={[1]=true,[2]=true,[3]=true,[4]=true}
F.db.confirmedSteps={before=true,later=true}
F.db.bindings={kept=501}; F.db.completed[999]=true
F.GuideEngine.selectedStep=2
F.GuideEngine:ResetFrom()
assert(F.db.step==2 and F.GuideEngine.manualHold)
assert(F.db.skipped[1] and not F.db.skipped[2] and not F.db.skipped[3] and not F.db.skipped[4])
assert(F.db.confirmedSteps.before and not F.db.confirmedSteps.later)
assert(F.db.bindings.kept==501 and F.db.completed[999])
assert(F.Tracker.offset==1 and F.Tracker.rows[1].stepIndex==2)
F.Refresh(); assert(F.db.step==2, "live completed pickup must not snap past restart point")
assert(F.GuideEngine:StepState(2)=="complete", "live quest state is retained")
F.GuideEngine:Move(1,true)
assert(not F.GuideEngine.manualHold and F.db.step==3)
SlashCmdList.FOREVERRESTED("reset 3")
assert(F.db.step==3 and F.GuideEngine.manualHold)
F.GuideEngine:Move(1)
assert(not F.GuideEngine.manualHold and F.db.confirmedSteps.later)
assert(F.db.step==4)
SlashCmdList.FOREVERRESTED("reset 0")
SlashCmdList.FOREVERRESTED("reset nope")
SlashCmdList.FOREVERRESTED("reset 2.5")
assert(F.db.step==4 and F.db.skipped[1], "invalid reset must preserve progress")
F.GuideEngine:ResetFrom(4)
F.GuideEngine:ResumeAuto()
assert(not F.GuideEngine.manualHold and F.db.step==4)
-- Moving the From boundary changes active skips without losing their history.
F.Guide={title="Twenty steps",quests={},steps={}}
for index=1,20 do F.Guide.steps[index]={id="step"..index,type="note",text="Step "..index} end
F.db.skipped={[15]=true,[18]=true}; F.db.skipHistory={}; F.db.confirmedSteps={}
F.db.manualSkippedSteps={step15=true,step18=true}
F.GuideEngine:ResetFrom(1)
assert(not F.db.skipped[15] and not F.db.skipped[18])
assert(F.GuideEngine:StepState(15)=="waiting" and F.GuideEngine:StepState(18)=="waiting")
assert(F.db.skipHistory.step15 and F.db.skipHistory.step18)
F.GuideEngine:ResetFrom(20)
assert(F.GuideEngine:StepState(15)=="skipped" and F.GuideEngine:StepState(18)=="skipped")
F.GuideEngine:ResetFrom(18)
assert(F.db.skipped[15] and not F.db.skipped[18], "boundary itself is available again")
F.GuideEngine:ResetFrom(1)
F.GuideEngine.catchUpPending=true
F.GuideEngine:CatchUpOnLoad()
assert(not F.GuideEngine.catchUpPending and not F.db.skipped[15])
''')
lua.execute("local F=...\n" + (root / "GuideLibrary.lua").read_text(encoding="utf-8").replace("local _, F = ...", ""), lua.globals().F)
lua.execute(r'''
F.db.guideID="test"; F.db.guides={}; F.Guide.revision=1
F.GuideLibrary.guides={test=F.Guide,other={title="Other",revision=1,steps={{id="other",type="note"}}}}
F.GuideLibrary:SaveCurrent()
local saved=F.db.guides.test
F.GuideLibrary:ApplyState(F.GuideLibrary.guides.other,{})
assert(not F.db.restartStepID and not next(F.db.skipHistory), "skip history belongs to each guide")
F.GuideLibrary:ApplyState(F.Guide,saved)
assert(F.db.restartStepID=="step1" and F.db.skipHistory.step15 and not F.db.skipped[15])
F.GuideEngine:CatchUpOnLoad()
F.GuideEngine:ResetFrom(20)
assert(F.db.skipped[15] and F.db.skipped[18], "restored guide remembers suspended skips")
F.GuideEngine:Reset()
assert(not next(F.db.skipHistory) and not F.db.restartStepID)
F.GuideEngine:ResetFrom(20)
assert(not F.db.skipped[15] and not F.db.skipped[18], "full reset clears skip history")
''')
print("PASS: reversible From boundary, guide persistence, live quest state, resume and invalid step handling.")
