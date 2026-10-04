"""Early route coverage, bounded sections, optional actions and saved-position migration."""
from pathlib import Path
import sys
sys.dont_write_bytecode = True
base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
ns = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local L=F.GuideLibrary
local bySource,count={},0
for _,id in ipairs(L.order) do
 local g=L.guides[id]
 if g.sourceGuideID and g.minLevel<20 then
  count=count+1;print(g.title,#g.steps)
  assert(#g.steps>0 and #g.steps<=65,'bounded early section '..g.id)
  bySource[g.sourceGuideID]=bySource[g.sourceGuideID] or {}
  local actions=bySource[g.sourceGuideID]
  for _,s in ipairs(g.steps) do
   assert(not actions[s.id],'action duplicated across sections '..s.id)
   actions[s.id]=g.id
   assert(s.type~='grind' or s.levelRecovery and s.zone and s.x and s.y and s.note,'level recovery has concrete local guidance')
   assert(s.type=='trainer' or not s.alongside or #s.alongside==0,'side quests must have rows')
   if s.optional and s.questID then assert(not s.activeOnly,'optional pickup can be selected') end
  end
  assert(L.guides[g.nextGuideID],'linked next guide exists')
  local visited,current={},g
  while current do
   assert(not visited[current.id],'route loop');visited[current.id]=true
   current=current.nextGuideID and L.guides[current.nextGuideID]
  end
 end
end
assert(count==22,'expected early sections')
for source,actions in pairs(bySource) do
 local old=L.guides[source]
 assert(old.retired,'old circuit hidden')
 for _,s in ipairs(old.steps) do
  local side=s.type~='trainer' and s.alongside or nil
  local retained=not side or #side==0 or s.tasks and #s.tasks>0 or s.type~='note' and s.type~='group'
  if retained and s.type~='grind' and s.id~='finish' and not s.id:find('%-finish$') then
   assert(actions[s.id],'lost original action '..source..':'..s.id)
  end
 end
 -- A stable action ID shared by another starter route must not migrate there.
 local index
 for i,s in ipairs(old.steps) do if actions[s.id] then index=i end end
 assert(index)
 F.db.guideID=source;F.db.step=index;F.db.stepID=old.steps[index].id
 F.db.guides={};F.db.skipped={};F.db.skippedIDs=nil;F.db.confirmedSteps={}
 F.db.manualSkippedSteps={};F.db.skipHistory={};F.db.guideRevision=old.revision
 L:Initialize()
 assert(F.Guide.sourceGuideID==source,'migration stayed in original route')
 assert(F.db.guideID==actions[old.steps[index].id],'migration chose matching section')
end
for bracket,expected in ipairs({10,12}) do
 local total=0
 for _,id in ipairs(L:GuidesForBracket(bracket)) do
  assert(not L.guides[id].retired,'chooser hides retired circuits')
  if L.guides[id].sourceGuideID then total=total+1 end
 end
 assert(total==expected,'chooser exposes short sections')
end
''')
print('PASS: early sections, complete action coverage, optional rows and migration')
