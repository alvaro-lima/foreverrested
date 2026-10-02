"""Draft route structure, class/race filtering, navigation, and live progression."""
from pathlib import Path
import runpy
import sys

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
lua = runpy.run_path(str(root / "tests/validate.py"))["lua"]
lua.execute(r'''
local E,L=F.GuideEngine,F.GuideLibrary
local ids={'alliance-dun-morogh-01-10','alliance-elwynn-01-10','alliance-teldrassil-01-10','alliance-zephras-01-10'}
local class,race,level='WARRIOR','Dwarf',1
function UnitClass() return class,class end
function UnitRace() return race,race end
function UnitLevel() return level end
function GetPlayerFacing() return 0 end
local map,zone=1426,'Dun Morogh'
C_Map={
 GetBestMapForUnit=function() return map end,
 GetMapInfo=function(id) return id==map and {name=zone,parentMapID=0} or nil end,
 GetPlayerMapPosition=function() return CreateVector2D(.298,.712) end,
 GetWorldPosFromMapPos=function(id,v) return 0,CreateVector2D(-v.y*1000,-v.x*1000) end,
}
live={};objectives={}
C_QuestLog={
 GetNumQuestLogEntries=function() return #live end,
 GetInfo=function(i) return live[i] end,
 GetQuestObjectives=function(id) return objectives[id] end,
 IsComplete=function(id) return objectives[id] and objectives[id][1].finished or false end,
 IsQuestFlaggedCompleted=function(id) return F.db.completed[id]==true end,
}
local questRefs=0
for _,gID in ipairs(ids) do
 local guide=L.guides[gID]; assert(guide and guide.status=='draft' and #guide.steps>30)
 local seen={}
 for _,step in ipairs(guide.steps) do
  assert(step.id and not seen[step.id]);seen[step.id]=true
  for _,task in ipairs(step.tasks or {}) do
   if task.questID then
    local reference=F.AllianceQuestData[task.questID]
    assert(reference and reference.side~=2,'Alliance drafts must not require Horde quests')
    assert(not task.slot,'draft routes must use explicit IDs instead of test bindings')
    questRefs=questRefs+1
   end
  end
 end
end
assert(questRefs>150)
L:Select(ids[1]); F.db.completed={}; F.db.bindings={}; F.db.step=1
F.Refresh();assert(next(F.db.bindings)==nil and F.db.step==1)
assert(F.Tracker.rows[1].body.text:find('Accept Dwarven Outfitters',1,true),'current action must identify the unaccepted quest')
assert(F.Tracker.rows[1].body.text:find('AvailableQuestIcon',1,true),'pickup uses the native exclamation icon')
assert(not F.Tracker.rows[1].body.text:find('Listed XP',1,true),'reward estimates stay out of the main action text')
assert(F.Navigation.targetMap==1426 and F.Navigation.source=='Public area (approx.)')
live={{questID=179,title='Dwarven Outfitters',level=1,isComplete=false}}
objectives[179]={{text='Tough Wolf Meat: 0/8',type='item',numRequired=8,numFulfilled=0,finished=false}}
F.Refresh();assert(F.db.step==2)
local targets=E:Targets();assert(#targets==1 and targets[1].mob,'loot objectives need a source target')
objectives[179][1].numRequired=10; F.Refresh();assert(F.db.step==2,'beta-tuned requirements must remain live')
objectives[179][1].finished=true;F.Refresh();assert(F.db.step==3)
F.db.completed[179]=true;live={};F.Refresh();assert(F.Guide.steps[F.db.step].id=='coldridge-class')
local classTasks=E:Tasks(nil,true)
local hasRune,hasMemo=false,false
for _,task in ipairs(classTasks) do
 if task.questID==3106 then hasRune=true end
 if task.questID==3112 then hasMemo=true end
 assert(not task.classes or task.classes[1]=='WARRIOR','other class tasks must be hidden')
end
assert(hasRune and not hasMemo,'Dwarf warrior should not see Gnome-only memorandum')
E:Move(1);assert(F.db.confirmedSteps['coldridge-class'])
L:SaveCurrent();L:Select(ids[2]);assert(not F.db.confirmedSteps['coldridge-class'])
L:Select(ids[1]);assert(F.db.confirmedSteps['coldridge-class'])
E:ResumeAuto();assert(F.Guide.steps[F.db.step].legacyGroupID=='coldridge-pickup','Auto must pass confirmed trainer stops')
race='Gnome';class='PRIEST';level=2
assert(E:Applies(F.GuideDraft:Task('pickup',98574,true)))
assert(not E:Applies(F.GuideDraft:Task('pickup',98581,true)))
race='Dwarf';class='SHAMAN';level=4
assert(E:Applies(F.GuideDraft:Task('pickup',98581,true)))
for _,token in ipairs({'WARRIOR','PALADIN','HUNTER','ROGUE','PRIEST','MAGE','WARLOCK','DRUID','SHAMAN'}) do
 class=token;assert(F.GuideDraft:Advice()~='' and F.GuideDraft.classAdvice[token])
end
map=99999;zone='Zephras Isle';class='MAGE';race='Skyborne';level=2
L:Select(ids[4]);F.db.completed={};F.db.step=1;live={};F.Refresh()
assert(F.Navigation.targetMap==map,'new zone must resolve from the actual client, without invented map IDs')
assert(E:Applies(F.GuideDraft:Task('pickup',92481,true)))
assert(not E:Applies(F.GuideDraft:Task('pickup',92532,true)))
assert(L:Recommended()==ids[4])
-- Complete all required quests: every unconfirmed manual checkpoint still stops Auto.
for _,gID in ipairs(ids) do
 L:Select(gID);F.db.confirmedSteps={};F.db.completed={};live={};level=10
 for _,step in ipairs(F.Guide.steps) do
  for _,task in ipairs(step.tasks or {}) do if task.questID then F.db.completed[task.questID]=true end end
 end
 E:ResumeAuto()
 local turns=0
 while F.db.step<#F.Guide.steps do
  local current=F.Guide.steps[F.db.step]
  assert(current.confirmOnNext,'completed required quests must not leave an unexplained blocker')
  E:Move(1);turns=turns+1;assert(turns<25)
 end
 assert(F.Guide.steps[F.db.step].confirmOnNext)
end
combat=true;F.Refresh();combat=false
''')
print("PASS: four Alliance drafts, explicit quest IDs, nine class advice branches, race/class filtering, tuned objectives, loot targets, map fallback and per-guide manual checkpoints.")
