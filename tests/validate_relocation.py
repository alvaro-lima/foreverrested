"""Loading-screen relocation replans remaining travel without losing quest state."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace["lua"].execute(r'''
F.LoadDatabase()
local refreshed=0
F.Refresh=function() refreshed=refreshed+1 end
local target={zone='Loch Modan',name='Noric',x=.3,y=.6}
local function travel(id,from,to,number,final)
 return {id=id,type='travel',travelQuestID=94500,travelAction='turnin',
 travelFrom=from,travelTo=to,travelLeg=number,travelFinal=final,
 travelZones={'Darkshore','Wetlands','Loch Modan'},travelDestination=target,
 criticalReason='Class unlock',confirmOnNext=true}
end
F.Guide={id='relocation-test',faction='Alliance',steps={
 {id='earlier',type='note'},
 travel('boat','Ashenvale','Darkshore',1,false),
 {id='learn',flightPathQuestID=94500,flightPathStop='Auberdine'},
 travel('harbor','Darkshore','Wetlands',2,false),
 travel('arrival','Wetlands','Loch Modan',3,true),
 {id='turnin',type='turnin',questID=94500},
 {id='later',type='note'}}}
F.db.step=2;F.db.skipped={[1]=true,[7]=true}
F.db.confirmedSteps={earlier=true};F.db.manualSkippedSteps={later=true}
F.db.knownFlightPaths={Thelsamar=true}
F.QuestLog.byID[94500]={complete=true}
local zone,ready='Stormwind City',false
C_Map.GetBestMapForUnit=function() return 1 end
C_Map.GetMapInfo=function() return {name=zone,parentMapID=0} end
C_Map.GetPlayerMapPosition=function() if ready then return CreateVector2D(.4,.4) end end
F.Navigation.clientPoints={old={1,.5,.5}}
F.Travel:PositionChanged()
assert(not next(F.Navigation.clientPoints),'relocation invalidates cached quest waypoints')
F.Travel:ReplanAfterRelocation()
assert(F.Travel.relocationPending and refreshed==0,'wait for readable position')
ready=true
combat=true;F.Travel:ReplanAfterRelocation()
assert(F.Travel.relocationPending,'combat defers replan');combat=false
F.Travel:ReplanAfterRelocation()
assert(refreshed==1 and not F.Travel.relocationPending)
assert(F.Guide.steps[2].travelFrom=='Stormwind City','new journey starts at hearth location')
assert(F.Guide.steps[2].travelTo=='Loch Modan','known flight route uses new departure')
assert(F.Guide.steps[2].id=='arrival','final arrival identity is preserved')
assert(F.Guide.steps[3].id=='turnin' and F.Guide.steps[4].id=='later')
assert(F.db.skipped[1] and F.db.skipped[4],'skips reindex by stable ID')
assert(F.db.confirmedSteps.earlier and F.db.manualSkippedSteps.later)
assert(F.QuestLog.byID[94500].complete,'replan never changes quest completion')
-- Same-zone hearth movement refreshes live choices without rebuilding rows.
zone='Stormwind City'
local steps=F.Guide.steps
F.Travel:PositionChanged();F.Travel:ReplanAfterRelocation()
assert(F.Guide.steps==steps and refreshed==2,'same-zone movement only refreshes guidance')
-- Normal arrival zones retain the itinerary and use regular progress checks.
zone='Loch Modan'
F.Travel:PositionChanged();F.Travel:ReplanAfterRelocation()
assert(F.Guide.steps==steps and refreshed==3,'arrival does not reroute back to departure')
''')
print("PASS: relocation readiness, rerouting, stable progress and arrival checks")
