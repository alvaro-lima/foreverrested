"""Required work and XP recovery cannot depend on optional quest completion."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_xp_progression import main
main()
audit=json.loads(Path(__file__).resolve().parents[1].joinpath('Data/XP_PROGRESSION_AUDIT.json').read_text())
ash=next(g for g in audit['chapters'] if g['guideID']=='alliance-kalimdor-20-24')
assert ash['listedRequiredQuestXP']==25535
assert {1016,1024}.issubset(ash['requiredTurninIDs'])
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local a=F.GuideLibrary.guides['alliance-kalimdor-20-24']
local b=F.GuideLibrary.guides['alliance-kalimdor-25-27-rebuild']
local found={}
for _,s in ipairs(a.steps) do
 if s.questID==1093 or s.questID==1025 or s.questID==1024 or s.questID==1016 then
  assert(not s.optional and not s.activeOnly,'local quest circuit is required')
  found[s.questID..':'..s.type]=true
 end
 assert(not (s.questID and ({[1072]=true,[1073]=true,[1074]=true,[1075]=true,[1076]=true,[1077]=true,[1094]=true,[1095]=true,[1096]=true,[1090]=true,[1092]=true,[1057]=true,[86574]=true})[s.questID]),'distant optional detour left in introductory chapter')
end
for _,id in ipairs({1093,1025}) do
 for _,kind in ipairs({'pickup','objective','turnin'}) do assert(found[id..':'..kind]) end
end
for _,kind in ipairs({'pickup','objective','turnin'}) do assert(found['1016:'..kind]) end
assert(found['1024:pickup'] and found['1024:turnin'])
for _,s in ipairs(b.steps) do assert(s.questID~=1025 and s.questID~=1024 and s.questID~=1016,'moved quest belongs only to its new chapter') end
local exit=a.steps[#a.steps]
assert(exit.levelRecovery and exit.zone=='Ashenvale' and exit.text:find('Foulweald Warrior',1,true))
UnitLevel=function() return 22 end
UnitXP=function() return 1000 end
UnitXPMax=function() return 4000 end
assert(not F.GuideEngine:Done(exit),'22 with partial XP must not satisfy level 23')
assert(F.UI:TaskText(exit):find('3000 XP to next level',1,true),'live shortfall remains visible')
UnitLevel=function() return 23 end
assert(F.GuideEngine:Done(exit))
assert(a.nextGuideID=='alliance-kalimdor-23-24')
local wetlands=F.GuideLibrary.guides['alliance-kalimdor-23-24']
assert(wetlands.nextGuideID=='alliance-kalimdor-24-25')
assert(wetlands.steps[1].id=='menethil-first:pickup:279',
 'Kalimdor arrival starts at Menethil, not the optional Dun Algaz approach')
assert(F.GuideLibrary.guides['alliance-kalimdor-24-25'].nextGuideID==b.id)
assert(b.nextGuideID=='alliance-kalimdor-27-30')
assert(F.GuideLibrary.guides['alliance-kalimdor-24-27'].retired)
local legacy=F.GuideLibrary.guides['alliance-kalimdor-24-27']
local oldStep
for index,s in ipairs(legacy.steps) do if s.id=='culling-threat-objectives' then oldStep=index end end
assert(oldStep)
F.db.guideID=legacy.id;F.db.step=oldStep;F.db.stepID=legacy.steps[oldStep].id
F.db.manualSkippedSteps={['culling-threat-pickup']=true}
F.GuideLibrary:Initialize()
assert(F.Guide.id==b.id and F.Guide.steps[F.db.step].id=='culling-threat-objectives',
 'retired middle chapter migrates to the retained Ashenvale action')
assert(F.db.manualSkippedSteps['culling-threat-pickup'],'explicit skip survives route rebuild')
local final=F.GuideLibrary.guides['alliance-kalimdor-27-30']
assert(final.steps[#final.steps].text:find('Ghostpaw Alpha',1,true))
''')
print('PASS: required local work, single chapter ownership, live XP shortfall and suitable exit recovery')
