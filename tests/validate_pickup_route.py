from pathlib import Path
base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace['lua'].execute(r'''
local expected={279,484,305,470,463}
local function distance(ids)
 local total,previous=0,nil
 for _,id in ipairs(ids) do
  local point
  for _,p in ipairs(F.AllianceQuestData[id].locations) do
   if p.role=='start' then point=p;break end
  end
  assert(point and point.zone=='Wetlands')
  if previous then total=total+math.sqrt((point.x-previous.x)^2+(point.y-previous.y)^2) end
  previous=point
 end
 return total
end
assert(distance(expected)<distance({279,484,463,305,470})*.8,'harbor pickups must reduce backtracking')
for _,guideID in ipairs({'alliance-wetlands-20-30','alliance-eastern-20-22'}) do
 local found={}
 for _,step in ipairs(F.GuideLibrary.guides[guideID].steps) do
  if step.legacyGroupID=='menethil-first' then
   local task=step.tasks[1]
   assert(task.type=='pickup')
   found[#found+1]=task.questID
   assert(step.id=='menethil-first:pickup:'..task.questID,'stable progress IDs must survive reordering')
  end
 end
 assert(#found==#expected)
 for index,id in ipairs(expected) do assert(found[index]==id) end
end
''')
print('PASS: shorter Menethil pickup circuit in source and chapter; stable step IDs retained')
