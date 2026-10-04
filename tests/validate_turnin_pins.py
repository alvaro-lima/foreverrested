"""Completed objectives do not make pending delivery pins in progress."""
from pathlib import Path
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
namespace={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],namespace)
namespace['lua'].execute(r'''
F.LoadDatabase()
local gather={type='objective',questID=101}
local deliver={type='turnin',questID=101}
F.Guide={steps={gather,deliver}};F.db.step=2;F.db.skipped={};F.db.completed={}
C_QuestLog.IsQuestFlaggedCompleted=function() return false end
F.QuestLog.byID[101]={complete=true}
assert(F.GuideEngine:StepState(1)=='complete','gathering complete')
assert(F.GuideEngine:StepState(2)~='complete','delivery pending')
local pin=F.StepPins:Create(UIParent)
pin.entry={index=2,task=deliver};F.StepPins:Style(pin)
assert(pin.icon.texturePath:find('MapStepBadge-thick.tga',1,true),'current turnin destination is highlighted')
F.db.step=1;F.Navigation.waypointTask=nil;F.StepPins:Style(pin)
assert(pin.icon.texturePath:find('StatusNotStarted.tga',1,true),'upcoming pending turnin uses to-do pin')
F.db.completed[101]=true;F.StepPins:Style(pin)
assert(pin.icon.texturePath:find('StatusDone.tga',1,true),'delivered quest uses done pin')
''')
print('PASS: independent gathering and delivery status')
