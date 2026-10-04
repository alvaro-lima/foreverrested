"""Flight selection only for the active travel step and matching flight master."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace["lua"].execute(r'''
F.LoadDatabase()
local step={id='flight-test',type='travel',travelQuestID=94500,
 travelAction='objective',travelFrom='Darkshore',travelTo='Ashenvale'}
F.Guide={steps={step}};F.db.step=1;F.db.skipped={}
F.db.knownFlightPaths={Astranaar=true}
local realDone=F.GuideEngine.Done
F.GuideEngine.Done=function() return false end
local nodes={{name='Auberdine, Darkshore',state='CURRENT'},
 {name='Astranaar, Ashenvale',state='REACHABLE'}}
NumTaxiNodes=function() return #nodes end
TaxiNodeName=function(i) return nodes[i].name end
TaxiNodeGetType=function(i) return nodes[i].state end
local calls=0
TakeTaxiNode=function(i) assert(i==2);calls=calls+1 end
F.Travel:AutoFly();assert(calls==1,'matching flight must depart')
local function blocked(reason)
 F.Travel:AutoFly();assert(calls==1,reason)
end
IsShiftKeyDown=function() return true end;blocked('Shift pauses flight')
IsShiftKeyDown=nil
combat=true;blocked('combat prevents flight');combat=false
UnitOnTaxi=function() return true end;blocked('already flying');UnitOnTaxi=nil
nodes[1].name='Thelsamar, Loch Modan';blocked('wrong master')
nodes[1].name='Auberdine, Darkshore'
nodes[2].state='DISTANT';blocked('unreachable destination')
nodes[2].state='REACHABLE'
nodes[3]={name=nodes[2].name,state='REACHABLE'};blocked('ambiguous destination');nodes[3]=nil
F.db.skipped[1]=true;blocked('skipped step');F.db.skipped={}
step.travelAction='turnin';F.QuestLog.byID={};blocked('unfinished turnin quest')
F.QuestLog.byID[94500]={complete=true}
F.Travel:AutoFly();assert(calls==2,'ready return flight')
calls=1;step.travelQuestID=nil;step.flightPathStop='Auberdine'
blocked('learning a flight point must not take a flight')
step.travelQuestID=94500;step.travelFrom='Wetlands';step.travelTo='Darkshore'
blocked('cross-continent travel must not fly')
step.travelFrom='Darkshore';step.travelTo='Ashenvale';TakeTaxiNode=nil
blocked('missing API is harmless')
-- Screenshot regression: Astranaar -> Auberdine return flight, modern nodes.
step.travelFrom='Ashenvale';step.travelTo='Darkshore'
F.db.knownFlightPaths.Auberdine=true
NumTaxiNodes=function() return 0 end
local ready=false
C_Map.GetBestMapForUnit=function() return 1440 end
C_Map.GetMapInfo=function(map)
 return map==1440 and {parentMapID=1414,mapType=3} or {parentMapID=0,mapType=2}
end
C_TaxiMap={GetAllTaxiNodes=function(map)
 assert(map==1414,'structured nodes require continent map')
 if not ready then return {} end
 return {{name='Astranaar, Ashenvale',state=0,slotIndex=4},
  {name='Auberdine, Darkshore',state=1,slotIndex=7}}
end}
TakeTaxiNode=function(i) assert(i==7);calls=calls+1 end
F.Travel:FlightMapOpened();assert(calls==1,'wait for loading nodes')
ready=true;F.Travel:FlightMapTick()
assert(calls==2 and not F.Travel.flightAttempts,'retry selects correct structured slot')
F.Travel:FlightMapTick();assert(calls==2,'do not take the flight twice')
local selected
C_GossipInfo={GetOptions=function() return {{icon=132057,status=0,gossipOptionID=42}} end,
 SelectOption=function(id) selected=id end}
assert(F.Travel:OpenFlightGossip() and selected==42,'NPC gossip opens flight service')
selected=nil;IsShiftKeyDown=function() return true end
F.Travel:OpenFlightGossip();assert(not selected,'Shift suppresses gossip selection')
IsShiftKeyDown=nil
step.travelFrom='Wetlands';step.travelTo='Loch Modan'
step.travelFinal=true;step.travelDestination={name='Noric Lothrache',zone='Loch Modan'}
F.db.knownFlightPaths.Thelsamar=true
C_Map.GetBestMapForUnit=function() return 1437 end
C_Map.GetMapInfo=function() return {name='Wetlands'} end
local px,py=.63,.70
C_Map.GetPlayerMapPosition=function() return CreateVector2D(px,py) end
assert(not F.Travel:FlightLeg(step),'Dun Algaz must not send player back to Menethil')
local map,x,y,source=F.Navigation:TravelWaypoint(step)
assert(map==1437 and x==.535 and y==.70 and source=='Road exit (approx.)')
assert(F.Travel:Note(step):find('Continue through Dun Algaz',1,true))
assert(not F.Travel:AutoFlightStep(),'walking route does not auto-fly')
px,py=.095,.596
assert(F.Travel:FlightLeg(step)=='Menethil Harbor','near harbor keeps flight option')
assert(F.Travel:Note(step):lower():find('fly to thelsamar',1,true))
C_Map.GetPlayerMapPosition=function() return nil end
assert(not F.Travel:WalkingExit(step),'unknown position never invents a walking shortcut')
-- General rule: any guide with a reviewed direct road and readable positions.
step.travelFrom='Ashenvale';step.travelTo='Darkshore'
step.travelDestination={zone='Darkshore',name='Auberdine',x=.2,y=.2}
F.db.flightPathLocations.Astranaar={mapID=1414,x=.9,y=.9}
F.db.knownFlightPaths.Auberdine=true
C_Map.GetBestMapForUnit=function() return 1440 end
C_Map.GetMapInfo=function(map)
 return {name=map==1440 and 'Ashenvale' or 'Darkshore',parentMapID=0}
end
F.AllianceZoneMaps.Darkshore=1439
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.21,.21) end
C_Map.GetWorldPosFromMapPos=function(map,pos) return 1,CreateVector2D(pos.x*1000,pos.y*1000) end
assert(F.Travel:WalkingExit(step).name=='Auberdine','near road destination avoids distant departure')
assert(not F.Travel:FlightLeg(step),'shared flight choice respects walking')
assert(F.Travel:Note(step):find('Walking avoids backtracking',1,true))
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.89,.89) end
assert(F.Travel:FlightLeg(step)=='Astranaar','near departure retains flying')
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.21,.21) end
C_Map.GetWorldPosFromMapPos=function(map,pos) return map,CreateVector2D(pos.x*1000,pos.y*1000) end
assert(not F.Travel:WalkingExit(step),'incompatible map spaces cannot imply a shortcut')
local shared={locations={{role='start',zone='Durotar',x=.389,y=.582},
 {role='start',zone='Loch Modan',x=.319,y=.645}}}
F.AllianceZoneMaps['Loch Modan']=1432
assert(F.Travel:ReferenceLocation(shared,'start').zone=='Loch Modan',
 'shared brazier must use the Alliance copy when constructing routes')
local flight={id='in-flight',type='travel',confirmOnNext=true,travelQuestID=94500,travelAction='objective',travelFrom='Westfall',travelTo='Loch Modan',
 travelFinal=true,travelLeg=1,travelZones={'Loch Modan'},travelDestination={name='Norric Lochthane',zone='Loch Modan'}}
local nextFlight={id='second-flight',type='travel',confirmOnNext=true,travelQuestID=94500,
 travelAction='objective',travelFrom='Loch Modan',travelTo='Wetlands',travelLeg=1,travelZones={'Wetlands'}}
F.Guide={steps={flight,nextFlight}};F.db.step=1
F.db.knownFlightPaths['Sentinel Hill']=true
F.db.knownFlightPaths['Menethil Harbor']=true
F.db.confirmedSteps={};F.QuestLog.byID={}
F.GuideEngine.Done=realDone
UnitOnTaxi=function() return true end
assert(F.Travel:Note(flight)=='Fly to Thelsamar.')
local oldRefresh=F.UI.Refresh
F.UI.Refresh=function() end
F.Travel.onTaxi=false
F.Travel:Tick();F.Travel:Tick()
assert(F.db.confirmedSteps[flight.id] and F.db.step==2,'boarding advances the active flight step')
assert(not F.db.confirmedSteps[nextFlight.id],'same flight cannot complete the next leg')
UnitOnTaxi=function() return false end
F.Travel:Tick()
assert(F.GuideEngine:Done(flight),'boarded flight remains complete after landing')
F.db.confirmedSteps={};F.db.step=1
C_Map.GetMapInfo=function() return {name='Loch Modan'} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.4,.4) end
assert(F.GuideEngine:Done(flight),'landing completes flight without boarding confirmation or reaching the NPC')
F.Travel:Tick()
assert(F.db.step==2,'missed boarding still advances after landing')
F.db.step=1
C_Map.GetMapInfo=function() return {name='Westfall'} end
assert(not F.GuideEngine:Done(flight),'departure zone does not complete flight')
flight.travelAction='turnin'
C_Map.GetMapInfo=function() return {name='Loch Modan'} end
assert(not F.GuideEngine:Done(flight),'arrival cannot bypass unfinished quest objectives')
F.QuestLog.byID[94500]={complete=true}
assert(F.GuideEngine:Done(flight),'ready return flight completes at landing')
local pin=F.StepPins:Create(UIParent)
pin.entry={index=1,task=flight}
F.StepPins:Style(pin)
assert(pin.icon.texturePath:find('StatusDone.tga',1,true),'completed flight pin uses done status')
C_Map.GetMapInfo=function() return {name='Westfall'} end
F.StepPins:Style(pin)
assert(pin.icon.texturePath:find('MapStepBadge-thick.tga',1,true),'active travel pin retains step progress')
local travel1={id='optional-road',type='travel',optional=true}
local travel2={id='optional-boat',type='travel',optional=true}
local goal={id='next-npc',type='turnin',questID=999888,zone='Loch Modan',x=.4,y=.4}
F.Guide={steps={travel1,travel2,goal}};F.db.step=1;F.db.skipped={}
C_QuestLog.GetNextWaypoint=nil
C_Map.GetMapInfo=function() return {name='Loch Modan'} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.8,.8) end
assert(not F.Travel:SkipTravelNearNext(),'distant target must not skip travel')
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.4,.4) end
UnitOnTaxi=function() return true end
assert(not F.Travel:SkipTravelNearNext(),'flying over target must not skip travel')
UnitOnTaxi=function() return false end
assert(F.Travel:SkipTravelNearNext(),'any arrival near next NPC bypasses travel')
assert(F.db.skipped[1] and F.db.skipped[2] and F.db.step==3,'all intervening travel steps are skipped')
assert(F.GuideEngine:StepState(1)=='skipped','bypassed travel keeps skipped status')
assert(not F.db.skipped[3],'quest action must remain unskipped')
F.UI.Refresh=oldRefresh
F.Guide.faction='Alliance'
assert(F.Navigation:ReferencePoint(shared,'start').zone=='Loch Modan',
 'quest navigation must agree with route construction')
''')
print("Auto flight validation passed")
