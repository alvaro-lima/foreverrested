from pathlib import Path
base=Path(__file__).with_name('validate.py');setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local T=F.Travel
local class,known,cooldown='DRUID',true,0
UnitClass=function() return class,class end
UnitFactionGroup=function() return 'Alliance' end
IsSpellKnown=function(id) return id==18960 and known end
GetSpellCooldown=function() return 10,cooldown,1 end
GetTime=function() return 11 end
T.ReadyHearth=function() return nil end
F.db.knownFlightPaths={};F.db.flightPathLocations={}
F.db.knownFlightPaths.Moonglade=true
assert(T:Route('Darkshore','Moonglade')[1].mode=='teleport-moonglade','learned teleport preferred for Moonglade returns')
assert(F.UI:ActionTitleText({type='travel',travelMode='teleport-moonglade'})=='Teleport to Moonglade.','authored return travel title names teleport')
F.db.knownFlightPaths={}
local villageRoute=T:Route('Darnassus','Darkshore')
assert(#villageRoute==2 and villageRoute[1].mode=='portal-ruttheran' and villageRoute[2].mode=='boat','Darnassus to Auberdine uses portal then boat')
F.db.knownFlightPaths={["Rut'theran Village"]=true,Auberdine=true}
local villageBoat=T:Route('Teldrassil','Darkshore')
assert(#villageBoat==1 and villageBoat[1].mode=='boat','cached flight nodes do not prove village-to-Auberdine flight')
assert(not T:FlightLeg({travelFrom='Teldrassil',travelTo='Darkshore'}),'unknown village connection cannot become a flight')
T.ReadyHearth=function() return 'Auberdine' end
local fixedBoat={entryTravel=true,travelMode='boat',travelFrom='Teldrassil',travelTo='Darkshore',entryGoal='Darkshore',note='Board the boat to Auberdine.'}
assert(T:EntryTitle(fixedBoat)=='Take the boat to Auberdine.' and T:Note(fixedBoat)==fixedBoat.note,'selected boat keeps boat instructions despite ready hearth')
T.ReadyHearth=function() return nil end
F.db.knownFlightPaths={}
local cityRoute=T:Route('Darkshore','Darnassus')
assert(#cityRoute==2 and cityRoute[1].mode=='boat' and cityRoute[2].mode=='portal-darnassus','Auberdine to Darnassus uses boat then portal')
local islandRoute=T:Route('Darnassus','Teldrassil')
assert(#islandRoute==1 and islandRoute[1].mode~='portal-ruttheran','Teldrassil island work uses eastern gate')
local moongladeCity=T:Route('Moonglade','Darnassus')
assert(#moongladeCity==2 and moongladeCity[1].mode=='druid-flight' and moongladeCity[2].mode=='portal-darnassus','druid flight lands at village outside city')
assert(not F.Navigation:TravelWaypoint({travelMode='portal-ruttheran'}),'unknown portal entrance has no fabricated arrow')
local legs=T:Route('Ashenvale','Darkshore')
assert(#legs==3 and legs[1].mode=='teleport-moonglade' and legs[2].mode=='druid-flight')
assert(legs[3].text:find('marked',1,true) and not legs[3].text:find('Check',1,true),'marked boat dock gives direct boarding instructions')
assert(legs[1].zone=='Moonglade' and legs[2].zone=='Teldrassil' and legs[3].zone=='Darkshore' and legs[3].mode=='boat')
assert(T:EntryTitle({travelMode=legs[1].mode})=='Teleport to Moonglade.')
assert(not F.Navigation:TravelWaypoint({travelMode='teleport-moonglade'}),'no ground arrow for teleport')
C_Map.GetMapInfo=function() return {name='Moonglade'} end
local dm,dx,dy=F.Navigation:TravelWaypoint({travelMode='druid-flight'})
assert(dm and dx==.4415 and dy==.4523,'recorded druid flight master coordinates')
F.Guide={steps={{id='port',type='travel',entryTravel=true,travelMode='teleport-moonglade',travelTo='Moonglade',entryGoal='Darkshore'}}}
F.db.step=1;F.db.skipped={}
assert(not F.Navigation:Waypoint(),'no quest arrow while teleport is next')
GetRealZoneText=function() return 'Ashenvale' end
F.Travel:RefreshEntryPlan()
assert(#F.Guide.steps==1 and F.Guide.steps[1].id=='port','refresh retains the active teleport leg')
GetRealZoneText=function() return 'Moonglade' end
assert(F.GuideEngine:Done(F.Guide.steps[1]),'arrival completes teleport leg separately')
local departure={mapID=493,x=.4,y=.5,name='Moonglade'}
F.db.flightPathLocations.Moonglade=departure
local map,x,y=F.Navigation:TravelWaypoint({travelMode='druid-flight'})
assert(x==.4415 and y==.4523,'ordinary Moonglade node cannot replace druid departure')
local flight={id='druid-departure',type='travel',travelMode='druid-flight',travelFrom='Moonglade',travelTo='Teldrassil'}
local savedGuide=F.Guide
F.Guide={steps={flight}};F.db.step=1
local fm,fx,fy=F.Navigation:Waypoint()
assert(fm and fx==.4415 and fy==.4523 and F.Navigation.waypointTask==flight,'authored flight navigates to special departure NPC without entry flags')
local pm,px,py=F.StepPins:TaskLocation(flight)
assert(pm==fm and px==fx and py==fy,'map pin and arrow share the flight NPC')
assert(F.StepPins:DestinationStep()==1,'flight pin uses its own numbered step')
assert(F.UI:ActionContact(flight):find("Silva Fil'naveth",1,true),'flight tooltip identifies the special NPC')
assert(F.UI:StepLocation(flight):find('Moonglade',1,true),'flight tooltip locates departure rather than arrival')
F.Guide={steps={{},{},{},{},{},{},flight}};F.db.step=7
local pin=F.StepPins:Create(UIParent)
pin.entry={index=7,task=flight};F.StepPins:Style(pin)
assert(pin.number.text=='7','departure pin displays step 7')
F.Guide=savedGuide
F.db.step=1
F.db.knownFlightPaths.Auberdine=true
assert(T:Route('Ashenvale','Darkshore')[1].mode=='teleport-moonglade','saved Auberdine node must not suppress class shortcut')
F.db.knownFlightPaths.Astranaar=true
assert(T:Route('Ashenvale','Darkshore')[1].mode=='flight','both ordinary endpoints permit direct flight')
F.db.knownFlightPaths.Moonglade=true
assert(T:Route('Moonglade','Darkshore')[1].mode=='druid-flight','cached nodes do not prove ordinary Moonglade flight')
F.db.observedFlightConnections={Moonglade={Auberdine=true}}
local oldPosition=C_Map.GetPlayerMapPosition
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.4,.5) end
assert(T:Route('Moonglade','Darkshore')[1].mode=='flight','actually observed reachable ordinary flight can be used')
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.4415,.4523) end
assert(T:Route('Moonglade','Darkshore')[1].mode=='druid-flight','nearby Silva wins even with known reachable normal flight')
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.4,.5) end
assert(T:Route('Moonglade','Darkshore')[1].mode=='flight','closer ordinary departure remains available')
C_Map.GetPlayerMapPosition=function() return nil end
assert(T:Route('Moonglade','Darkshore')[1].mode=='flight','unknown player position does not invent proximity')
C_Map.GetPlayerMapPosition=oldPosition
F.db.observedFlightConnections={Moonglade={}}
assert(T:Route('Moonglade','Darkshore')[1].mode=='druid-flight','unavailable ordinary destination retains druid route')
assert(not T:FlightLeg({travelMode='druid-flight',travelFrom='Moonglade',travelTo='Teldrassil'}),'druid leg never switches to ordinary flight')
assert(not T:FlightLeg({travelMode='boat',travelFrom='Teldrassil',travelTo='Darkshore'}),'boat leg never switches to unavailable ordinary flight')
F.db.knownFlightPaths={}
known=false
assert(T:Route('Ashenvale','Darkshore')[1].mode~='teleport-moonglade','unlearned spell excluded')
known=true;cooldown=60
assert(T:Route('Ashenvale','Darkshore')[1].mode~='teleport-moonglade','active cooldown excluded')
cooldown=0;class='WARRIOR'
assert(T:Route('Ashenvale','Darkshore')[1].mode~='teleport-moonglade','other classes excluded')
class='DRUID';UnitFactionGroup=function() return 'Horde' end
assert(not T:DruidShortcut('Ashenvale','Darkshore'),'Alliance destination restricted')
UnitFactionGroup=function() return 'Alliance' end
assert(T:Route('Moonglade','Darkshore')[1].mode=='druid-flight','continue after teleport')
C_Map.GetMapInfo=function() return {name='Darkshore'} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.332,.402) end
local boat={id='boat',type='travel',travelMode='boat',travelFrom='Teldrassil',travelTo='Darkshore',travelQuestID=272,travelAction='objective',travelFinal=true,travelLeg=3,travelZones={'Moonglade','Teldrassil','Darkshore'}}
F.QuestLog.byID[272]={id=272,complete=false}
assert(F.GuideEngine:Done(boat),'boat completes at arrival dock without reaching quest objective')
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.8,.8) end
assert(not F.Travel:TransportArrived(boat),'zone alone does not prove dock arrival')
C_Map.GetMapInfo=function() return {name='Teldrassil'} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.549,.971) end
assert(not F.Travel:TransportArrived(boat),'departure dock is not arrival')
local cross=T:Route('Moonglade','Westfall')
assert(cross[1].mode=='druid-flight' and cross[2].mode=='boat','Moonglade exit uses specific druid and boat legs')
for _,leg in ipairs(cross) do assert(not leg.text:find('if it returns',1,true),'no conditional hearth advice') end
T.ReadyHearth=function(_,zone) if zone=='Stormwind City' then return 'Stormwind' end end
local near=T:Route('Moonglade','Westfall')
assert(near[1].mode=='hearth' and near[1].zone=='Stormwind City' and near[#near].zone=='Westfall','ready known nearby hearth plus reviewed onward route')
assert(T:EntryTitle({entryTravel=true,travelMode='hearth',travelTo='Stormwind City',entryGoal='Westfall'})=='Hearth to Stormwind.','nearby hearth title reflects actual binding')
T.ReadyHearth=function() return nil end
assert(T:Route('Moonglade','Westfall')[1].mode=='druid-flight','unavailable hearth recalculates transport')
T.ReadyHearth=function() return 'Auberdine' end
assert(T:Route('Ashenvale','Darkshore')[1].mode=='hearth','ready hearth preferred')
''')
print('PASS: druid shortcut, learned spell/cooldown, faction, direct transport priority and safe navigation')
