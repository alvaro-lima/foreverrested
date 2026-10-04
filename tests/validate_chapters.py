"""Short linked routes, dependency order, carry-over objectives and automatic handoff."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).with_name('validate.py');setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local L,E=F.GuideLibrary,F.GuideEngine
local turnins={}
for _,id in ipairs(L.order) do
 local g=L.guides[id]
 if g.routeGroup=='eastern-20-30' and g.minLevel>=20 then
  print(g.title,#g.steps)
  assert(#g.steps>0 and #g.steps<65,'short populated section')
  local seen,pickups={},{}
  for _,s in ipairs(g.steps) do
   if s.optional then assert(not s.alongside or #s.alongside==0,'optional quest is a real row') end
   assert(not seen[s.id]);seen[s.id]=true
   assert(s.type~='grind' or s.levelRecovery and s.zone and s.x and s.y,'recovery has concrete local guidance')
   for _,t in ipairs(s.tasks or {s}) do
    if t.questID then
     if t.type=='pickup' and not t.optional then
      assert(not pickups[t.questID],'duplicate pickup');pickups[t.questID]=true
      for _,prior in ipairs(F.QuestPolicy:Record(t.questID).prerequisites or {}) do
       assert(turnins[prior] or F.QuestPolicy:Satisfied(prior),'missing prerequisite '..prior..' for '..t.questID)
      end
     end
     if t.type=='turnin' then turnins[t.questID]=true end
    end
   end
  end
  if g.nextGuideID then assert(L.guides[g.nextGuideID],'next section exists') end
 end
end
assert(turnins[484] and turnins[470] and turnins[299] and turnins[58])
for _,id in ipairs(L:GuidesForBracket(3)) do assert(not L.guides[id].retired) end
-- Retired guide positions migrate by stable action ID.
local old=L.guides['alliance-wetlands-20-30']
local oldIndex
for index,s in ipairs(old.steps) do if s.id=='greenwarden-paws-objectives' then oldIndex=index end end
assert(oldIndex)
F.db.guideID=old.id;F.db.step=oldIndex;F.db.stepID=old.steps[oldIndex].id
F.db.manualSkippedSteps={['menethil-first:pickup:484']=true}
L:Initialize()
assert(F.db.guideID=='alliance-eastern-20-22','retired guide migrates to its matching visit')
assert(F.Guide.steps[F.db.step].id=='greenwarden-paws-objectives','migration preserves current action')
assert(F.db.manualSkippedSteps['menethil-first:pickup:484'],'migration preserves explicit skips')
-- Handoff uses the real progression engine, saves outgoing state, and respects manual hold.
local a={id='handoff-a',title='A',steps={{id='a',type='note',confirmOnNext=true}},nextGuideID='handoff-b',routeGroup='test'}
local b={id='handoff-b',title='B',steps={{id='b',type='note',confirmOnNext=true}},routeGroup='test'}
L:Register(a);L:Register(b)
F.Guide=a;F.db.guideID=a.id;F.db.step=1;F.db.skipped={};F.db.confirmedSteps={a=true}
E.manualHold=true;E:AdvanceSafe();assert(F.Guide==a,'manual browsing holds section')
E.manualHold=nil;E:AdvanceSafe();assert(F.Guide==b and F.db.step==1,'automatic section handoff')
assert(F.db.guides[a.id].confirmedSteps.a,'outgoing progress saved')
-- Accepted objectives remain owned by their scheduled chapter.
a.steps={{id='qa',type='objective',questID=101}};b.steps={{id='qb',type='objective',questID=102}}
F.QuestLog.list={{id=101,title='Carry over',objectives={{text='A: 1/3',finished=false}}}}
F.db.completed={};C_QuestLog.IsQuestFlaggedCompleted=function() return false end
assert(#F.ObjectiveQueue:Build()==0,'previous-chapter collection stays with its scheduled chapter')
F.Guide=a
assert(#F.ObjectiveQueue:Build()==1,'accepted objective remains available in its owning chapter')
F.Guide=b
F.db.guides[a.id].manualSkippedSteps={qa=true}
assert(#F.ObjectiveQueue:Build()==0,'skip survives section handoff')
''')
print('PASS: short routes, prerequisite ordering, handoffs and chapter objective ownership')
