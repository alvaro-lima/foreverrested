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
''')
print("PASS: partial reset, live quest state, restart hold, resume and invalid step handling.")
