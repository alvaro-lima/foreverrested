"""Row hover supports optional markers and unknown future marker kinds."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace['lua'].execute(r'''
F.LoadDatabase();F.UI:Create()
F.Guide={title='Tooltip test',quests={},steps={{id='optional-travel',type='travel',text='Travel to town',optional=true}}}
F.db.step=1;F.db.skipped={};F.Tracker:Refresh()
local row=F.Tracker.rows[1]
row.stepIndex=1;row.zone=false;row:Show()
local lines={}
GameTooltip.AddLine=function(_,line) lines[#lines+1]=line end
local function hover()
 F.Tooltips:Cancel();row.scripts.OnEnter(row)
 assert(not F.Tooltips.pending,'quest tooltip appears immediately')
end
hover()
assert(table.concat(lines,'\n'):find('Optional travel:',1,true))
F.Guide.steps[1].type='note';lines={};hover()
assert(table.concat(lines,'\n'):find('Optional quest:',1,true))
F.UI.StepMarkers=function() return {{kind='FutureMarker'}} end
lines={};hover()
assert(table.concat(lines,'\n'):find('FutureMarker',1,true))
''')
print('PASS: optional travel, optional quest and unknown marker row tooltips')
