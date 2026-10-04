"""Auto and a fresh start stop at unfinished live work despite stale catch-up skips."""
from pathlib import Path
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2);ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local E=F.GuideEngine
F.Guide={id='recheck',steps={
 {id='pickup',type='pickup',questID=1007},
 {id='collect',type='objective',questID=1007},
 {id='deliver',type='turnin',questID=1007},
 {id='ruuzel',type='pickup',questID=1009},
 {id='exit',type='note'}
}}
F.QuestLog.byID={[1007]={complete=false}}
F.QuestLog.TurnedIn=function() return false end
F.Refresh=function() E:AdvanceSafe() end
F.Tracker.ShowCurrentAtTop=function() end
F.db.skipped={[2]=true,[3]=true};F.db.step=4
F.db.manualSkippedSteps={};E.catchUpPending=true
E:ResumeAuto()
assert(F.db.step==2,'accepted statuette stops at collection')
F.QuestLog.byID[1007].complete=true
E:ResumeAuto()
assert(F.db.step==3,'complete objective still requires statuette hand-in')
E:Move(1,true)
assert(F.db.step==4,'explicit skip proceeds to next unfinished action')
E:ResetFrom(1)
assert(F.db.step==3,'fresh start clears explicit skips and checks completion')
assert(not F.db.manualSkippedSteps.deliver)
E:Move(1,true)
F.QuestLog.byID[1009]={complete=false}
E:AdvanceSafe()
assert(F.db.step==5,'accepted next quest pickup is checked automatically')
assert(not E.selectedStep,'Skip follows the unfinished row rather than a completed pickup')
''')
print('PASS: Auto rechecks collection, turn-in, explicit skips and fresh starts')
