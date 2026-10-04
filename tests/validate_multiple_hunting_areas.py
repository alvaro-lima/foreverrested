from pathlib import Path
base=Path(__file__).with_name('validate.py');setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local q={id=1134,title="Pridewings of Stonetalon",complete=false,objectives={{type="item",text="Pridewing Venom Sac: 0/12",finished=false}}}
F.QuestLog.byID={[1134]=q}
F.QuestLog.TurnedIn=function() return false end
local step={id="hunt",type="objective",questID=1134}
F.Guide={steps={step},faction="Alliance"};F.db.step=1;F.db.skipped={}
local record=F.GuideEngine:TargetRecord(q)
assert(#record.locations>1)
local target=record.locations[#record.locations]
C_Map.GetMapInfo=function() return {name=target.zone} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(target.x,target.y) end
local closest=F.GuideEngine:TargetLocation(q)
assert(closest.x==target.x and closest.y==target.y,'nearest recorded hunting area')
local tasks=F.StepPins:HuntingTasks(step)
assert(#tasks>1,'multiple map areas for one hunt')
local seen={}
for _,task in ipairs(tasks) do
 local key=F.StepPins:TaskKey(task)
 assert(not seen[key],'distinct area pin identities');seen[key]=true
 local map,x,y=F.StepPins:TaskLocation(task)
 assert(x==task.huntingLocation.x and y==task.huntingLocation.y)
end
-- The same mechanism works without a hand-authored target record.
F.QuestLog.byID[385]={id=385,title="Crocolisk Hunting",complete=false}
local general=F.StepPins:HuntingTasks({id="other",type="objective",questID=385})
assert(#general>1,'generic hunting metadata supports multiple areas')
-- A farther client waypoint must not override the closest hunting area.
local map,x,y=F.Navigation:Waypoint()
assert(x==target.x and y==target.y and F.Navigation.source=='Hunting area (approx.)')
-- Compare world distances across maps, including when the player is on a submap.
C_Map.GetBestMapForUnit=function() return 10 end
C_Map.GetMapInfo=function(map)
 return {name=map==10 and 'Player submap' or map==20 and 'Near zone' or 'Far zone'}
end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.5,.5) end
C_Map.GetWorldPosFromMapPos=function(map,v)
 return map==40 and 2 or 1,CreateVector2D(v.x*100+(map==30 and 1000 or 0),v.y*100)
end
local near={role='hunting',mapID=20,zone='Near zone',x=.6,y=.5}
local far={role='hunting',mapID=30,zone='Far zone',x=.5,y=.5}
local other={role='hunting',mapID=40,zone='Far zone',x=.5,y=.5}
local invalid={role='hunting',mapID=99,zone='Unavailable zone',x=.5,y=.5}
assert(F.Navigation:ReferencePoint({locations={invalid,other,far,near}},'hunting')==near,
 'nearest valid area in the same world space')
C_Map.GetWorldPosFromMapPos=nil
C_Map.GetBestMapForUnit=function() return 20 end
assert(F.Navigation:ReferencePoint({locations={far,near}},'hunting')==near,
 'same-zone fallback when world positions are unavailable')
''')
print('PASS: multiple hunting areas, unique pins, nearest navigation and generic quest support')
