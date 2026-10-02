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
assert(current().flightPathTravel and current().text:find('Auberdine',1,true),
 'arrival keeps flight collection visible until manually confirmed')
assert(not E:Done(current()),'zone arrival does not prove the flight path was learned')
E:Move(1); E:ResumeAuto()
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
local arrivalStep=current()
C_Map.GetPlayerMapPosition=function() return {x=.386,y=.488} end
E:ResetFrom(F.db.step)
F.Navigation:Update();F.Arrow:Update()
assert(F.Navigation.waypointTask==arrivalStep and F.Navigation.targetMap==1440,
 'From preserves the destination of the travel restart point')
assert(F.Arrow.frame:IsShown(),'From must keep the travel arrow visible')
C_Map.GetPlayerMapPosition=function() return nil end
F.Travel:Tick()
assert(current()==arrivalStep,'missing player position cannot confirm arrival')
C_Map.GetPlayerMapPosition=function() return {x=.386,y=.488} end
F.Travel:Tick()
assert(current()==arrivalStep,'outside the travel arrival area must not advance')
C_Map.GetPlayerMapPosition=function() return {x=.346,y=.488} end
F.Navigation:Update();F.Arrow:Update()
assert(F.Navigation.distance==0 and F.Arrow.frame:IsShown(),'reproduce zero yards after From')
F.Travel:Tick()
assert(not E.manualHold,'reaching the destination releases the From travel hold')
assert(current().flightPathTravel and current().text:find('Astranaar',1,true))
E:Move(1); E:ResumeAuto()
assert(current().questID==94500 and current().type=='objective','wider arrival area advances to water collection without a quest event')
C_Map.GetPlayerMapPosition=oldPosition
filled=true;live[1].isComplete=true;objectives[94500][1].finished=true
E:ResumeAuto()
assert(current().travelQuestID==94500 and current().travelAction=='turnin')
assert(current().note:find('Auberdine',1,true),'return route uses the harbor')
zone='Darkshore';E:ResumeAuto()
assert(current().flightPathTravel)
E:Move(1);E:ResumeAuto()
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
F.Travel:EnsureSteps(guide);assert(#guide.steps==6,'no collection detour without nearby flight master evidence')
-- Discovery is client evidence, independent of manual step confirmation.
F.db.knownFlightPaths={}
local fp={flightPathStop='Thelsamar',confirmOnNext=true,id='fp-fixture'}
assert(not E:Done(fp),'unknown flight path stays visible')
C_TaxiMap={GetTaxiNodesForMap=function() return {
 {name='Thelsamar, Loch Modan',faction=2,isUndiscovered=false},
 {name='Astranaar, Ashenvale',faction=2,isUndiscovered=true},
 {name='Auberdine, Darkshore',faction=2},
 {name='Horde fixture',faction=1,isUndiscovered=false},
} end}
F.Travel:ObserveFlightPaths()
assert(E:Done(fp),'discovered path automatically completes collection')
assert(not F.Travel:KnowsFlightPath('Astranaar'),'undiscovered is not learned')
assert(not F.Travel:KnowsFlightPath('Auberdine'),'missing discovery field is not evidence')
assert(not F.Travel:KnowsFlightPath('Horde fixture'),'ignore opposing faction nodes')
C_TaxiMap=nil
NumTaxiNodes=function() return 3 end
TaxiNodeName=function(i) return ({'Auberdine, Darkshore','Astranaar, Ashenvale','Menethil Harbor, Wetlands'})[i] end
TaxiNodeGetType=function(i) return ({'CURRENT','REACHABLE','DISTANT'})[i] end
F.Travel:ObserveFlightPaths(true)
assert(F.Travel:KnowsFlightPath('Auberdine') and F.Travel:KnowsFlightPath('Astranaar'))
assert(not F.Travel:KnowsFlightPath('Menethil Harbor'),'unreachable does not prove discovery')
NumTaxiNodes,TaxiNodeName,TaxiNodeGetType=nil,nil,nil
F.LoadDatabase()
assert(F.Travel:KnowsFlightPath('Thelsamar'),'flight knowledge survives database reload')
local flightStep={travelQuestID=999101,travelFrom='Ashenvale',travelTo='Darkshore',
 travelFinal=true,travelAction='turnin',travelLeg=1,travelZones={'Darkshore'},
 travelDestination={name='Auberdine harbor',zone='Darkshore',x=.327,y=.437},note='Walk the road'}
assert(F.Travel:Note(flightStep):find('fly to Auberdine',1,true),'known paths replace road advice')
F.db.knownFlightPaths.Auberdine=nil
assert(F.Travel:Note(flightStep)=='Walk the road','unknown destination retains road fallback')
F.db.knownFlightPaths.Auberdine=true
F.db.knownFlightPaths['Menethil Harbor']=true
assert(not F.Travel:FlightLeg({travelFrom='Darkshore',travelTo='Wetlands'}),
 'cross-continent travel still uses boats')
F.db.flightPathLocations.Astranaar={mapID=1414,x=.45,y=.6,name='Astranaar, Ashenvale'}
zone='Ashenvale'
local fm,fx,fy=F.Navigation:TravelWaypoint(flightStep)
assert(fm==1414 and fx==.45 and fy==.6,'flight arrow targets departure flight master')
zone='Darkshore'
assert(not F.Travel:DepartureFlight(flightStep),'arrival never points back to departure')
F.db.knownFlightPaths.Ironforge=true
local direct=F.Travel:Route('Ironforge','Loch Modan')
assert(#direct==1 and direct[1].zone=='Loch Modan','known flight bypasses intermediate road zones')
F.QuestLog.byID[999101]={complete=true}
UnitOnTaxi=function() return true end
assert(not E:Done(flightStep),'flying through the arrival zone does not complete travel')
UnitOnTaxi=nil
local itinerary={faction='Alliance',questData={[999201]={title='Boat and flight',locations={
 {role='start',zone='Wetlands'},
 {role='requirement',zone='Ashenvale',x=.346,y=.488,name='Astranaar'},
}}},steps={{id='boat-flight',type='objective',questID=999201,critical=true}}}
F.Guide=itinerary
F.db.knownFlightPaths={Astranaar=true}
F.Travel:EnsureSteps(itinerary)
assert(#itinerary.steps==3,'boat then flight needs no separate collection rows')
assert(itinerary.steps[1].note:find('boat',1,true),'Wetlands still requires boat')
assert(F.Travel:Note(itinerary.steps[2]):find('fly to Astranaar',1,true))
assert(F.Travel:Note(itinerary.steps[2]):find('learn its flight path',1,true),
 'learn departure path as part of boarding the flight')
F.db.knownFlightPaths={Auberdine=true}
F.Travel:EnsureSteps(itinerary)
assert(#itinerary.steps==4 and itinerary.steps[3].flightPathStop=='Astranaar',
 'walking to Astranaar adds only the missing nearby flight path')
assert(F.Travel:Note(itinerary.steps[2]):find('road',1,true),'missing destination requires walking')
F.db.knownFlightPaths={Auberdine=true,Astranaar=true}
F.Travel:EnsureSteps(itinerary)
assert(#itinerary.steps==3,'known paths produce no learning stops')
assert(not F.Travel:NearFlightStop({from='Darkshore',zone='Ashenvale'},
 {zone='Ashenvale',x=.9,y=.9},true),'remote destination does not create a flight path detour')
''')
print("PASS: travel checkpoints, stable reloads and automatic flight path discovery.")
