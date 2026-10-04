"""Recommendation and linked-route catch-up from live quest progress."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local L,P,E=F.GuideLibrary,F.QuestPolicy,F.GuideEngine
UnitLevel=function() return 18 end
UnitRace=function() return 'Human','Human' end
C_Map.GetMapInfo=function() return {name='Stormwind City'} end
F.QuestLog.byID={}
local id,reason=L:Recommended()
assert(id=='alliance-redridge-human-15-20','level 18 starts in appropriate mainland section')
assert(reason:find('level 18'))
UnitRace=function() return 'Night Elf','NightElf' end
C_Map.GetMapInfo=function() return {name='Darnassus'} end
assert(L:Recommended()=='alliance-darkshore-17-20','race path fallback uses current level')
UnitLevel=function() return 31 end
assert(L:Recommended()==nil,'no outleveled recommendation')
UnitLevel=function() return 18 end
P.unlocks={};P.foreverUnlocks={}
P.forever[100001]={prerequisites={100002}}
P.forever[100002]={prerequisites={100003}}
P.forever[100003]={}
local g={id='catchup-linked-test',title='Catch-up fixture',status='draft',faction='Alliance',routeGroup='test-catchup',minLevel=17,maxLevel=20,
 steps={{id='entry',type='note',confirmOnNext=true,text='Route'},
 {id='next',type='pickup',questID=100001}},
 questData={[100001]={title='Next'},[100002]={title='Middle'},[100003]={title='First'}}}
L:Register(g);F.Guide=g;F.db.guideID=g.id;F.db.step=1
F.db.completed={};F.db.skipped={};F.db.manualSkippedSteps={};F.db.confirmedSteps={};F.db.guides={}
C_QuestLog.IsQuestFlaggedCompleted=function() return false end
P:LoadCatchUp()
assert(g.steps[1].questID==100003 and g.steps[1].type=='pickup','oldest prerequisite is first')
assert(g.steps[4].questID==100002,'dependency order')
assert(F.UI:ActionTitle(g.steps[1]):find('PriorityCatchup'),'running marker before title')
local count=#g.steps
P:LoadCatchUp();assert(#g.steps==count,'catch-up reload is idempotent')
F.QuestLog.byID={[100003]={id=100003,title='First',complete=true}}
P:LoadCatchUp()
assert(g.steps[1].questID==100003 and g.steps[1].type=='turnin','ready quest only needs delivery')
F.QuestLog.byID={[100002]={id=100002,title='Middle',complete=false}}
P:LoadCatchUp()
assert(g.steps[1].questID==100002 and g.steps[1].type=='objective','accepted quest starts at objectives')
assert(not P.requiredQuests[100003],'accepted descendant proves earlier acceptance prerequisites')
F.db.completed={[100003]=true,[100002]=true};F.QuestLog.byID={}
P:LoadCatchUp();assert(g.steps[1].id=='entry','no missing prerequisites starts ordinary route')
-- Class unlocks already authored after entry move to the catch-up prefix without duplicates.
g.authoredSteps={{id='entry',type='note',confirmOnNext=true},
 {id='unlock-accept',type='pickup',questID=100003,critical=true},
 {id='unlock-objective',type='objective',questID=100003,critical=true},
 {id='unlock-deliver',type='turnin',questID=100003,critical=true}}
F.db.completed={};F.db.manualSkippedSteps={}
P:LoadCatchUp();assert(g.steps[1].questID==100003 and g.steps[1].recovery)
local actions=0;for _,s in ipairs(g.steps) do if s.questID==100003 then actions=actions+1 end end
assert(actions==3,'no duplicate class unlock actions')
F.db.manualSkippedSteps={['unlock-accept']=true}
P:LoadCatchUp();assert(g.steps[1].id=='entry','explicit skipped quest is not recovered')
F.db.step=4;E.catchUpPending=true;F.db.restartStepID=nil
E:CatchUpOnLoad();assert(not E.catchUpPending,'linked sections run catch-up on load')
-- Recommend Guide loads directly, without an intermediate highlighted choice.
F.UI:Create();F.Minimap:Create()
local target='alliance-redridge-human-15-20'
local selected
L.Recommended=function() return target,'Recommendation' end
L.Select=function(_,guideID,recommended) assert(recommended,'recommend loads check catch-up');selected=guideID end
F.Minimap.recommendButton.scripts.OnClick()
assert(selected==target,'recommendation button loads the guide directly')
''')
print('PASS: level recommendations, catch-up order, live stages, reloads, unlock deduplication and skips')
