"""Step tooltips resolve action-specific zones, grouped actions and fallbacks."""
from pathlib import Path

base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace['lua'].execute(r'''
F.LoadDatabase();F.UI:Create()
assert(F.Tooltips.delay==2)
F.Guide={zone='Westfall',quests={},steps={}}
local records={
 [501]={locations={{role='start',zone='Loch Modan',x=.2,y=.3},
                   {role='end',zone='Wetlands',x=.4,y=.5},
                   {role='requirement',zone='Dun Morogh',x=.6,y=.7}}},
 [502]={locations={{role='start',zone='Elwynn Forest'}}},
}
for _,record in pairs(records) do record.requirements={};record.rewards={} end
F.GuideEngine.Metadata=function(_,id) return records[id] end
F.Travel.QuestArea=function() end
assert(F.UI:StepLocation({type='pickup',questID=501})=='Location: Loch Modan (20.0, 30.0)')
assert(F.UI:StepLocation({type='turnin',questID=501})=='Location: Wetlands (40.0, 50.0)')
assert(F.UI:StepLocation({type='objective',questID=501})=='Location: Dun Morogh (60.0, 70.0)')
assert(F.UI:StepLocation({type='pickup',questID=502})=='Location: Elwynn Forest')
assert(F.UI:StepLocation({type='travel',travelTo='Darkshore',travelFrom='Wetlands'})=='Location: Darkshore')
assert(F.UI:StepLocation({type='note'})=='Location: Westfall')
local grouped=F.UI:StepLocation({tasks={{type='pickup',questID=501},{type='pickup',questID=502}}})
assert(grouped:find('Loch Modan',1,true) and grouped:find('Elwynn Forest',1,true))
F.Guide.steps={{type='pickup',questID=501,text='Accept quest'}}
F.db.step=1;F.db.skipped={};F.Tracker:Refresh()
local row=F.Tracker.rows[1];row.stepIndex=1;row.zone=false;row:Show()
local lines={}
GameTooltip.AddLine=function(_,line) lines[#lines+1]=line end
row.scripts.OnEnter(row)
assert(#lines>0 and not F.Tooltips.pending,'quest row tooltip appears immediately')
assert(table.concat(lines,'\n'):find('Location: Loch Modan (20.0, 30.0)',1,true))
''')
print('PASS: immediate quest tooltips, two-second control delay and action-specific locations')
