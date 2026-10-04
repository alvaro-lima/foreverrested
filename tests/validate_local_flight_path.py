"""A town arrival inserts one learn-flight-path step only when needed."""
from pathlib import Path

base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
ns = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local T,E=F.Travel,F.GuideEngine
F.db.flightKnowledgeVersion=1
F.db.knownFlightPaths={Auberdine=true,Astranaar=true}
F.LoadDatabase()
assert(not T:KnowsFlightPath('Auberdine'),'reload removes flight paths inferred from the old global-map scan')
local zone,subzone='Darkshore','Auberdine'
GetRealZoneText=function() return zone end
GetSubZoneText=function() return subzone end
C_Map.GetBestMapForUnit=function() return zone=='Darkshore' and 1439 or 1457 end
C_Map.GetMapInfo=function(map) return {name=map==1439 and 'Darkshore' or 'Darnassus'} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.332,.402) end
UnitOnTaxi=function() return false end
local function guide()
 F.Guide={id='local-flight-test',faction='Alliance',steps={{id='continue',type='note',text='Continue'}}}
 F.db.step=1;F.db.skipped={};F.db.manualSkippedSteps={};F.db.knownFlightPaths={}
 E.manualHold=nil
end
guide()
F.QuestLog.Refresh=function() end
F.Refresh()
assert(F.Guide.steps[1].flightPathStop=='Auberdine','refresh while already in Auberdine inserts the missing path')
local step=F.Guide.steps[1]
assert(step.flightPathStop=='Auberdine' and step.flightPathTravel and step.optional,'distinct optional learning action')
assert(F.Guide.steps[2].id=='continue','original action remains next')
assert(not E:Done(step),'arrival in town alone does not prove discovery')
assert(not T:EnsureLocalFlightPath() and #F.Guide.steps==2,'refresh does not duplicate local action')
F.StepPins.TaskLocation=function() return 1439,.332,.402 end
assert(not T:SkipTravelNearNext() and not F.db.skipped[1],
 'nearby next quest cannot auto-skip the flight-path learning row')
T:Tick()
assert(F.db.step==1 and not F.db.skipped[1],'regular travel tick keeps missing flight path active')
F.db.skipped[1]=true;F.db.step=2
F.Refresh()
assert(F.db.step==1 and not F.db.skipped[1],'refresh repairs an older automatic skip of the local flight path')
F.db.knownFlightPaths.Auberdine=true
assert(E:Done(step),'observed flight path completes learning action')
guide();subzone='Wavestrider Beach'
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.8,.8) end
assert(not T:EnsureLocalFlightPath(),'being elsewhere in Darkshore does not invent a town visit')
guide();subzone='Auberdine';E.manualHold=true
assert(not T:EnsureLocalFlightPath(),'manual browsing holds local insertion')
E.manualHold=nil
F.db.manualSkippedSteps['flightpath:local:local-flight-test:Darkshore']=true
assert(not T:EnsureLocalFlightPath(),'explicit skip is respected')
guide();zone='Darnassus';subzone="Rut'theran Village"
assert(not T:EnsureLocalFlightPath(),'Darnassus does not stand in for the village taxi')
''')
print('PASS: local flight-path discovery, town proximity, deduplication, manual hold and skip')
