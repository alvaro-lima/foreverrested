"""Single step list, explicit completion/skipping and persistent manual scrolling."""
from pathlib import Path
import runpy
lua=runpy.run_path(str(Path(__file__).with_name("validate.py")))["lua"]
lua.execute(r'''
assert(rawget(F.UI,"currentPanel")==nil and rawget(F.UI,"nextPanel")==nil and rawget(F.UI,"sidePanel")==nil)
assert(rawget(F.UI,"stepsButton")==nil and rawget(F.UI,"questsButton")==nil)
F.Guide={title="Step list test",quests={},steps={
 {id="one",type="pickup",questID=501,text="Accept Legacy Quest"},
 {id="two",type="note",text="Travel to town"},
 {id="three",type="note",text="Optional detour"},
 {id="four",type="objective",questID=501,text="Complete Legacy Quest"},
 {id="five",type="note",text="Finish"},
}}
F.db.step=2;F.db.skipped={[3]=true};F.UI:Refresh()
F.Tracker.offset=0;F.Tracker:Refresh()
local rows=F.Tracker.rows
assert(rows[1].text.text:find("1",1,true) and rows[1].status.texturePath:find("StatusDone.tga",1,true))
assert(rows[2].text.text:find("2",1,true) and rows[2].statusLabel=="Current")
assert(rows[2].body.text:find("Travel to town",1,true))
assert(rows[2].stepGlow:IsShown() and not rows[1].stepGlow:IsShown())
assert(rows[3].statusLabel=="Skipped" and rows[3].status.texturePath:find("StatusSkipped.tga",1,true))
assert(rows[4].text.text:find("4",1,true) and rows[4].statusLabel=="Next")
F.Tracker.offset=4;F.Tracker:Refresh();assert(rows[1].stepIndex==5)
F.UI:Refresh();assert(F.Tracker.offset==4,"live refresh must not undo manual scrolling")
rows[1].scripts.OnClick(rows[1]);assert(F.db.step==5 and F.GuideEngine.manualHold)
F.UI:SetFontSize(20);assert(rows[1].text.fontSize==20 and rows[1]:IsShown())
''')
print("PASS: one step window, X of Y numbering, completed and skipped icons, next relevance, review and scrolling.")
