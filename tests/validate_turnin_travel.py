"""Completion replans an ordinary return trip from the player's live region."""
from pathlib import Path
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local T,E=F.Travel,F.GuideEngine
local zone='Stonetalon Mountains'
GetRealZoneText=function() return zone end
C_Map.GetBestMapForUnit=function() return 1442 end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.36,.15) end
C_Map.GetMapInfo=function(map) return {name=map==1440 and 'Ashenvale' or zone} end
C_QuestLog.GetNextWaypoint=function() end
UnitOnTaxi=function() return false end
GetItemCount=function() return 0 end
F.QuestLog.Refresh=function() end
F.QuestLog.TurnedIn=function() return false end
local function fixture()
 local q={id=100009,title='Return quest',complete=false,objectives={{finished=false}}}
 local g={id='return-test',title='Return',faction='Alliance',zone='Ashenvale',steps={
  {id='gather',type='objective',questID=q.id},
  {id='deliver',type='turnin',questID=q.id}},questData={
  [q.id]={title=q.title,locations={{role='end',zone='Ashenvale',name='Quest giver',x=.37,y=.5}}}}}
 F.Guide=g;F.db.guideID=g.id;F.db.step=1;F.db.skipped={};F.db.manualSkippedSteps={};F.db.confirmedSteps={}
 F.QuestLog.byID={[q.id]=q};T.entryPending=nil;T.lastTurninStep=nil;E.manualHold=nil
 F.db.knownFlightPaths={Astranaar=true,['Stonetalon Peak']=true}
 F.db.flightPathLocations={['Stonetalon Peak']={mapID=1442,x=.36,y=.07,name='Flight master'}}
 return g,q
end
local g,q=fixture()
assert(not T:EnsureTurninTravel(),'unfinished gathering gets no return suggestion')
q.complete=true;q.objectives[1].finished=true
F.Refresh()
local trip=g.steps[F.db.step]
assert(trip.entryTravel and trip.travelAction=='turnin' and trip.travelMode=='flight','completion inserts a flight before ordinary turn-in')
assert(T:Note(trip)=='Fly to Astranaar.')
local map,x,y=F.Navigation:Waypoint()
assert(map==1442 and x==.36 and y==.07,'arrow directs to departure flight master')
F.Refresh();assert(#g.steps==3,'refresh does not duplicate suggestion')
F.db.confirmedSteps[trip.id]=true
F.Refresh();assert(g.steps[F.db.step].id=='deliver' and #g.steps==3,'dismissed suggestion stays dismissed')
g,q=fixture();q.complete=true;F.db.step=2;E.manualHold=true
assert(not T:EnsureTurninTravel() and #g.steps==2,'manual browsing remains held')
E.manualHold=nil;zone='Ashenvale'
assert(not T:EnsureTurninTravel() and #g.steps==2,'same-region turn-in adds no trip')
zone='Stonetalon Mountains';g,q=fixture();q.complete=true;F.db.step=2
F.db.knownFlightPaths={}
assert(T:EnsureTurninTravel())
assert(g.steps[2].travelMode~='flight','unknown destination flight is never assumed')
g,q=fixture();zone='Darnassus'
g.steps={{id='trek-pickup',type='pickup',questID=q.id}}
g.questData[q.id].locations={{role='start',zone='Darkshore',x=.39,y=.43,name='Sentinel Selarin'}}
F.QuestLog.byID={};F.db.step=1;T.lastTurninStep=nil
assert(T:EnsureTurninTravel(),'remote pickup inserts transport without an accepted quest')
assert(g.steps[1].entryTravel and g.steps[1].travelMode=='portal-ruttheran' and g.steps[1].travelAction=='pickup','Darnassus pickup first uses Ruttheran portal')
assert(g.steps[2].travelMode=='boat' and g.steps[3].id=='trek-pickup','boat follows portal before underlying pickup')
assert(not T:EnsureTurninTravel() and #g.steps==3,'pickup transport does not duplicate')
''')
print('PASS: live completion travel, departure arrow, no duplicate/dismissed trips, holds and known paths')
