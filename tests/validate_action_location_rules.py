"""An unrelated quest/guide zone must never supply missing action evidence."""
from pathlib import Path
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
F.Guide={zone='Ashenvale',questData={
 [999999]={zone='Ashenvale',locations={
  {role='start',zone='Darnassus',x=.3,y=.4},
  {role='end',zone='Moonglade',x=.4,y=.5}}}
}}
assert(F.UI:StepLocation({type='objective',questID=999999})=='Location: Not specified in guide data')
assert(F.UI:StepLocation({type='pickup',questID=999999}):find('Darnassus',1,true))
assert(F.UI:StepLocation({type='turnin',questID=999999}):find('Moonglade',1,true))
assert(#F.GuideEngine:ActionLocations({type='objective',questID=999999})==0,'catalog validator uses the same missing phase evidence')
F.QuestObjectiveLocations[999999]={{role='requirement',zone='Darkshore',x=4,y=.2}}
assert(not F.GuideEngine:ActionLocation({type='objective',questID=999999}),'invalid source coordinates cannot reach runtime navigation')
F.QuestObjectiveLocations[999999]=nil
F.Guide={zone='Ashenvale'}
for _,id in ipairs({272,5061}) do
 for _,action in ipairs({'pickup','objective','turnin'}) do
  local label=F.UI:StepLocation({type=action,questID=id})
  assert(not label:find('Not specified',1,true),id..' '..action)
  assert(not label:find('Ashenvale',1,true),id..' '..action)
 end
end
''')
print('PASS: action-specific locations and complete aquatic quest phase coverage')
