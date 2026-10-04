"""Full class delivery -> regional pickup -> boat -> pickup -> reload flow."""
from pathlib import Path
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local E,T,L=F.GuideEngine,F.Travel,F.GuideLibrary
local zone='Darnassus'
GetRealZoneText=function() return zone end
GetSubZoneText=function() return zone=='Darkshore' and 'Auberdine' or "Rut'theran Village" end
C_Map.GetBestMapForUnit=function() return zone=='Darnassus' and 1457 or zone=='Teldrassil' and 1438 or 1439 end
C_Map.GetMapInfo=function(m) return {name=m==1457 and 'Darnassus' or m==1439 and 'Darkshore' or 'Teldrassil'} end
C_Map.GetPlayerMapPosition=function() return zone=='Teldrassil' and {x=.549,y=.971} or {x=.332,y=.402} end
C_QuestLog.GetNextWaypoint=function() end
UnitClass=function() return 'Druid','DRUID' end
UnitRace=function() return 'Night Elf','NightElf' end
UnitLevel=function() return 23 end
UnitFactionGroup=function() return 'Alliance' end
UnitOnTaxi=function() return false end
IsSpellKnown=function(id) return id==1066 end
GetItemCount=function() return 0 end
F.QuestLog.Refresh=function() end
F.QuestLog.byID={}
local delivered=false
F.QuestLog.TurnedIn=function(_,id) return delivered and id==5061 end
local pickupID
for id,q in pairs(F.AllianceQuestData) do if q.title=='Trek to Ashenvale' then pickupID=id end end
assert(pickupID,'real regional breadcrumb metadata exists')
local g={id='class-return-journey',faction='Alliance',zone='Ashenvale',steps={
 {id='aquatic-delivery',type='turnin',questID=5061},
 {id='regional-pickup',type='pickup',questID=pickupID}}}
F.Guide=g;F.db.guideID=g.id;F.db.step=1
F.db.skipped={};F.db.completed={};F.db.manualSkippedSteps={};F.db.confirmedSteps={}
E.catchUpPending=nil;E.manualHold=nil;T.entryPending=nil;T.lastTurninStep=nil
F.QuestLog.byID[5061]={id=5061,complete=true,objectives={}}
delivered=true;F.QuestLog.byID[5061]=nil
F.Refresh()
local travel=g.steps[F.db.step]
assert(travel.entryTravel and travel.travelMode=='portal-ruttheran' and travel.travelAction=='pickup','delivery inserts portal before boat')
assert(T:EntryTitle(travel)=="Portal to Rut'theran Village.")
assert(g.steps[#g.steps].id=='regional-pickup','quest action identity survives insertion')
local count=#g.steps;F.Refresh();assert(#g.steps==count,'refresh cannot duplicate travel')
zone='Teldrassil';F.Refresh()
assert(g.steps[F.db.step].flightPathStop=="Rut'theran Village",'village arrival offers its missing flight path')
F.db.knownFlightPaths["Rut'theran Village"]=true;F.Refresh()
travel=g.steps[F.db.step]
assert(travel.entryTravel and travel.travelMode=='boat','portal arrival advances to boat')
assert(T:EntryTitle(travel)=='Take the boat to Auberdine.')
local dockMap,dockX,dockY=F.Navigation:TravelWaypoint(travel)
assert(dockMap and dockX==.549 and dockY==.971,'boat arrow approaches the observed Ruttheran boarding area')
local worldX=100
C_Map.GetWorldPosFromMapPos=function() return 1,{x=worldX,y=100} end
GetUnitSpeed=function() return 0 end
for i=1,4 do worldX=worldX+2;T:Tick() end
assert(T.boatBoardedStepID==travel.id,'passive boat movement detects boarding on an entry leg')
assert(not F.Navigation:TravelWaypoint(travel),'boarded boat no longer points back to the dock')
assert(not E:Done(travel),'boarding does not claim arrival in Auberdine')
zone='Darkshore';F.Refresh()
assert(g.steps[F.db.step].flightPathStop=='Auberdine','Auberdine arrival offers the missing flight path first')
F.db.knownFlightPaths.Auberdine=true;F.Refresh()
assert(g.steps[F.db.step].id=='regional-pickup','arrival resumes pickup rather than old class work')
local saved={stepID='regional-pickup',revision=g.revision or 1,confirmedSteps=F.db.confirmedSteps}
L:ApplyState(g,saved);E.catchUpPending=nil;F.Refresh()
assert(g.steps[F.db.step].id=='regional-pickup','reload preserves unfinished pickup after completed travel')
F.QuestLog.byID[pickupID]={id=pickupID,complete=false,objectives={}}
local action=g.steps[F.db.step]
assert(E:Done(action,E:Resolve(action)),'accepting quest finishes only the pickup action')
''')
print('PASS: aquatic delivery, real regional pickup, portal/boat instructions, arrival, reload and acceptance')
