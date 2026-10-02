"""Action-step migration, concurrent progress and independent map/minimap markers."""
from pathlib import Path
import runpy

lua=runpy.run_path(str(Path(__file__).with_name("validate_sections.py")))["lua"]
lua.execute(r'''
local L,E,P,N=F.GuideLibrary,F.GuideEngine,F.StepPins,F.Navigation
local g=L.guides['alliance-dun-morogh-01-10']
for _,step in ipairs(g.steps) do
 if step.questID then assert(#step.tasks==1 and step.tasks[1].questID==step.questID) end
end
-- An old grouped position and skip migrate to every new action in that group.
L:ApplyState(g,{stepID='coldridge-pickup',revision=1,skippedIDs={['coldridge-pickup']=true}})
assert(g.steps[F.db.step].legacyGroupID=='coldridge-pickup')
local migrated=0
for i,step in ipairs(g.steps) do
 if step.legacyGroupID=='coldridge-pickup' then assert(F.db.skipped[i]);migrated=migrated+1 end
end
assert(migrated==2)
L:Select(g.id);F.db.skipped={};F.db.completed={};F.db.confirmedSteps={}
local index
for i,s in ipairs(g.steps) do if s.legacyGroupID=='coldridge-pickup' then index=index or i end end
F.db.step=index;F.Refresh()
assert(g.steps[index].questID==170 and g.steps[index+1].questID==233)
local alongside=false
for _,task in ipairs(E:Tasks(nil,true)) do if task.questID==233 then alongside=task.optional end end
assert(alongside,'nearby quest must remain nonblocking alongside work')
F.db.completed[170]=true;F.Refresh();assert(F.db.step==index+1,'progress advances one quest action at a time')
-- Owned pins use the native canvas, and never change user waypoints/tracking.
local mapID=1426
local canvas=CreateFrame('Frame',nil,UIParent);canvas:SetSize(1000,700)
WorldMapFrame={GetCanvas=function() return canvas end,IsShown=function() return true end,
 GetMapID=function() return mapID end,GetCanvasScale=function() return 2 end,
 GetFrameStrata=function() return 'FULLSCREEN' end}
C_Minimap={GetViewRadius=function() return 100 end}
function GetCVarBool() return false end
N.targetMap=1426;N.tx=.25;N.ty=.75;N.north=50;N.west=0
P:Update();assert(P.world:IsShown() and P.mini:IsShown() and not P.mini.edge)
assert(P.world.number.text==tostring(F.db.step))
assert(P.world.icon.texturePath==F.icon and P.mini.icon.texturePath==F.icon)
-- Hover identifies the destination action and renders live objectives and notes.
local savedGuide,savedStep,savedTask=F.Guide,F.db.step,N.waypointTask
local savedQuest=F.QuestLog.byID[101]
F.QuestLog.byID[101]={title='The Troll Cave',complete=false,objectives={{text='Trolls: 8/14',finished=false,type='monster'}}}
local action={type='objective',questID=101,text='Hunt trolls',note='Use the cave entrance.'}
F.Guide={title='Tooltip test guide',steps={{type='note',text='Other step'},action}}
F.db.step=1;N.waypointTask=action
assert(P:DestinationStep()==2,'alongside destination must use its own step number')
local lines={}
local oldAddLine=GameTooltip.AddLine
GameTooltip.AddLine=function(_,line) lines[#lines+1]=line end
P.world.scripts.OnEnter(P.world);F.Tooltips:Tick(3)
assert(GameTooltip.text=='Forever Rested - Step 2')
local text=table.concat(lines,'\n')
assert(text:find('8/14',1,true),'tooltip must include live objective progress')
assert(text:find('Use the cave entrance.',1,true),'tooltip must include step notes')
assert(text:find('Location: 25.0, 75.0',1,true),'tooltip must show destination coordinates')
P.world.scripts.OnLeave(P.world);assert(not GameTooltip:IsShown())
GameTooltip.AddLine=oldAddLine
F.Guide,F.db.step,N.waypointTask=savedGuide,savedStep,savedTask
F.QuestLog.byID[101]=savedQuest
N.north=1000;P:Update();assert(P.mini.edge)
mapID=1429;P:Update();assert(not P.world:IsShown(),'marker must not use coordinates on an unrelated map')
C_Minimap=nil;P:Update();assert(not P.mini:IsShown(),'unknown radius must not invent a minimap scale')
N.targetMap=nil;P:Update();assert(not P.world:IsShown() and not P.mini:IsShown())
-- Secure icon-only targets hide when empty; combat changes are deferred.
F.SecureTarget:UpdateTasks({{mob='Test Wolf'}});assert(F.SecureTarget.frame:IsShown())
combat=true;F.SecureTarget:UpdateTasks({});assert(F.SecureTarget.pending and F.SecureTarget.frame:IsShown())
combat=false;F.SecureTarget:UpdateTasks({});assert(not F.SecureTarget.frame:IsShown())
F.SecureTarget:UpdateTasks({{mob='Test Wolf'}});assert(F.SecureTarget.frame:IsShown())
''')
print("PASS: quest-action steps, legacy group migration, concurrent progress, numbered map/minimap markers, missing-radius fallback and empty target visibility.")
