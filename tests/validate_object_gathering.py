"""Gathering coordinates remain usable without native quest map markers."""
from pathlib import Path
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
lua=ns['lua']
root=base.resolve().parents[1]
for name in ('Alliance_20_30_QuestData.lua','Alliance_ObjectLocations.lua'):
    lua.execute('assert(loadstring(...))("ForeverRested",F)',(root/'Guides'/name).read_text())
lua.execute(r'''
F.LoadDatabase()
F.Guide={id='gather-test',faction='Alliance',steps={},questData=F.AllianceQuestData}
C_QuestLog.GetNextWaypoint=function() return nil end
C_Map.GetBestMapForUnit=function() return 1440 end
C_Map.GetMapInfo=function(map) if map==1440 then return {name='Ashenvale'} end end
local quest={id=1010,title="Bathran's Hair",objectives={{text="0/5 Bathran's Hair",type='item'}}}
F.QuestLog.byID[1010]=quest
local task={id='bathran',type='objective',questID=1010}
local map,x,y=F.StepPins:TaskLocation(task)
assert(map==1440 and x>.30 and x<.34 and y>.20 and y<.26,'gathering pin uses object spawn area without native markers')
assert(F.ObjectiveQueue:ObjectiveZone(quest,quest.objectives[1],1)=='Ashenvale','same gathering data classifies current zone')
F.Guide.steps={task};F.db.step=1
local waypoint=F.Navigation:Waypoint()
assert(waypoint==1440,'navigation also resolves gathering area')
local unknown={id=999999,title='Client-only',objectives={{text='Gather'}}}
C_QuestLog.GetNextWaypoint=function() return 1440,.32,.23 end
assert(F.ObjectiveQueue:ObjectiveZone(unknown,unknown.objectives[1],1)=='Ashenvale','client-only single objective has zone')
unknown.objectives[2]={text='Another objective'}
assert(F.ObjectiveQueue:ObjectiveZone(unknown,unknown.objectives[1],1)=='Location unknown','quest-wide waypoint cannot relocate multiple objectives')
''')
print('PASS: gathering map pin, arrow and objective zone without native markers')
