"""Objective locations, remote collapse, quest tooltips and synchronized scrolling."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase();F.UI:Create()
local Q=F.ObjectiveQueue
GetRealZoneText=function() return 'Wetlands' end
F.Guide={title='A mixed route',steps={
 {id='remote',type='objective',questID=100101},
 {id='near',type='objective',questID=100102},
 {id='mixed',type='objective',questID=100103}},questData={
 [100101]={locations={{role='requirement',zone='Redridge Mountains'}}},
 [100102]={locations={{role='requirement',zone='Wetlands'}}},
 [100103]={locations={{role='sourcerequirement',zone='Wetlands',item='Cask'},
                    {role='sourcerequirement',zone='Redridge Mountains',item='Bottle'}}}}}
F.QuestLog.list={
 {id=100101,title='Remote quest',objectives={{text='Remote: 0/5'}}},
 {id=100102,title='Nearby quest',objectives={{text='Nearby: 0/4'}}},
 {id=100103,title='Mixed quest',objectives={{text='Cask: 0/1'},{text='Bottle: 0/1'}}}}
F.db.step=2;F.db.completed={};F.db.manualSkippedSteps={};F.db.skipped={}
C_QuestLog.IsQuestFlaggedCompleted=function() return false end
local entries=Q:Build()
assert(entries[3].zone=='Wetlands' and entries[4].zone=='Redridge Mountains','group each objective by its actual location')
Q.otherAreasExpanded=false;Q:Refresh()
for _,row in ipairs(Q.rows) do row.SetParent=function(self,parent) self.parent=parent end end
assert(Q.renderedText:find('Nearby quest') and not Q.renderedText:find('Remote quest'),'remote quests hidden initially')
assert(Q.renderedText:find('Upcoming objectives %(2 quests%)'),'remote count counts unique quests')
assert(not Q.renderedText:find('A mixed route',1,true),'guide title stays out of visible list')
local toggle
for _,row in ipairs(Q.rows) do if row:IsShown() and row.item.toggle then toggle=row end end
assert(toggle);toggle.scripts.OnClick(toggle)
assert(Q.otherAreasExpanded and Q.renderedText:find('Remote quest'))
local tooltip={}
GameTooltip.AddLine=function(_,line) tooltip[#tooltip+1]=line end
Q.rows[2].scripts.OnEnter(Q.rows[2])
assert(table.concat(tooltip,'\n'):find('A mixed route',1,true),'quest hover shows source guide')
Q.frame:SetHeight(60);Q:Refresh()
assert(Q.maxOffset>0 and Q.scrollbar:IsShown(),'overflow shows scrollbar')
Q.scroll.scripts.OnMouseWheel(Q.scroll,-1);assert(Q.offset>0,'wheel moves content')
Q.scrollbar.scripts.OnValueChanged(Q.scrollbar,Q.maxOffset);assert(Q.offset==Q.maxOffset,'drag moves content')
Q:SetOffset(100000);assert(Q.offset==Q.maxOffset,'scroll offset clamps')
Q.frame:SetHeight(5000);Q:Refresh()
assert(not Q.scrollbar:IsShown() and Q.offset==0,'resize removes scrollbar and clamps offset')
toggle.scripts.OnClick(toggle);assert(not Q.otherAreasExpanded,'collapse works')
assert(Q.scroll:GetHeight()==Q.content:GetHeight(),'short section uses its content height rather than leaving a gap')
assert(not Q.otherScroll:IsShown() and not Q.otherScrollbar:IsShown(),'collapsed section hides its body and scrollbar')
assert(Q.rows[1].parent==Q.frame and Q.rows[2].parent==Q.content,'header remains outside the scrolling objective body')
assert(Q.rows[1].item.header and Q.rows[1].sectionBar:IsShown(),'current zone has a styled section bar')
Q.rows[1].scripts.OnClick(Q.rows[1]);assert(Q.currentZoneCollapsed,'current section can collapse')
assert(not Q.renderedText:find('Nearby quest'),'collapsed current section hides its quests')
''')
print('PASS: planned current priority, per-objective zones, remote collapse, guide tooltips and scrollbar controls')
