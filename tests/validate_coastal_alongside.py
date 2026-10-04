"""Later-chapter ooze collection stays out of the current coastal guide."""
from pathlib import Path
base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace['lua'].execute(r'''
F.LoadDatabase();F.UI:Create()
F.Guide=F.GuideLibrary.guides['alliance-eastern-20-22']
F.db.skipped={};F.db.manualSkippedSteps={};F.db.completed={}
C_QuestLog.IsQuestFlaggedCompleted=function() return false end
local q={id=470,title='Digging Through the Ooze',objectives={{text="Sida's Bag: 0/1",finished=false}}}
F.QuestLog.list={q};F.QuestLog.byID={[470]=q}
local index
for i,step in ipairs(F.Guide.steps) do
 if step.legacyGroupID=='coastal-first-objectives' then
  index=i;break
 end
end
F.db.step=index
assert(#F.ObjectiveQueue:Build()==0,'accepted later-chapter quest must stay out of this guide')
for _,action in ipairs(F.GuideEngine:Tasks(F.Guide.steps[index],true)) do
 assert(action.questID~=470,'later collection must not be attached to coastal hunting')
end
F.Tracker:Refresh()
for _,row in ipairs(F.Tracker.rows) do
 assert(not (row.text and row.text:find('Alongside this step:',1,true)))
end
F.Guide=F.GuideLibrary.guides['alliance-eastern-26-27']
local entries=F.ObjectiveQueue:Build()
assert(#entries==1 and entries[1].questID==470,'collection remains in its scheduled chapter')
''')
print('PASS: later-chapter collection stays out of coastal guide and remains in its own chapter')
