"""Location-aware guide entry: usable hearth, known flight, ground route and arrival."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local T,E,L=F.Travel,F.GuideEngine,F.GuideLibrary
local zone,bind,count,start,duration,enabled='Westfall','Thelsamar',1,0,0,1
GetRealZoneText=function() return zone end
GetBindLocation=function() return bind end
GetItemCount=function() return count end
GetTime=function() return 1000 end
C_Container={GetItemCooldown=function() return start,duration,enabled end}
C_Item=nil
UnitOnTaxi=function() return false end
C_Map.GetMapInfo=function(map) return {name=zone} end
C_QuestLog.GetNextWaypoint=function() end
C_QuestLog.IsQuestFlaggedCompleted=function() return false end
F.QuestPolicy.unlocks={};F.QuestPolicy.foreverUnlocks={}
local function fixture(destination)
 local g={id='entry-test',title='Entry',faction='Alliance',zone='Loch Modan',steps={
  {id='earlier',type='note'},
  {id='accept',type='pickup',questID=100009}},
  questData={[100009]={title='Quest',locations={{role='start',zone=destination or 'Loch Modan',name='Quest giver',x=.4,y=.2}}}}}
 L:Register(g);F.Guide=g;F.db.guideID=g.id;F.db.step=2
 F.db.skipped={[1]=true};F.db.manualSkippedSteps={};F.db.confirmedSteps={};F.db.completed={}
 F.QuestLog.byID={};E.catchUpReasons={};T.entryPending=true
 return g
end
F.db.knownFlightPaths={Thelsamar=true,['Sentinel Hill']=true}
local g=fixture();assert(T:EnsureEntry())
local s=g.steps[2]
assert(s.entryTravel and s.travelTo=='Loch Modan' and s.travelMode=='hearth')
assert(T:Note(s)=='Hearth to Thelsamar.','short hearth advice')
assert(F.UI:ActionTitleText(s)=='Hearth to Thelsamar.','short hearth row title')
assert(not T:FlightLeg(s),'hearth must not trigger auto flight')
assert(F.db.skipped[1] and not F.db.skipped[3],'insertion retains skip positions')
assert(not E:Done(s),'remote travel remains unfinished')
L:SaveCurrent();assert(F.db.guides[g.id].stepID=='accept','save resumes original action rather than transient trip')
T.entryPending=true;T:EnsureEntry();assert(#g.steps==3,'rechecking does not duplicate entry travel')
T:HearthCast('UNIT_SPELLCAST_START','player',8690)
duration=3600;T:RefreshEntryPlan()
assert(g.steps[F.db.step]==s and s.travelMode=='hearth','cast start preserves the active travel leg')
assert(not E:Done(s),'hearth cast does not prove arrival')
assert(T:Note(s)=='Hearth to Thelsamar.' and T:EntryTitle(s)=='Hearth to Thelsamar.',
 'row and instructions retain the selected hearth while its cooldown begins')
T:HearthCast('UNIT_SPELLCAST_INTERRUPTED','player',8690)
T:RefreshEntryPlan()
assert(g.steps[F.db.step].travelMode=='flight','interrupted cast may replan')
duration=0;T:RefreshEntryPlan();s=g.steps[F.db.step]
zone='Loch Modan';assert(E:Done(s),'arrival completes entry travel')
E:AdvanceSafe();assert(g.steps[F.db.step].id=='accept','arrival advances to actual quest')
g=fixture();assert(not T:EnsureEntry() and #g.steps==2,'no trip when already in destination zone')
zone='Westfall';duration=3600
g=fixture();T:EnsureEntry();s=g.steps[2]
assert(s.travelMode=='flight' and T:Note(s)=='Fly to Thelsamar.','hearth on cooldown falls back to known flight')
assert(T:FlightLeg(s)=='Sentinel Hill')
count=0;duration=0;g=fixture();T:EnsureEntry()
assert(T:Note(g.steps[2])=='Fly to Thelsamar.','missing item cannot be recommended')
count=1;enabled=0;assert(not T:ReadyHearth('Loch Modan'),'disabled cooldown cannot be recommended')
enabled=nil;assert(not T:ReadyHearth('Loch Modan'),'unknown cooldown cannot be recommended')
enabled=1;bind='Unknown Inn';assert(not T:ReadyHearth('Loch Modan'),'unmapped home is not guessed')
F.db.knownFlightPaths={};g=fixture();T:EnsureEntry();s=g.steps[2]
assert(s.travelTo=='Elwynn Forest' and T:Note(s):find('bridge'),'unknown flight uses reviewed ground connection')
F.db.knownFlightPaths={Thelsamar=true,['Sentinel Hill']=true}
T:RefreshEntryPlan();assert(g.steps[2].travelMode=='flight','newly observed flight paths replace ground travel')
F.db.knownFlightPaths={}
bind='Thelsamar';duration=0;g=fixture();T:EnsureEntry();s=g.steps[2]
duration=3600;assert(not T:Note(s):find('Hearth'),'cooldown changes update existing advice')
T:RefreshEntryPlan();assert(g.steps[2].travelTo=='Elwynn Forest','unavailable hearth replans all ground legs')
duration=0;T:RefreshEntryPlan();assert(g.steps[2].travelMode=='hearth' and #g.steps==3,'ready hearth replaces unfinished ground legs')
-- A catch-up NPC takes priority over the nominal guide region.
duration=0;g=fixture('Westfall');assert(not T:EnsureEntry(),'already at catch-up region; do not send to nominal guide zone')
bind='Another Inn';zone='Loch Modan';T:RememberHearth()
zone='Westfall';assert(T:ReadyHearth('Loch Modan')=='Another Inn','observed bindings support unfamiliar inn names')
bind='Different Inn';assert(not T:ReadyHearth('Loch Modan'),'stale saved binding is rejected')
''')
print('PASS: entry destination, hearth readiness, flight fallback, roads, arrival, saved progress and binding changes')
