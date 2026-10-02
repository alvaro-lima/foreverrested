"""Key quest travel checkpoints, progress bypasses and stable guide reloads."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace["lua"].execute(r'''
function UnitClass() return 'Shaman','SHAMAN' end
function UnitRace() return 'Dwarf','Dwarf' end
function UnitLevel() return 20 end
local zone,filled='Wetlands',false
C_Map.GetMapInfo=function() return {name=zone,parentMapID=0} end
C_QuestLog.IsQuestFlaggedCompleted=function() return false end
C_QuestLog.IsComplete=function(id) return id==94500 and filled end
live={{questID=94500,title='Call of Water',isComplete=false}}
objectives[94500]={{text='Full Blue Waterskin: 0/1',numRequired=1,numFulfilled=0,finished=false}}
F.LoadDatabase(); F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create()
F.db.completed={[94375]=true,[94468]=true,[94495]=true,[94497]=true,[94499]=true}
local L,E=F.GuideLibrary,F.GuideEngine
L:Select('alliance-wetlands-20-30')
F.db.confirmedSteps['entry-class']=true
E:ResumeAuto()
local function current() return F.Guide.steps[F.db.step] end
assert(current().travelQuestID==94500 and current().travelAction=='objective')
assert(current().text:find('Darkshore',1,true) and current().note:find('Menethil',1,true))
local map,x,y=F.Navigation:Waypoint()
assert(map and x==0.0832 and y==0.5857,'boat travel points toward Menethil harbor')
assert(F.UI:StepPriority(current(),F.db.step)=='Critical')
local count=#F.Guide.steps
L:SaveCurrent();L:Select('alliance-wetlands-20-30')
assert(#F.Guide.steps==count,'travel rows must not duplicate on reload')
zone='Darkshore'; E:ResumeAuto()
assert(current().travelQuestID==94500 and current().text:find('Ashenvale',1,true))
C_QuestLog.GetNextWaypoint=function(id) if id==94500 then return 1440,0.35,0.50 end end
map,x,y=F.Navigation:Waypoint()
assert(map==1440 and x==0.35 and y==0.50,'final travel uses the linked quest waypoint')
C_QuestLog.GetNextWaypoint=nil
zone='Ashenvale'; E:ResumeAuto()
assert(current().travelQuestID==94500,'entering the zone alone does not prove arrival at Astranaar')
E:Move(1); E:ResumeAuto()
assert(current().questID==94500 and current().type=='objective','arrival advances to water collection')
filled=true;live[1].isComplete=true;objectives[94500][1].finished=true
E:ResumeAuto()
assert(current().travelQuestID==94500 and current().travelAction=='turnin')
assert(current().note:find('Auberdine',1,true),'return route uses the harbor')
zone='Darkshore';E:ResumeAuto()
map,x,y=F.Navigation:Waypoint()
assert(map and x==0.3677 and y==0.4428,'return boat travel points toward Auberdine harbor')
zone='Wetlands';E:ResumeAuto()
assert(current().travelQuestID==94500,'final NPC arrival requires confirmation or proximity')
E:Move(1); E:ResumeAuto()
assert(current().questID==94500 and current().type=='turnin','return arrival advances to NPC turn-in')
F.db.completed[94500]=true;live={};F.Refresh()
for _,step in ipairs(F.Guide.steps) do
 if step.travelQuestID==94500 then
  assert(E:Done(step),'completed quest bypasses old travel')
  assert(F.UI:StepPriority(step,1)=='Critical','completed travel keeps key marker')
 end
end
-- A different key quest uses the same generator; ordinary quests stay unchanged.
local data={
 [999101]={title='Travel fixture',locations={{role='start',zone='Dun Morogh'},
  {role='requirement',zone='Loch Modan'},{role='end',zone='Ironforge'}}},
 [999102]={title='Ordinary fixture',locations={{role='start',zone='Wetlands'},{role='end',zone='Ashenvale'}}},
}
local guide={faction='Alliance',questData=data,steps={
 {id='key-obj',type='objective',questID=999101,critical=true},
 {id='key-return',type='turnin',questID=999101,critical=true},
 {id='ordinary',type='turnin',questID=999102},
}}
F.Guide=guide; F.Travel:EnsureSteps(guide)
local travels=0
for _,step in ipairs(guide.steps) do
 if step.travelQuestID then assert(step.travelQuestID==999101);travels=travels+1 end
end
assert(travels==3,'generic outbound and return legs')
F.Travel:EnsureSteps(guide);assert(#guide.steps==6,'regeneration remains stable')
''')
print("PASS: generic key-quest travel, blue waterskin outbound/return boats, automatic arrival/completion bypasses and duplicate-free reloads.")
