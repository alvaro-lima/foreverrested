from pathlib import Path
base=Path(__file__).with_name('validate.py');setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
F.Guide={zone='Ashenvale',steps={}}
assert(not F.UI:StepLocation({type='objective',questID=272}):find('Ashenvale',1,true),'missing class objective location must not inherit regional guide zone')
assert(F.UI:StepLocation({type='turnin',questID=272}):find('Moonglade',1,true),'Sea Lion delivery is in Moonglade')
assert(F.UI:StepLocation({type='turnin',questID=5061}):find('Darnassus',1,true),'Aquatic Form delivery is in Darnassus')
local bag={}
GetItemCount=function(id) return bag[id] or 0 end
assert(F.GuideEngine:ObjectiveLocation(272).zone=='Darkshore')
assert(F.GuideEngine:ObjectiveLocation(272).actionTitle:find('Agility',1,true))
C_Item={GetItemCount=function(id) return bag[id] or 0 end}
GetItemCount=nil
bag[15883]=1
assert(F.GuideEngine:ObjectiveLocation(272).zone=='Westfall')
assert(F.GuideEngine:ObjectiveLocation(272).actionTitle:find('Endurance',1,true))
bag[15882]=1
assert(F.GuideEngine:ObjectiveLocation(272).zone=='Moonglade')
bag[15885]=1;bag[15882]=nil;bag[15883]=nil
assert(F.GuideEngine:ObjectiveLocation(272).zone=='Moonglade','consumed halves do not restart collection after assembly')
bag[15885]=nil

assert(F.GuideEngine:ObjectiveLocation(5061).zone=='Darnassus')
UnitClass=function() return 'Druid','DRUID' end
UnitRace=function() return 'High Order Skyborne','Skyborne' end
UnitLevel=function() return 22 end
local g=F.GuideLibrary.guides['alliance-kalimdor-20-24']
F.QuestPolicy:EnsureUnlockSteps(g)
local review,count
count=0
for _,s in ipairs(g.steps) do
 if s.questID==26 and s.type=='pickup' then review=s;count=count+1 end
end
assert(review and count==1,'level-22 Skyborne gets the actual aquatic chain')
F.QuestPolicy:EnsureUnlockSteps(g)
count=0;for _,s in ipairs(g.steps) do if s.id==review.id then count=count+1 end end
assert(count==1,'repeated catch-up does not duplicate reminder')
assert(not F.GuideEngine:Done(review),'unlearned form needs review')
F.Guide=g;F.db.guideID=g.id;F.db.step=#g.steps
F.db.restartStepID=g.steps[#g.steps].id
F.QuestLog.byID={[272]={id=272,title='Trial of the Sea Lion',complete=false}}
F.QuestLog.TurnedIn=function() return false end
F.GuideEngine.catchUpPending=true
F.GuideEngine:CatchUpOnLoad()
local position,ordinary
for i,s in ipairs(g.steps) do
 if s.questID==272 and s.type=='objective' and s.recovery then position=i end
 if s.questID==1008 and not ordinary then ordinary=i end
end
assert(position and position<ordinary,'accepted sea-lion objective appears in catch-up prefix despite saved From boundary')
IsSpellKnown=function(id) return id==1066 end
assert(F.GuideEngine:Done(review),'learned form completes reminder')
F.QuestPolicy:EnsureUnlockSteps(g)
for _,s in ipairs(g.steps) do
 assert(not (s.id and s.id:find('class-unlock:',1,true)==1 and F.GuideEngine:Done(s,F.GuideEngine:Resolve(s))),
  'completed generated class actions must not clutter the pending route')
end
''')
print('PASS: Skyborne Aquatic Form catch-up, deduplication and learned-form detection')
