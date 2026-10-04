"""Optional arrival clusters skip only beyond their approach, preserving accepted work."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local E=F.GuideEngine
F.Guide=F.GuideLibrary.guides['alliance-eastern-20-22']
F.db.skipped={};F.db.manualSkippedSteps={};F.db.completed={};F.QuestLog.byID={}
C_QuestLog.IsQuestFlaggedCompleted=function() return false end
local zone,x,y='Wetlands',.095,.596
GetRealZoneText=function() return zone end
C_Map.GetMapInfo=function() return {name=zone} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(x,y) end
F.db.knownFlightPaths={}
E:SkipOptionalArrivals()
for index=1,6 do assert(E:StepState(index)=='skipped','whole arrival cluster must visibly skip') end
assert(not F.db.manualSkippedSteps[F.Guide.steps[1].id],'automatic bypass is distinct from explicit quest skip')
F.QuestLog.byID[468]={id=468,complete=false}
E:SkipOptionalArrivals()
for index=1,3 do assert(not F.db.skipped[index],'accepted quest is retained') end
for index=4,6 do assert(F.db.skipped[index],'unaccepted companion remains skipped') end
F.QuestLog.byID={};x=.535;y=.70
E:SkipOptionalArrivals()
for index=1,6 do assert(not F.db.skipped[index],'nearby approach is retained without a flight path') end
zone='Loch Modan';E:SkipOptionalArrivals()
for index=1,6 do assert(not F.db.skipped[index],'starting in the approach zone retains optional work') end
F.db.manualSkippedSteps[F.Guide.steps[1].id]=true;F.db.skipped[1]=true
E:SkipOptionalArrivals();assert(F.db.skipped[1],'explicit skips are preserved')
-- The same policy applies to any annotated arrival quest, not specific IDs.
zone='Ashenvale';x=.8;y=.8
F.Guide={steps={{id='new-arrival',type='pickup',questID=100555,optional=true,
 optionalArrival={from='Darkshore',to='Ashenvale',x=.346,y=.488,radius=.1}}}}
F.db.skipped={};F.db.manualSkippedSteps={};E:SkipOptionalArrivals()
assert(F.db.skipped[1],'generic arrival policy')
-- Forever quest 990 is gated by either Escape Through Force (994) or
-- Escape Through Stealth (995), not the unrelated Tower of Althalaxx.
F.Guide=F.GuideLibrary.guides['alliance-kalimdor-20-24']
F.db.skipped={};F.db.manualSkippedSteps={};F.db.completed={};F.QuestLog.byID={}
zone='Darkshore';x=.392;y=.434
E:SkipOptionalArrivals()
for index=1,3 do assert(F.db.skipped[index],'unavailable Trek chain skips its three actions') end
F.db.completed[970]=true
E:SkipOptionalArrivals()
assert(F.db.skipped[1],'Tower of Althalaxx does not unlock Trek')
F.db.completed[994]=true
E:SkipOptionalArrivals()
for index=1,3 do assert(not F.db.skipped[index],'completed Force branch unlocks Trek actions') end
F.db.completed={};F.QuestLog.byID[990]={id=990,complete=false}
E:SkipOptionalArrivals()
for index=1,3 do assert(not F.db.skipped[index],'accepted Trek remains active even if prerequisite history is missing') end
F.QuestLog.byID={};F.db.completed={}
E:SkipOptionalArrivals()
local supplies={}
for index,step in ipairs(F.Guide.steps) do if step.questID==976 then supplies[#supplies+1]=index end end
assert(#supplies==3,'Supplies retains distinct pickup, escort and turn-in actions')
for _,index in ipairs(supplies) do assert(F.db.skipped[index],'Supplies escort stays optional until Tower stage 973 is complete') end
F.db.completed[973]=true
E:SkipOptionalArrivals()
for _,index in ipairs(supplies) do assert(not F.db.skipped[index],'completed Tower stage unlocks Supplies pickup, escort and turn-in') end
F.db.completed={};F.QuestLog.byID[976]={id=976,complete=false}
E:SkipOptionalArrivals()
for _,index in ipairs(supplies) do assert(not F.db.skipped[index],'accepted Supplies remains active despite missing prerequisite history') end
''')
print('PASS: visible arrival skips, accepted quests, nearby approach, explicit skips and reusable policy')
