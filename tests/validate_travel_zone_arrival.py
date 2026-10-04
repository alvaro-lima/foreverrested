"""A trip ends at its destination region; the following action owns local movement."""
from pathlib import Path

base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
ns = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local E=F.GuideEngine
local zone='Elwynn Forest'
GetRealZoneText=function() return zone end
C_Map.GetMapInfo=function() return {name=zone} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.5,.5) end
UnitOnTaxi=function() return false end
F.QuestLog.TurnedIn=function() return false end
F.QuestLog.byID[272]={id=272,title='Trial of the Sea Lion',complete=false,
 objectives={{text='Pendant of the Sea Lion: 0/1',finished=false}}}
local trip={id='westfall-trip',type='travel',travelQuestID=272,
 travelAction='objective',travelFrom='Elwynn Forest',travelTo='Westfall',
 travelMode='ground',travelFinal=true,travelLeg=1,travelZones={'Westfall'},
 travelDestination={zone='Westfall',x=.1794,y=.3318,name='Strange Lockbox'}}
local collect={id='endurance',type='objective',questID=272}
F.Guide={steps={trip,collect},faction='Alliance'}
F.db.step=1;F.db.skipped={};F.db.manualSkippedSteps={}
assert(not E:Done(trip),'still travelling before reaching the region')
zone='Westfall'
assert(E:Done(trip),'arrival in Westfall completes the travel leg')
E:AdvanceSafe()
assert(F.db.step==2 and not E:Done(collect),
 'collecting the pendant is a separate action with its own destination')

-- A boat does not complete merely by crossing a zone boundary offshore.
zone='Darkshore'
local boat={id='boat',type='travel',travelQuestID=272,
 travelAction='objective',travelFrom='Teldrassil',travelTo='Darkshore',
 travelMode='boat',travelFinal=true,travelLeg=1,travelZones={'Darkshore'},
 travelDestination={zone='Darkshore',x=.48,y=.11}}
assert(not E:Done(boat),'boat still requires its arrival dock')
''')
print('PASS: travel stops at region arrival; local objective and boat dock remain distinct')
