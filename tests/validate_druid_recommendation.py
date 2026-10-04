"""Druid recommendations and authoritative undiscovered flight destinations."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
UnitClass=function() return 'Druid','DRUID' end
UnitRace=function() return 'Night Elf','NightElf',4 end
UnitLevel=function() return 20 end
GetRealZoneText=function() return 'Darkshore' end
C_Map.GetMapInfo=function() return {name='Darkshore'} end
F.QuestLog.byID={}
assert(F.GuideLibrary:Recommended()=='alliance-kalimdor-20-24','Kalimdor druid stays on nearby level-20 route')
UnitRace=function() return 'New Elf','NewElf' end
assert(F.GuideLibrary:Recommended()=='alliance-kalimdor-20-24','unknown druid race uses location and druid fallback')
F.db.knownFlightPaths={Thelsamar=true,['Sentinel Hill']=true}
C_TaxiMap={GetTaxiNodesForMap=function() return {{name='Thelsamar, Loch Modan',faction=2,isUndiscovered=true}} end}
F.Travel:ObserveFlightPaths()
assert(not F.Travel:KnowsFlightPath('Thelsamar'),'explicit undiscovered state invalidates cached knowledge')
local step={id='old-flight',type='travel',travelQuestID=100000,travelFrom='Westfall',travelTo='Loch Modan',
 note='Fly to Thelsamar.',travelZones={'Loch Modan'},travelLeg=1,travelFinal=true}
assert(not F.Travel:FlightLeg(step),'unknown destination cannot be offered as a flight')
assert(not F.Travel:Note(step):find('Fly to Thelsamar',1,true),'stale fly text is regenerated')
F.db.knownFlightPaths={}
UnitRace=function() return 'Night Elf','NightElf',4 end
F.GuideLibrary:Select('alliance-eastern-20-22')
for i,s in ipairs(F.Guide.steps) do
 if s.travelTo=='Loch Modan' then assert(not F.Travel:Note(s):find('Fly to Thelsamar',1,true)) end
end
''')
print('PASS: nearby druid route, race fallback, undiscovered-node invalidation and stale flight advice')
