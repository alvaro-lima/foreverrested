"""A carried quest ingredient changes travel while the guide window is hidden."""
from pathlib import Path

base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
ns = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], ns)
ns['lua'].execute(r'''
F.LoadDatabase();F.UI:Create()
F.UI.frame:Hide()
local bag={[15883]=1}
C_Item={GetItemCount=function(id) return bag[id] or 0 end}
GetItemCount=nil
GetRealZoneText=function() return 'Westfall' end
C_Map.GetMapInfo=function() return {name='Westfall'} end
C_QuestLog.GetNextWaypoint=function() end
UnitClass=function() return 'Druid','DRUID' end
UnitFactionGroup=function() return 'Alliance' end
IsSpellKnown=function(id) return id==18960 end
GetSpellCooldown=function() return 0,0,1 end
GetTime=function() return 1000 end
F.Travel.ReadyHearth=function() return nil end
F.QuestLog.Refresh=function() end
F.QuestLog.TurnedIn=function() return false end
F.QuestLog.byID={[272]={id=272,title='Trial of the Sea Lion',complete=false,
 objectives={{text='Pendant of the Sea Lion: 0/1',finished=false}}}}
F.Guide={id='ingredient-stage-test',faction='Alliance',zone='Ashenvale',
 steps={{id='collect-pendant',type='objective',questID=272}}}
F.db.guideID=F.Guide.id;F.db.step=1;F.db.skipped={};F.db.manualSkippedSteps={}
F.Travel.entryPending=nil;F.Travel.objectiveStage=nil
F.Refresh()
assert(F.Guide.steps[1].type=='objective','first half is carried; second half is local')
assert(F.GuideEngine:ObjectiveLocation(272).zone=='Westfall')

-- Bag update while the main guide is closed changes the active destination.
bag[15882]=1
F.Refresh()
assert(F.Guide.steps[1].entryTravel and F.Guide.steps[1].travelMode=='teleport-moonglade',
 'both halves trigger travel to the Moonglade assembly location')
assert(F.Guide.steps[2].type=='objective' and F.GuideEngine:ObjectiveLocation(272).zone=='Moonglade')
assert(not F.UI.frame:IsShown(),'refresh does not reopen a closed guide')
local total=#F.Guide.steps
F.Refresh()
assert(#F.Guide.steps==total,'repeated refresh does not duplicate the journey')
''')
print('PASS: ingredient collection refreshes travel with the guide hidden')
