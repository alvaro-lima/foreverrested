"""Headless integration checks for completion, dependency recovery and class unlocks."""
from pathlib import Path
from lupa.lua51 import LuaRuntime

root = Path(__file__).resolve().parents[1]
lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute('''
unpack=unpack or table.unpack
F={UI={},Tracker={offset=0},QuestData={}}
function F.QuestData:ObserveLog() end
function F.QuestData:Initialize() end
function F.Tracker:ShowCurrentAtTop() end
function F.UI:Refresh() end
history={}; live={}; profile={class='MAGE',race='Human',level=8}
function UnitClass() return profile.class,profile.class end
function UnitRace() return profile.race,profile.race end
function UnitLevel() return profile.level end
C_QuestLog={
 GetNumQuestLogEntries=function() return #live end,
 GetInfo=function(i) return live[i] end,
 GetQuestObjectives=function() return {} end,
 IsQuestFlaggedCompleted=function(id) return history[id] or false end,
}
''')
files = ['Core.lua','GuideLibrary.lua','Guides/AllianceQuestData.lua','Guides/Alliance_20_30_QuestData.lua','Data/ClassicQuestPolicy.lua',
         'Data/ForeverUnlockFacts.lua','Data/ForeverQuestPolicy.lua',
         'GuideDraft.lua','Travel.lua','tests/fixtures/GnomeDwarf_01_10.lua','Guides/Alliance_01_10.lua',
         'Guides/Alliance_10_20.lua','Guides/Alliance_20_30.lua','Guides/Zephras_10_14.lua','QuestLog.lua',
         'GuideEngine.lua','QuestPolicy.lua','AutoQuest.lua','Database.lua']
for name in files:
    lua.execute("assert(loadstring(...))('ForeverRested', F)", (root/name).read_text(encoding='utf-8'))
lua.execute('''
F.LoadDatabase()
local E,P=F.GuideEngine,F.QuestPolicy
local function fixture(steps,data,saved)
 F.Guide={id='fixture',revision=1,minLevel=1,steps=steps,questData=data or {}}
 F.GuideLibrary.guides.fixture=F.Guide; F.db.guideID='fixture'
 F.db.completed={}; F.db.bindings={}
 F.GuideLibrary:ApplyState(F.Guide,saved or {})
 F.Refresh()
end
local function position(key)
 for i,s in ipairs(F.Guide.steps) do if s.id==key then return i end end
end
local function currentID() return F.Guide.steps[F.db.step].id end
history={[100101]=true,[100103]=true}
fixture({{id='entry',type='note'}, {id='done',type='turnin',questID=100101},
 {id='old',type='objective',questID=100102}, {id='current',type='pickup',questID=100104},
 {id='later-done',type='turnin',questID=100103}, {id='exit',type='note'}},
 {[100101]={level=2},[100102]={level=3},[100103]={level=9},[100104]={level=8}},
 {step=6,skipped={[2]=true,[5]=true}})
assert(currentID()=='current')
assert(E:StepState(position('done'))=='complete' and E:StepState(position('later-done'))=='complete')
assert(E:StepState(position('entry'))=='skipped' and E:StepState(position('old'))=='skipped')
assert(F.db.completed[100101] and F.db.completed[100103])
-- One-shot reconciliation respects a manual restart.
F.db.skipped[1]=nil; F.db.step=1
E:CatchUpOnLoad(); assert(F.db.step==1 and not F.db.skipped[1])
fixture({{id='old',type='note'},{id='checkpoint',type='grind',targetLevel=8},
 {id='exit',type='note'}})
assert(currentID()=='exit' and F.db.skipped[position('old')])
-- Missing and skipped ancestors are inserted in prerequisite order.
history={}
P.forever[100104]={prerequisites={100102}}
P.forever[100102]={prerequisites={100105}}
fixture({{id='ancestor',type='turnin',questID=100105},
 {id='prior',type='turnin',questID=100102},{id='ordinary',type='note'},
 {id='current',type='pickup',questID=100104},{id='exit',type='note'}},
 {[100104]={level=8}}, {skipped={[1]=true,[2]=true}})
assert(currentID()=='catchup:100105:pickup')
assert(position('catchup:100105:turnin')<position('catchup:100102:pickup'))
assert(not F.db.skipped[position('ancestor')] and not F.db.skipped[position('prior')])
assert(F.db.skipped[position('ordinary')])
assert(F.AutoQuest:Allowed(100105,'pickup') and F.AutoQuest:Allowed(100102,'turnin'))
local n=#F.Guide.steps
E.catchUpPending=true; F.Refresh(); assert(#F.Guide.steps==n,'reloading must not duplicate recovery steps')
-- Completing an ancestor removes its recovery actions on the next load.
history[100105]=true; E.catchUpPending=true; F.Refresh()
assert(not position('catchup:100105:pickup') and currentID()=='catchup:100102:pickup')
-- An already accepted descendant needs no recovery of its acceptance chain.
live={{questID=100104,title='Current quest'}}
E.catchUpPending=true; F.Refresh()
assert(not P.requiredQuests[100102] and not P.requiredQuests[100105])
live={}
-- ALL dependencies retain every requirement; ANY picks one eligible branch.
P.forever[100104]={prerequisites={100102,100106},prerequisitesAny={100107,100108}}
P.forever[100107]={classes={'WARRIOR'}}
fixture({{id='current',type='pickup',questID=100104},{id='exit',type='note'}}, {[100104]={level=8}})
assert(P.requiredQuests[100102] and P.requiredQuests[100106] and P.requiredQuests[100108])
assert(not P.requiredQuests[100107])
history[100107]=true
E.catchUpPending=true; F.Refresh(); assert(not P.requiredQuests[100108],'any completed alternative satisfies the branch')
-- Active parents are accepted and kept active, never turned in prematurely.
P.forever[100104]={parentQuest=100109}
fixture({{id='current',type='pickup',questID=100104},{id='exit',type='note'}}, {[100104]={level=8}})
assert(position('catchup:100109:pickup') and not position('catchup:100109:turnin'))
live={{questID=100109,title='Parent'}}
E.catchUpPending=true; F.Refresh(); assert(not position('catchup:100109:pickup'))
live={}
-- Future level requirements do not force unavailable prerequisites now.
P.forever[100104]={minLevel=20,prerequisites={100110}}
fixture({{id='current',type='pickup',questID=100104},{id='exit',type='note'}}, {[100104]={level=8}})
assert(not P.requiredQuests[100110] and not position('catchup:review'))
-- Cycle errors are visible, rather than silently pretending the chain is done.
history={}
P.forever[100104]={prerequisites={100102}}
P.forever[100102]={prerequisites={100105}}
P.forever[100105]={prerequisites={100102}}
fixture({{id='current',type='pickup',questID=100104},{id='exit',type='note'}}, {[100104]={level=8}})
assert(position('catchup:review') and #P.issues>0)
P.forever={}
-- Test guides retain arbitrary live bindings and receive no Vanilla recovery.
profile={class='WARLOCK',race='Human',level=20}; history={}
F.db.completed={}; F.GuideLibrary:Select('gnome-dwarf-slice-v1')
assert(#F.Guide.steps==8 and not F.Guide.steps[1].recovery)
-- Every applicable unlock group is recovered, including missing quest metadata,
-- race variants, and full upstream prerequisite ancestry.
local runs=0
for _,unlock in ipairs(P.unlocks) do
 local race=unlock.races==8 and 'NightElf' or unlock.races==4 and 'Dwarf'
     or unlock.races==64 and 'Gnome' or unlock.races==68 and 'Gnome' or 'Human'
 profile={class=unlock.class,race=race,level=unlock.level}; history={}; live={}
 fixture({{id='route',type='note'},{id='exit',type='note'}})
 local chosen=false
 for _,id in ipairs(unlock.terminals) do if P.requiredQuests[id] then chosen=true end end
 assert(chosen,'missing unlock: '..unlock.key)
 assert(#P.issues==0,'invalid unlock prerequisite data: '..unlock.key)
 local seen={}
 for i,s in ipairs(F.Guide.steps) do
  assert(not seen[s.id],'duplicate stable step ID'); seen[s.id]=true
  if s.recovery then
   assert(E:Metadata(s.questID) and E:Metadata(s.questID).title)
   assert(F.AutoQuest:Allowed(s.questID,s.type) or s.type=='objective')
   assert(not F.db.skipped[i])
  end
 end
 -- One terminal completion satisfies all equivalent variants of this milestone.
 for _,id in ipairs(unlock.terminals) do history[id]=true; break end
 E.catchUpPending=true; F.Refresh()
 for _,id in ipairs(unlock.terminals) do assert(not P.requiredQuests[id],'completed unlock must not reappear') end
 runs=runs+1
end
-- Vanilla has no ability unlock quest for mages by 20; gear stays optional.
profile={class='MAGE',race='Human',level=20}; history={}
fixture({{id='route',type='note'},{id='exit',type='note'}})
assert(next(P.requiredQuests)==nil)
-- Forever can replace or disable a whole milestone without changing the source.
profile={class='HUNTER',race='Dwarf',level=10}; history={}
P.foreverUnlocks['hunter-dwarf-pets']=false
fixture({{id='route',type='note'},{id='exit',type='note'}})
assert(next(P.requiredQuests)==nil)
P.foreverUnlocks={}
-- New Forever classes/races can add milestones without a Vanilla counterpart.
P.foreverUnlocks['forever-earth']={class='SHAMAN',raceTokens={'Skyborne'},level=4,
 terminals={100777},reason='Earth totem'}
P.forever[100777]={classes={'SHAMAN'},minLevel=4,requiredRaces=2^32}
profile={class='SHAMAN',race='Skyborne',level=10}
fixture({{id='route',type='note'},{id='exit',type='note'}})
assert(P.requiredQuests[100777] and currentID()=='catchup:100777:pickup')
P.foreverUnlocks={}; P.forever={}
-- Manual skips persist by stable ID across recovery rebuilding and selection.
profile={class='HUNTER',race='Dwarf',level=15}; history={}
fixture({{id='route',type='note'},{id='exit',type='note'}})
local skippedID=currentID()
E.selectedStep=nil; E:Move(1,true)
assert(F.db.manualSkippedSteps[skippedID] and F.db.skipped[position(skippedID)])
F.GuideLibrary:SaveCurrent(); F.GuideLibrary:Select('fixture')
assert(E:StepState(position(skippedID))=='skipped')
for i,s in ipairs(F.Guide.steps) do
 if s.recovery and s.id~=skippedID then assert(not F.db.skipped[i],'critical actions cannot be auto-skipped') end
end
E:ResetFrom(position(skippedID))
assert(F.db.manualSkippedSteps[skippedID] and not F.db.skipped[position(skippedID)],
 'From clears the visible skip while retaining its saved history')
-- The screenshot's shaman case has concrete Earth/Fire actions, no generic
-- protected class paragraph; completed Earth unlocks leave just the Fire chain.
P.forever=F.ForeverQuestPolicy.records; P.foreverUnlocks=F.ForeverQuestPolicy.unlocks
profile={class='SHAMAN',race='Dwarf',level=15}; history={[94375]=true}
fixture({{id='class',type='note',classAdvice=true,confirmOnNext=true},{id='exit',type='note'}})
assert(currentID()=='catchup:94449:pickup')
assert(not P.requiredQuests[94373] and P.requiredQuests[94468])
assert(F.db.skipped[position('class')])
for _,s in ipairs(F.Guide.steps) do
 if s.recovery then assert(s.critical and not s.tasks and not s.note) end
end
P.forever={}; P.foreverUnlocks={}
-- Unknown Forever races retain class reviews instead of forcing Vanilla IDs.
profile={class='HUNTER',race='Skyborne',level=15}
fixture({{id='class',type='note',classAdvice=true,confirmOnNext=true},{id='exit',type='note'}})
assert(currentID()=='exit' and next(P.requiredQuests)==nil)
-- Login level unavailability defers the one-shot pass.
profile.level=0
F.GuideLibrary:ApplyState(F.Guide,{})
F.Refresh(); assert(E.catchUpPending)
profile.level=15; F.Refresh(); assert(not E.catchUpPending)
-- Sweep every installed route across every Vanilla Alliance class/race profile.
local profiles={{'WARRIOR','Human'},{'WARRIOR','Dwarf'},{'WARRIOR','Gnome'},
 {'WARRIOR','NightElf'},{'PALADIN','Human'},{'PALADIN','Dwarf'},
 {'HUNTER','Dwarf'},{'HUNTER','NightElf'},{'DRUID','NightElf'},
 {'WARLOCK','Human'},{'WARLOCK','Gnome'},{'ROGUE','Human'},{'ROGUE','Gnome'},
 {'PRIEST','Human'},{'PRIEST','Dwarf'},{'PRIEST','NightElf'},{'MAGE','Human'}}
local scenarios=0
for _,p in ipairs(profiles) do
 for _,level in ipairs({1,10,14,16,20}) do
  profile={class=p[1],race=p[2],level=level}
  for _,gID in ipairs(F.GuideLibrary.order) do
   if F.GuideLibrary.guides[gID].status~='test' then
    F.db.completed={}; history={}; live={}
    F.GuideLibrary:Select(gID)
    assert(F.db.step>=1 and F.db.step<=#F.Guide.steps)
    local seen={}
    for i,s in ipairs(F.Guide.steps) do
     assert(not seen[s.id]); seen[s.id]=true
     if s.recovery then assert(not F.db.skipped[i]) end
    end
    local count=#F.Guide.steps
    F.GuideLibrary:SaveCurrent(); F.GuideLibrary:Select(gID)
    assert(#F.Guide.steps==count,'guide switch duplicated recovery actions')
    scenarios=scenarios+1
   end
  end
 end
end
print('PASS: '..runs..' unlock groups, '..scenarios..' installed-guide scenarios, completion, alternatives, active parents, overrides and repeated loading')
''')
for path in root.rglob('*.lua'):
    lua.execute('assert(loadstring(...))',path.read_text(encoding='utf-8'))
print('PASS: all addon Lua compiles with Lua 5.1')
lua.execute("assert(loadstring(...))('ForeverRested', F)", (root/'UI.lua').read_text(encoding='utf-8'))
lua.execute("assert(F.UI:ActionBody({type='pickup',questID=1642,recovery=true}):find('item #6775',1,true))")
print('PASS: item-start recovery instructions')
