"""Run with Python + lupa (Lua 5.1). No client or addon dependencies required."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[1]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
unpack = unpack or table.unpack
combat = false
UIParent = {}
SlashCmdList = {}
DEFAULT_CHAT_FRAME = {AddMessage=function() end}
function InCombatLockdown() return combat end
function GetBuildInfo() return 'Forever', 'test', '', 16001 end
function GetPlayerFacing() return 0 end
SLASH_TARGET_MARKER1='/tm'
function SetRaidTarget() error('addon must not call marking API directly') end
function CreateVector2D(x,y) return {x=x,y=y,GetXY=function(self) return self.x,self.y end} end
C_Map = {
 GetBestMapForUnit=function() return 1 end,
 GetPlayerMapPosition=function() return CreateVector2D(.5,.5) end,
 GetWorldPosFromMapPos=function(map,v) return 0,CreateVector2D(-v.y*1000,-v.x*1000) end,
}
live = {
 {questID=101,title='The Troll Cave',level=6,isComplete=false},
 {questID=102,title="A Refugee's Quandary",level=5,isComplete=false},
 {questID=103,title='Bring Back the Mug',level=5,isComplete=true},
}
objectives = {
 [101]={{text='Frostmane Troll Whelp: 8/14',type='monster',numFulfilled=8,numRequired=14,finished=false}},
 [102]={{text="Felix's Box: 1/1",finished=true},{text="Felix's Chest: 0/1",finished=false}},
 [103]={{text='Mug: 1/1',finished=true}},
}
C_QuestLog = {
 GetNumQuestLogEntries=function() return #live end,
 GetInfo=function(i) return live[i] end,
 GetQuestObjectives=function(id) return objectives[id] end,
 IsComplete=function(id) return id==103 end,
 IsQuestFlaggedCompleted=function() return false end,
 GetNextWaypoint=function() return 1,.5,.4 end,
}
local methods = {}
function methods:SetScript(name,fn) self.scripts[name]=fn end
function methods:SetText(t) self.text=t end
function methods:SetAttribute(k,v) assert(not combat,'protected mutation in combat'); self.attributes[k]=v end
function methods:SetEnabled(v) assert(not combat,'protected enable in combat'); self.enabled=v end
function methods:IsShown() return self.shown~=false end
function methods:Show() assert(not (rawget(self,'secure') and combat),'protected visibility in combat'); self.shown=true end
function methods:Hide() assert(not (rawget(self,'secure') and combat),'protected visibility in combat'); self.shown=false end
function methods:SetShown(v) assert(not (rawget(self,'secure') and combat),'protected visibility in combat'); self.shown=v end
function methods:GetCenter() return 500,500 end
function methods:GetWidth() return rawget(self,'width') or 140 end
function methods:GetHeight() return rawget(self,'height') or 140 end
function methods:SetSize(w,h) self.width=w; self.height=h end
function methods:SetWidth(w) self.width=w end
function methods:SetHeight(h) self.height=h end
function methods:GetText() return rawget(self,'text') end
function methods:SetOwner(owner) self.owner=owner end
function methods:GetEffectiveScale() return 1 end
function methods:GetFont() return 'native-blizzard-font',11,'' end
function methods:SetFont(face,size,flags) self.fontSize=size end
function methods:SetTexCoord(...) self.texCoords={...} end
function methods:SetTexture(path) self.texturePath=path; return true end
local function make()
 return setmetatable({scripts={},attributes={}}, {__index=function(self,k)
  if methods[k] then return methods[k] end
  if k=='CreateFontString' or k=='CreateTexture' or k=='CreateLine' then return function() return make() end end
  return function() end
 end})
end
UIParent=make()
Minimap=make()
GameTooltip=make(); GameTooltip:Hide()
createdButtons={}
function CreateFrame(kind,name,parent,template)
 local f=make(); f.parent=parent; f.secure=template and template:find('SecureActionButtonTemplate')~=nil or false
 if template=='UIPanelScrollBarTemplate' then f.ScrollUpButton=make(); f.ScrollDownButton=make() end
 if kind=='Button' then createdButtons[#createdButtons+1]=f end
 return f
end
F = {}
''')
toc = (root / "ForeverRested.toc").read_text()
files = [line.strip() for line in toc.splitlines() if line.strip().endswith(".lua")]
for name in files:
    lua.execute("assert(loadstring(...))('ForeverRested', F)", (root / name).read_text())
lua.execute("assert(loadstring(...))('ForeverRested', F)", (root / 'tests/fixtures/GnomeDwarf_01_10.lua').read_text())
lua.execute(r'''
F.LoadDatabase(); F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create()
F.GuideLibrary:Select('gnome-dwarf-slice-v1'); F.Refresh()
assert(F.db.step==2, 'accepted pickup must advance')
assert(F.db.bindings[1]==101 and F.db.bindings[2]==102 and F.db.bindings[3]==103)
assert(F.SecureTarget.current=='Frostmane Troll Whelp')
assert(F.SecureTarget.button.attributes.macrotext=='/cleartarget\n/targetexact Frostmane Troll Whelp\n/tm [@target,exists,harm,nodead] !8')
assert(F.SecureTarget.button.marker==8 and F.SecureTarget.button.markerIcon.texCoords[1]==.75)
assert(math.abs(F.Navigation.distance-100)<.0001)
assert(math.abs(F.Navigation.angle)<.0001, 'north must point up at facing zero')
for i=1,#F.Guide.steps do F.GuideEngine:Move(1) end
assert(F.db.step==#F.Guide.steps)
SlashCmdList.FOREVERRESTED('auto')
assert(F.db.step==2, 'Auto must recover the live objective after browsing to the end')
F.GuideEngine:Move(1,true)
F.GuideEngine:Move(1)
F.GuideEngine:ResumeAuto()
assert(F.db.step==3, 'Auto respects explicitly skipped objectives but stops at pending turnin')
F.db.skipped={}
F.GuideEngine:ResumeAuto()
assert(F.db.step==2)
combat=true
F.UI:Toggle()
assert(not F.UI.frame:IsShown() and F.db.hidden, 'combat permits closing the guide window')
F.UI:Toggle()
assert(not F.UI.frame:IsShown() and F.db.hidden, 'combat blocks reopening the guide window')
F.SecureTarget:Update('Other Mob')
assert(F.SecureTarget.current=='Frostmane Troll Whelp' and F.SecureTarget.pending)
combat=false
F.UI:Toggle()
assert(F.UI.frame:IsShown() and not F.db.hidden, 'guide window can reopen after combat')
F.SecureTarget:UpdateTasks(F.SecureTarget.desiredTargets)
assert(F.SecureTarget.current=='Other Mob')
F.SecureTarget:Update('Bad\n/attack')
assert(F.SecureTarget.current==nil and F.SecureTarget.button.attributes.macrotext=='')
F.SecureTarget.button.scripts.OnDragStart()
assert(F.SecureTarget.dragging)
combat=true
F.SecureTarget.button.scripts.OnDragStop()
assert(F.SecureTarget.stopPending and F.db.targetPosition==nil)
combat=false
F.SecureTarget:Update(nil)
assert(not F.SecureTarget.dragging and F.db.targetPosition.x==0)
combat=true
F.SecureTarget.button.scripts.OnDragStart()
assert(not F.SecureTarget.dragging)
combat=false
F.Arrow.frame.scripts.OnDragStop()
assert(F.db.arrowPosition.x==0)
objectives[101][1].finished=true
F.Refresh(); assert(F.db.step==3, 'finished objective must advance to turnin')
live[1]=nil; live[1]=live[3]; live[3]=nil
F.Refresh(); assert(F.db.step==3, 'quest removal alone is not turnin evidence')
F.GuideEngine:Move(100)
F.GuideEngine:ResumeAuto()
assert(F.db.step==1, 'Auto returns to pickup when a quest is absent without turnin evidence')
F.db.completed[101]=true
F.Refresh(); assert(F.db.step==5, 'turnin evidence advances and completed objective 2 advances')
F.GuideEngine:Move(-1); F.Refresh(); assert(F.db.step==4, 'Back holds completed step')
F.GuideEngine.manualHold=nil; F.Refresh(); assert(F.db.step==5)
F.GuideEngine:Move(100)
F.GuideEngine:ResumeAuto()
assert(F.db.step==5, 'Auto returns to a pending turnin after previous quests are finished')
F.db.completed[102]=true; F.db.completed[103]=true
F.GuideEngine:ResumeAuto()
assert(F.db.step==#F.Guide.steps, 'fully finished guide stays at the final note')
-- Grouped steps use ALL required tasks; optional alongside tasks never block.
F.db.completed={}
live={
 {questID=101,title='The Troll Cave',level=6,isComplete=false},
 {questID=102,title="A Refugee's Quandary",level=5,isComplete=false},
 {questID=103,title='Bring Back the Mug',level=5,isComplete=false},
}
objectives[101][1].finished=false
objectives[102][1]={text='Ice Troll: 2/4',type='monster',finished=false}
objectives[103][1]={text='Snow Wolf: 0/2',type='monster',finished=false}
C_QuestLog.IsComplete=function() return false end
F.GuideLibrary:Select('gnome-dwarf-concurrent-v1')
assert(F.db.step==2, 'accepted grouped pickups advance to concurrent objectives')
local targets=F.GuideEngine:Targets()
assert(#targets==3, 'active targets include required and alongside kill objectives')
assert(F.SecureTarget.buttons[2].mob=='Ice Troll' and F.SecureTarget.buttons[3].mob=='Snow Wolf')
assert(F.SecureTarget.buttons[1].marker==8 and F.SecureTarget.buttons[2].marker==7 and F.SecureTarget.buttons[3].marker==6)
assert(F.SecureTarget.buttons[2].attributes.macrotext:find('!7',1,true))
combat=true
F.SecureTarget:UpdateTasks({{mob='Replacement A'},{mob='Replacement B'}})
assert(F.SecureTarget.buttons[2].mob=='Ice Troll', 'entire secure pool remains unchanged in combat')
combat=false
F.SecureTarget:UpdateTasks(F.SecureTarget.desiredTargets)
assert(F.SecureTarget.buttons[2].mob=='Replacement B' and not F.SecureTarget.buttons[3]:IsShown())
F.Refresh()
objectives[101][1].finished=true
F.Refresh(); assert(F.db.step==2, 'one finished task cannot complete a group')
objectives[102][1].finished=true
F.Refresh(); assert(F.db.step==3, 'group advances while optional side objective remains unfinished')
F.GuideEngine:Move(100); F.GuideEngine:ResumeAuto()
assert(F.db.step==3, 'Auto finds the first incomplete grouped step')
C_QuestLog.IsComplete=function() return true end
F.Refresh(); assert(F.db.step==4, 'all whole quests complete advances to grouped turnins')
F.db.completed[101]=true; F.db.completed[102]=true
F.Refresh(); assert(F.db.step==4, 'grouped turnin waits for every required quest')
F.db.completed[103]=true
F.Refresh(); assert(F.db.step==5)
F.GuideLibrary:Select('gnome-dwarf-slice-v1')
F.GuideLibrary:Select('gnome-dwarf-concurrent-v1')
assert(F.db.step==5, 'each guide keeps its saved position')
F.Minimap:ToggleMenu(); assert(F.Minimap.menu:IsShown())
assert(F.Minimap.button, 'native minimap launcher is created when minimap exists')
assert(F.GuideLibrary:BracketIndex(9)==1 and F.GuideLibrary:BracketIndex(10)==2)
assert(F.GuideLibrary:BracketIndex(60)==6)
F.Minimap.bracketIndex=2; F.Minimap:RefreshGuides()
assert(not F.Minimap.guideButtons['gnome-dwarf-slice-v1']:IsShown())
assert(#F.GuideLibrary:GuidesForBracket(2)==4)
assert(F.Minimap.guideButtons['alliance-westfall-10-20']:IsShown())
F.Minimap.bracketIndex=1; F.Minimap:RefreshGuides()
assert(F.Minimap.guideButtons['gnome-dwarf-slice-v1']:IsShown())
F.Minimap.guideButtons['gnome-dwarf-slice-v1'].scripts.OnClick()
assert(F.db.guideID=='gnome-dwarf-slice-v1' and not F.Minimap.menu:IsShown())
-- Reproduce the reported loot objective: count is before the item name, and
-- native waypoints are absent. Do not mistake the item ID for a creature ID.
assert(F.Tracker.rows[1].text.fontSize==14 and F.Tracker.rows[1].text.fontSize==14)
F.db.bindings={95212,102,103}; F.db.completed={}; F.db.skipped={}; F.db.step=2
live={{questID=95212,title='Never Saddle on Quality',level=10,isComplete=false}}
objectives[95212]={{text='0/6 Pristine Leopard Pelt',type='item',objectID=267414,numFulfilled=0,numRequired=6,finished=false}}
C_QuestLog.IsComplete=function() return false end
C_QuestLog.GetNextWaypoint=nil
C_Map.GetMapInfo=function(map) return {name=map==1426 and 'Dun Morogh' or 'Other Zone',parentMapID=0} end
F.Refresh()
assert(F.SecureTarget.current=='Elder Snow Leopard', 'loot-source mapping creates leopard target')
assert(F.GuideEngine:TaskState(F.Guide.steps[2])=='ongoing')
local turnin=F.Guide.steps[3]
assert(F.GuideEngine:TaskState(turnin)=='notready')
local originalIsComplete=C_QuestLog.IsComplete
C_QuestLog.IsComplete=function() return true end; F.QuestLog:Refresh()
assert(F.GuideEngine:TaskState(turnin)=='ready', 'ready to turn in is distinct from rewarded')
assert(F.GuideEngine:StepState(3)=='ready')
C_QuestLog.IsComplete=originalIsComplete; F.QuestLog:Refresh()
assert(F.SecureTarget.button.attributes.macrotext=='/cleartarget\n/targetexact Elder Snow Leopard\n/tm [@target,exists,harm,nodead] !8')
-- Model native command semantics, independent of the addon macro builder.
local function clickNativeMacro(macro, nearby, selected)
    local marks={}
    for line in macro:gmatch('[^\n]+') do
        if line=='/cleartarget' then selected=nil
        elseif line:match('^/targetexact ') then
            local name=line:sub(14)
            for _, unit in ipairs(nearby) do if unit.name==name then selected=unit; break end end
        elseif line:match('^/tm ') then
            assert(line:find('[@target,exists,harm,nodead]',1,true))
            if selected and selected.hostile and not selected.dead then
                selected.marker=tonumber(line:match('!(%d+)$')); marks[#marks+1]=selected.name
            end
        else error('unexpected macro command') end
    end
    return selected,marks
end
local leopard={name='Elder Snow Leopard',hostile=true}
local selected,marks=clickNativeMacro(F.SecureTarget.button.attributes.macrotext,{leopard},nil)
assert(selected==leopard and leopard.marker==8 and #marks==1)
clickNativeMacro(F.SecureTarget.button.attributes.macrotext,{leopard},leopard)
assert(leopard.marker==8, 'repeated clicks keep skull instead of toggling it off')
local unrelated={name='Unrelated Creature',hostile=true}
selected,marks=clickNativeMacro(F.SecureTarget.button.attributes.macrotext,{},unrelated)
assert(selected==nil and #marks==0 and not unrelated.marker, 'no matching mob must not mark an old target')
local corpse={name='Elder Snow Leopard',hostile=true,dead=true}
selected,marks=clickNativeMacro(F.SecureTarget.button.attributes.macrotext,{corpse},nil)
assert(#marks==0 and not corpse.marker, 'dead creatures are not marked')
local previousAlias=SLASH_TARGET_MARKER1; SLASH_TARGET_MARKER1=nil
assert(F.SecureTarget:MarkerCommand()==nil, 'unsupported native command fails closed')
SLASH_TARGET_MARKER1=previousAlias
assert(F.Arrow.frame.parent==UIParent and F.SecureTarget.frame.parent==UIParent, 'navigation and targets are independent of the guide window')
assert(F.Arrow.artSource:find('BronzeArrow.tga',1,true) and F.Arrow.texture, 'custom bronze arrow is selected before native fallback')
F.Minimap.button.scripts.OnClick(F.Minimap.button, 'LeftButton')
assert(F.db.hidden and not F.UI.frame:IsShown() and not F.Arrow.frame:IsShown(), 'minimap toggle hides the guide and arrow immediately')
F.UI:NavigationTick(); F.Arrow:Animate(1/60)
assert(not F.Arrow.frame:IsShown(), 'navigation updates keep the arrow hidden')
F.Minimap.button.scripts.OnClick(F.Minimap.button, 'LeftButton')
assert(not F.db.hidden and F.UI.frame:IsShown() and F.Arrow.frame:IsShown() and F.Arrow.yards.text:match('yd$'), 'minimap toggle restores the guide and navigation arrow')
function UnitName(unit) if unit=='target' then return 'Elder Snow Leopard' end end
combat=true; F.SecureTarget:UpdateSelection()
assert(rawget(F.SecureTarget.button,'selectedMark')==nil, 'target icon must not show a selected X')
UnitName=function() return 'Unrelated Creature' end
F.SecureTarget:UpdateSelection(); assert(rawget(F.SecureTarget.button,'selectedMark')==nil)
combat=false
F.UI.frame:SetSize(600,900); F.UI:Layout(600,900); F.UI:SaveWindowGeometry()
assert(F.db.windowSize.width==600 and F.db.windowSize.height==900)
assert(F.Tracker.rows[1]:GetWidth()==556 and F.Tracker.rows[1].body:GetWidth()>300)
F.UI:ToggleOptions(); assert(F.UI.options:IsShown())
F.UI:SetFontSize(18)
assert(F.db.fontSize==18 and F.Tracker.rows[1].text.fontSize==18 and F.Arrow.yards.fontSize==18)
assert(F.Tracker.rowHeight==66 and F.Tracker.visibleRows>=1)
F.UI:SetFontSize(100); assert(F.db.fontSize==20)
F.UI:SetFontSize(1); assert(F.db.fontSize==11)
F.UI:SetFontSize(14)
F.UI.frame:SetSize(400,520); F.UI:Layout(400,520)
assert(F.Tracker.visibleRows>=1 and not F.Tracker.rows[F.Tracker.visibleRows+1]:IsShown(), 'small window clips rows and keeps scrolling available')
F.UI.frame:SetSize(400,742); F.UI:Layout(400,742)
-- A tooltip is never shown on initial enter or a short hover; leaving, changing
-- owners, and hidden buttons cancel the pending delay. All buttons have help.
for _, button in ipairs(createdButtons) do assert(button.foreverTooltip, 'every addon button must have delayed help') end
local helpButton=F.UI.resizeGrip
helpButton.scripts.OnEnter(helpButton)
assert(not GameTooltip:IsShown())
F.Tooltips:Tick(1.9); assert(not GameTooltip:IsShown())
F.Tooltips:Tick(.11); assert(GameTooltip:IsShown() and GameTooltip.owner==helpButton)
helpButton.scripts.OnLeave(helpButton); assert(not GameTooltip:IsShown())
helpButton.scripts.OnEnter(helpButton); F.Tooltips:Tick(1)
helpButton.scripts.OnLeave(helpButton); F.Tooltips:Tick(5)
assert(not GameTooltip:IsShown(), 'leaving before 2 seconds cancels help')
helpButton.scripts.OnEnter(helpButton); F.Tooltips:Tick(2)
F.Minimap.button.scripts.OnEnter(F.Minimap.button)
assert(GameTooltip.owner==F.Minimap.button and GameTooltip:IsShown(), 'minimap launcher help appears immediately')
assert(GameTooltip.text=='Forever Rested' and not F.Tooltips.pending)
F.Minimap.button.scripts.OnLeave(F.Minimap.button)
helpButton.scripts.OnEnter(helpButton); helpButton:Hide(); F.Tooltips:Tick(4)
assert(not GameTooltip:IsShown(), 'hidden buttons cannot produce a delayed tooltip')
helpButton:Show()
assert(F.Navigation.targetMap==1426 and F.Navigation.tx==.764 and F.Navigation.ty==.614)
assert(F.Navigation.source=='Hunting area (approx.)' and F.Navigation.angle~=nil and F.Arrow.frame:IsShown())
objectives[95212][1].numFulfilled=2; objectives[95212][1].text='2/6 Pristine Leopard Pelt'
F.Refresh(); assert(F.SecureTarget.button.progress=='2/6 Pristine Leopard Pelt')
assert(F.Tracker.rows[1].body.text:find('Hunt',1,true) and F.Tracker.rows[1].body.text:find('2/6 Pristine Leopard Pelt',1,true), 'current action and live progress are readable together')
C_Map.GetMapInfo=function() return {name='Unrelated map',parentMapID=0} end
F.UI:NavigationTick(); assert(F.Navigation.angle==nil, 'wrong map must never use Dun Morogh percentages')
C_Map.GetMapInfo=function(map) return {name=map==1426 and 'Dun Morogh' or 'Other Zone',parentMapID=0} end
objectives[95212][1].finished=true
F.Refresh(); assert(F.db.step==3 and F.SecureTarget.current==nil)
assert(F.Tracker.rows[1].body.text:find('ActiveQuestIcon',1,true) and F.Tracker.rows[1].body.text:find('Turn in',1,true))
assert(F.Tracker.rows[1].body.text:find('GossipGossipIcon',1,true) and F.Tracker.rows[1].body.text:find('Rudra',1,true), 'turnin shows the speech icon and destination NPC')
local upcoming=F.GuideEngine:NextRelevantIndex()
assert(upcoming and F.Tracker.rows[2].text.text:find(tostring(upcoming),1,true))
F.db.skipped[upcoming]=true
assert(F.GuideEngine:NextRelevantIndex()~=upcoming,'next action skips explicitly skipped steps')
F.db.skipped[upcoming]=nil
assert(F.Navigation.targetMap==1426 and F.Navigation.tx==.63 and F.Navigation.ty==.498,
 'ready turnin must navigate to Rudra, not to the completed hunting objective')
C_QuestLog.GetNextWaypoint=nil; F.UI:NavigationTick()
assert(F.Navigation.angle~=nil and F.Arrow.frame:IsShown(),'sourced quest giver keeps turnin navigation active without a native waypoint')
C_Map=nil; F.UI:NavigationTick(); assert(F.Navigation.distance==nil)
-- Legacy quest API fallback, with no modern quest namespace.
C_QuestLog=nil
function GetNumQuestLogEntries() return 1 end
function GetQuestLogTitle() return 'Legacy Quest',2,0,false,false,0,0,501 end
function GetNumQuestLeaderBoards() return 1 end
function GetQuestLogLeaderBoard() return 'Legacy Monster: 2/3','monster',false end
F.QuestLog:Refresh()
assert(F.QuestLog.byID[501].objectives[1].text=='Legacy Monster: 2/3')
''')
print(f"PASS: {len(files)} Lua files compile in Lua 5.1; 3-second tooltips on every button, quest status distinctions, marker safety, independent arrow, resizing/fonts, grouped progression and API fallbacks.")
