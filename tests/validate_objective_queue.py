"""Persistent objective queue follows live completion and explicit quest skips."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
namespace={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],namespace)
namespace['lua'].execute(r'''
F.LoadDatabase();F.UI:Create()
F.Guide={steps={{id='one',type='objective',questID=101},
 {id='two',type='objective',questID=102},
 {id='travel',type='travel',travelQuestID=103},
 {id='three',type='objective',questID=103}}}
F.db.manualSkippedSteps={};F.db.skipped={}
F.QuestLog.list={
 {id=101,title='First',objectives={{text='A: 1/3',finished=false},{text='B: 3/3',finished=true}}},
 {id=102,title='Second',objectives={{text='C: 0/4',finished=false}}},
 {id=103,title='Third',objectives={{text='D: 0/2',finished=false}}},
 {id=104,title='Outside guide',objectives={{text='E: 0/5',finished=false}}}}
F.db.completed={};C_QuestLog.IsQuestFlaggedCompleted=function() return false end
local queue=F.ObjectiveQueue
assert(#queue:Build()==3,'unfinished objectives across quests are queued')
F.db.step=1
local display=queue:DisplayRows(queue:Build())
assert(display[1].text:find('Current objectives',1,true))
assert(display[2].entries[1].questID==101,'active objective owns current section')
assert(display[3].text:find('Upcoming objectives',1,true) and not display[3].expanded,'upcoming collapsed by default')
queue.otherAreasExpanded=true
local expanded=queue:DisplayRows(queue:Build())
assert(expanded[4].entries[1].questID==102 and expanded[5].entries[1].questID==103,'upcoming follows guide order')
F.Guide.steps[1]={id='trip',type='travel',travelQuestID=103,travelAction='objective'}
local travel=queue:DisplayRows(queue:Build())
assert(travel[2].entries[1].questID==103,'travel keeps destination objective current across zones')
F.Guide.steps[1]={id='one',type='objective',questID=101}
queue.otherAreasExpanded=false

for _,entry in ipairs(queue:Build()) do assert(entry.questID~=104,'quests outside the guide are excluded') end
F.db.manualSkippedSteps.one=true
assert(#queue:Build()==2,'skipping quest removes its objectives')
F.db.manualSkippedSteps.travel=true
assert(#queue:Build()==2,'skipping travel does not skip its quest')
F.db.skipped[2]=true
assert(#queue:Build()==2,'automatic route skips do not discard accepted quests')
F.QuestLog.list[2].complete=true
assert(#queue:Build()==1,'ready turnins leave objective queue')
F.db.manualSkippedSteps.one=nil
assert(#queue:Build()==2,'unskipping restores unfinished objectives')
F.QuestLog.list[1].objectives[1].finished=true
assert(#queue:Build()==1,'finished objectives leave immediately')
queue:Refresh()
assert(queue.frame and queue.renderedText:find('Third',1,true),'panel renders live quest grouping')
assert(queue.frame:IsShown(),'nonempty queue is visible')
F.QuestLog.list={};queue:Refresh()
assert(not queue.frame:IsShown(),'empty queue hides automatically')
assert(queue.button.enabled==false,'empty queue disables the button')
F.QuestLog.list={{id=103,title='Third',objectives={{text='D: 0/2',finished=false}}}}
queue:Refresh();assert(queue.frame:IsShown(),'new objectives reopen the panel')
assert(queue.button.enabled==true,'objectives enable the button again')
F.db.objectivesHidden=true;queue:Refresh()
assert(not queue.frame:IsShown(),'manual toggle stays respected')
''')
print('PASS: objective queue, live completion, skips, unskips and rendering')
