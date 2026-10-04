"""Shared loot targets stay sourced, separated by ingredient and combat-safe."""
from pathlib import Path
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase();F.SecureTarget:Create()
F.QuestLog.TurnedIn=function() return false end
for _,id in ipairs({11,47,60,156,297,313,416,418,459,470}) do
 local record=F.QuestTargets[id]
 local q={id=id,title=record.title,complete=false,objectives={}}
 local ingredients={}
 for _,source in ipairs(record.objectives) do
  local verified=false
  for _,point in ipairs(F.AllianceQuestData[id].locations) do
   if point.entityType==1 and point.role=='sourcerequirement' and point.item==source.item and point.name==source.mob then verified=true end
  end
  assert(verified,'target source must exist in recorded drop data: '..id..' '..source.mob)
  q.objectives[source.index]={type='item',objectID=source.itemID,text=source.item..': 0/10',finished=false}
  ingredients[source.index]=true
 end
 F.QuestLog.byID={[id]=q}
 F.Guide={steps={{id='hunt',type='objective',questID=id}}}
 F.db.step=1;F.db.skipped={}
 F.SecureTarget:UpdateTasks(F.GuideEngine:Targets())
 local count=0;for _ in pairs(ingredients) do count=count+1 end
 assert(#F.SecureTarget.desiredTargets==count,'one icon per ingredient: '..id)
 for _,target in ipairs(F.SecureTarget.desiredTargets) do assert(#target.mobs>1) end
 q.objectives[1].finished=true
 F.SecureTarget:UpdateTasks(F.GuideEngine:Targets())
 assert(#F.SecureTarget.desiredTargets==count-1,'finished ingredient removes only its icon')
 q.complete=true
 assert(#F.GuideEngine:Targets()==0,'completed quest has no target list')
end
''')
print('PASS: 10 additional grouped quests, sourced mobs, separate ingredients and completion')
