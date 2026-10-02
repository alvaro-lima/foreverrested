"""Key quest travel checkpoints, progress bypasses and stable guide reloads."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace["lua"].execute(r'''
function UnitClass() return 'Shaman','SHAMAN' end
function UnitRace() return 'Dwarf','Dwarf' end
function UnitLevel() return 20 end
local zone,filled='Wetlands',false
C_Map.GetMapInfo=function() return {name=zone,parentMapID=0} end
C_QuestLog.IsQuestFlaggedCompleted=function() return false end
C_QuestLog.IsComplete=function(id) return id==94500 and filled end
live={{questID=94500,title='Call of Water',isComplete=false}}
objectives[94500]={{text='Full Blue Waterskin: 0/1',numRequired=1,numFulfilled=0,finished=false}}
F.LoadDatabase(); F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create()
F.db.completed={[94375]=true,[94468]=true,[94495]=true,[94497]=true,[94499]=true}
local L,E=F.GuideLibrary,F.GuideEngine
-- Every boat edge has a departure dock, including both Darnassus aliases.
for _,pair in ipairs({{'Wetlands','Darkshore'}, {'Darkshore','Wetlands'},
 {'Teldrassil','Darkshore'}, {'Darnassus','Darkshore'},
 {'Darkshore','Teldrassil'}, {'Darkshore','Darnassus'}}) do
 local dock=F.Travel:DepartureDock({travelFrom=pair[1],travelTo=pair[2]})
 assert(dock and dock.x>0 and dock.y>0 and dock.name:find('dock'),'boat edge must target a dock')
end
assert(F.Travel.docks.Darkshore.Wetlands.y~=F.Travel.docks.Darkshore.Teldrassil.y,
 'Auberdine boat destinations must use different docks')
L:Select('alliance-wetlands-20-30')
F.db.confirmedSteps['entry-class']=true
E:ResumeAuto()
local function current() return F.Guide.steps[F.db.step] end
assert(current().travelQuestID==94500 and current().travelAction=='objective')
assert(current().text:find('Darkshore',1,true) and current().note:find('Menethil',1,true))
local map,x,y=F.Navigation:Waypoint()
assert(map and x==0.047 and y==0.570,'boat travel points toward Menethil boat dock')
assert(F.UI:StepPriority(current(),F.db.step)=='Critical')
local boardingStep=current()
local oldPosition,oldWorld=C_Map.GetPlayerMapPosition,C_Map.GetWorldPosFromMapPos
local worldX,moving,swimming=100,0,false
C_Map.GetPlayerMapPosition=function() return {x=.047,y=.570} end
C_Map.GetWorldPosFromMapPos=function() return 1,{x=worldX,y=100} end
GetUnitSpeed=function() return moving end
IsSwimming=function() return swimming end
F.Travel:Tick()
for i=1,4 do worldX=worldX+2;moving=7;F.Travel:Tick() end
assert(not F.db.confirmedSteps[boardingStep.id],'walking on the dock must not confirm boarding')
moving=0;swimming=true
for i=1,4 do worldX=worldX+2;F.Travel:Tick() end
assert(not F.db.confirmedSteps[boardingStep.id],'swimming must not confirm boarding')
swimming=false;F.Travel:Tick()
for i=1,3 do worldX=worldX+2;F.Travel:Tick() end
assert(F.db.confirmedSteps[boardingStep.id],'passive boat movement confirms boarding')
assert(current().id~=boardingStep.id,'boarding refresh advances to the next step')
F.db.confirmedSteps[boardingStep.id]=nil
C_Map.GetPlayerMapPosition,C_Map.GetWorldPosFromMapPos=oldPosition,oldWorld
GetUnitSpeed,IsSwimming=nil,nil
E:ResumeAuto()
for _,step in ipairs(F.Guide.steps) do
 if step.travelQuestID==94500 and step.travelAction=='turnin' then
  assert(not E:Done(step),'starting in Wetlands must not complete the future return journey')
 end
end
local count=#F.Guide.steps
L:SaveCurrent();L:Select('alliance-wetlands-20-30')
assert(#F.Guide.steps==count,'travel rows must not duplicate on reload')
zone='Darkshore'; E:ResumeAuto()
assert(current().travelQuestID==94500 and current().text:find('Ashenvale',1,true))
C_QuestLog.GetNextWaypoint=function(id) if id==94500 then return 1440,0.35,0.50 end end
map,x,y=F.Navigation:Waypoint()
assert(map==1440 and x==0.35 and y==0.50,'final travel uses the linked quest waypoint')
C_QuestLog.GetNextWaypoint=nil
map,x,y=F.Navigation:Waypoint()
assert(map==1440 and x==.35 and y==.50,'observed waypoint survives loss of the live POI')
F.Navigation.clientPoints={}
local oldInfo=C_Map.GetMapInfo
C_Map.GetMapInfo=function(map)
 if map==1440 then return {name='Ashenvale',parentMapID=0} end
 return {name=zone,parentMapID=0}
end
map,x,y=F.Navigation:Waypoint()
assert(map==1440 and x==.346 and y==.488,'missing client waypoint falls back to Astranaar arrival area')
local pinMap,pinX,pinY=F.StepPins:TaskLocation(current())
assert(pinMap==map and pinX==x and pinY==y,'map and minimap share the travel fallback')
local oldPosition=C_Map.GetPlayerMapPosition
C_Map.GetPlayerMapPosition=function() return nil end
F.Navigation:Update()
assert(F.Navigation.targetMap==1440 and F.Navigation.angle==nil,'loading waits for player position')
C_Map.GetPlayerMapPosition=oldPosition
GetPlayerFacing=function() return 0 end
F.Navigation:Update()
assert(F.Navigation.angle~=nil,'navigation recovers after boat loading without client quest waypoint')
C_Map.GetMapInfo=oldInfo
zone='Ashenvale'; E:ResumeAuto()
assert(current().travelQuestID==94500,'entering the zone alone does not prove arrival at Astranaar')
E:Move(1); E:ResumeAuto()
assert(current().questID==94500 and current().type=='objective','arrival advances to water collection')
filled=true;live[1].isComplete=true;objectives[94500][1].finished=true
E:ResumeAuto()
assert(current().travelQuestID==94500 and current().travelAction=='turnin')
assert(current().note:find('Auberdine',1,true),'return route uses the harbor')
zone='Darkshore';E:ResumeAuto()
map,x,y=F.Navigation:Waypoint()
assert(map and x==0.327 and y==0.437,'return boat travel points toward Auberdine boat dock')
zone='Wetlands';E:ResumeAuto()
assert(current().travelQuestID==94500,'final NPC arrival requires confirmation or proximity')
E:Move(1); E:ResumeAuto()
assert(current().questID==94500 and current().type=='turnin','return arrival advances to NPC turn-in')
F.db.completed[94500]=true;live={};F.Refresh()
for _,step in ipairs(F.Guide.steps) do
 if step.travelQuestID==94500 then
  assert(E:Done(step),'completed quest bypasses old travel')
  assert(F.UI:StepPriority(step,1)=='Critical','completed travel keeps key marker')
 end
end
-- A different key quest uses the same generator; ordinary quests stay unchanged.
local data={
 [999101]={title='Travel fixture',locations={{role='start',zone='Dun Morogh'},
  {role='requirement',zone='Loch Modan'},{role='end',zone='Ironforge'}}},
 [999102]={title='Ordinary fixture',locations={{role='start',zone='Wetlands'},{role='end',zone='Ashenvale'}}},
}
local guide={faction='Alliance',questData=data,steps={
 {id='key-obj',type='objective',questID=999101,critical=true},
 {id='key-return',type='turnin',questID=999101,critical=true},
 {id='ordinary',type='turnin',questID=999102},
}}
F.Guide=guide; F.Travel:EnsureSteps(guide)
local generic={id='generic-return',travelQuestID=999101,travelAction='turnin',travelFinal=true,
 travelFrom='Loch Modan',travelTo='Ironforge',travelDestination={zone='Ironforge',x=.4,y=.6}}
local oldMapInfo=C_Map.GetMapInfo
C_Map.GetMapInfo=function() return {name='Ironforge',parentMapID=0} end
local gm,gx,gy=F.Navigation:TravelWaypoint(generic)
assert(gm and gx==.4 and gy==.6,'generic travel uses authored destination coordinates without a client POI')
local pm,px,py=F.StepPins:TaskLocation(generic)
assert(pm==gm and px==gx and py==gy,'generic travel pins share the arrow resolver')
C_QuestLog.GetNextWaypoint=function(id) if id==999101 then return 1,.25,.75 end end
gm,gx,gy=F.Navigation:TravelWaypoint(generic)
C_QuestLog.GetNextWaypoint=nil
local cm,cx,cy=F.Navigation:TravelWaypoint(generic)
assert(cm==gm and cx==gx and cy==gy,'generic route retains its observed client waypoint')
local other={id='another-action',travelQuestID=999101,travelAction='objective',travelFinal=true}
assert(not F.Navigation:TravelWaypoint(other),'waypoint cache does not leak between quest actions')
C_Map.GetMapInfo=oldMapInfo
local travels=0
for _,step in ipairs(guide.steps) do
 if step.travelQuestID then assert(step.travelQuestID==999101);travels=travels+1 end
end
assert(travels==3,'generic outbound and return legs')
F.Travel:EnsureSteps(guide);assert(#guide.steps==6,'regeneration remains stable')
''')
print("PASS: generic key-quest travel, blue waterskin outbound/return boats, automatic arrival/completion bypasses and duplicate-free reloads.")
