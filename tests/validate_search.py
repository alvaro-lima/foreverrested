"""Exercise guide search with the shared Lua 5.1 UI mock setup."""
from pathlib import Path

base = Path(__file__).with_name("validate.py")
source = base.read_text()
# Reuse setup without running the legacy behavior assertions below it.
setup = source.split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace["lua"].execute(r'''
F.LoadDatabase(); F.UI:Create()
F.Guide={title="Search test",quests={},questData={
 [901]={title="Hidden Quest",locations={{name="Guide NPC"}}}
},steps={
 {id="one",type="note",text="Travel to town",note="Find the inn"},
 {id="two",type="pickup",questID=901,text="Accept quest"},
 {id="three",type="note",text="Optional detour",alongside={{type="note",text="Gather flowers"}}},
}}
F.db.step=1; F.db.skipped={}; F.UI.lastGuide=F.Guide; F.UI.lastStep=1; F.Tracker.offset=0
F.Tracker:SetSearch("  HIDDEN quest  ")
assert(F.Tracker.rows[1].stepIndex==2)
assert(not F.Tracker.rows[2]:IsShown())
assert(F.UI.searchCount.text=="1 / 3 steps match")
F.Tracker:SetSearch("guide npc"); assert(F.Tracker.rows[1].stepIndex==2)
F.Tracker:SetSearch("flowers"); assert(F.Tracker.rows[1].stepIndex==3)
F.Tracker:SetSearch("inn"); assert(F.Tracker.rows[1].stepIndex==1)
F.Tracker:SetSearch("2"); assert(F.Tracker.rows[1].stepIndex==2)
F.Tracker.rows[1].scripts.OnClick(F.Tracker.rows[1])
assert(F.GuideEngine.selectedStep==2 and F.db.step==1)
F.Tracker:SetSearch("town flowers")
assert(not F.Tracker.rows[1]:IsShown() and F.UI.searchCount.text=="No matching steps.")
F.Tracker:SetSearch("["); assert(not F.Tracker.rows[1]:IsShown())
F.Tracker:SetSearch(""); assert(F.Tracker.searchQuery==nil and F.Tracker.rows[1].stepIndex==1)
F.Tracker:SetSearch("flowers"); F.Tracker:ShowCurrentAtTop()
assert(F.Tracker.searchQuery==nil and F.Tracker.rows[1].stepIndex==1)
local oldMarkers=F.UI.StepMarkers
F.UI.StepMarkers=function(_,step,index)
 return index==2 and {{kind="Critical"},{kind="Gear",alongside=true}} or {}
end
local function matches(query,index,state,label)
 F.Tracker.searchQuery=query
 return F.Tracker:MatchesSearch(F.Guide.steps[index],index,state,label)
end
assert(matches("critical",2,"waiting","Not started"))
assert(matches("key/critical quests",2,"waiting","Not started"))
assert(matches("gear to do",2,"waiting","Not started"))
assert(not matches("gear to do",2,"skipped","Skipped"))
assert(not matches("gear to do",2,"complete","Done"))
assert(matches("skipped",2,"skipped","Skipped"))
assert(matches("in progress",2,"ongoing","In progress"))
assert(matches("ready to turn in",2,"ready","In progress"))
assert(matches("completed",2,"complete","Done"))
assert(matches("next",2,"waiting","Next"))
assert(not matches("critical",1,"waiting","Current"))
F.UI.StepMarkers=oldMarkers; F.Tracker.searchQuery=nil
''')
print("PASS: search content, priorities, status combinations, numbers, empty results and browsing.")
