"""Online acquisition evidence stays distinct from quest delivery and combat."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
review=json.loads((root/'Data/ONLINE_ACTION_LOCATIONS.json').read_text())
for points in review['locations'].values():
    for p in points:
        assert p['source'].startswith('https://') and p['evidenceKind']
        assert p['approximate'] and 0<=p['x']<=1 and 0<=p['y']<=1
base=Path(__file__).with_name('validate.py');setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local E=F.GuideEngine
F.Guide={id='online-locations',steps={}}
local bow={type='pickup',questID=96138}
local contact=F.UI:ActionContact(bow)
assert(contact:find('Loot',1,true) and contact:find('Lost Watcher',1,true) and not contact:find('Talk to',1,true),'item-started quest is not a conversation')
assert(F.UI:ActionContact({type='pickup',questID=86613}):find('Interact',1,true),'tools quest begins at its object')
for _,id in ipairs({62,76,92597,93552,92683,93949,92747,92749,86667,1141,984,944,94896,93835,93160,94485,98197,96139}) do
 local points=E:ActionLocations({type='objective',questID=id})
 assert(#points>0 and points[1].x and points[1].y,'objective has recorded coordinates '..id)
end
local task={id='spoils',type='objective',questID=98197}
F.QuestLog.byID[98197]={id=98197,complete=false,objectives={{finished=true},{finished=false}}}
for _,p in ipairs(E:ActionLocations(task)) do assert(p.objectiveIndex==2,'finished timber must not keep directing collection') end
C_Map.GetBestMapForUnit=function() return 1437 end
C_Map.GetMapInfo=function(map) if map==1437 then return {name='Wetlands'} end end
C_QuestLog.GetNextWaypoint=function() return 1437,.99,.99 end
F.Guide.steps={task};F.db.step=1
local map,x,y=F.StepPins:TaskLocation(task)
assert(map==1437 and x<.2 and y<.7,'pin uses recorded remaining iron rather than unrelated native waypoint')
local nm,nx,ny=F.Navigation:Waypoint()
assert(nm==map and nx==x and ny==y,'arrow and pin use the same remaining acquisition source')
for _,gid in ipairs(F.GuideLibrary.order) do
 local g=F.GuideLibrary.guides[gid]
 if g.sourceGuideID then for _,s in ipairs(g.steps) do for _,t in ipairs(s.tasks or {s}) do
  assert(t.questID~=912,'unsupported disguise actions must stay out of playable guides')
 end end end
end
''')
print('PASS: online evidence, acquired quest starts, remaining ingredients and unsupported quest exclusion')
