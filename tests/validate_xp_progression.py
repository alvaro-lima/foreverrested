"""Required work and XP recovery cannot depend on optional quest completion."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from audit_xp_progression import main
main()
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local a=F.GuideLibrary.guides['alliance-kalimdor-20-24']
local b=F.GuideLibrary.guides['alliance-kalimdor-24-27']
local found={}
for _,s in ipairs(a.steps) do
 if s.questID==1093 or s.questID==1025 then
  assert(not s.optional and not s.activeOnly,'local quest circuit is required')
  found[s.questID..':'..s.type]=true
 end
end
for _,id in ipairs({1093,1025}) do
 for _,kind in ipairs({'pickup','objective','turnin'}) do assert(found[id..':'..kind]) end
end
for _,s in ipairs(b.steps) do assert(s.questID~=1025,'moved objective belongs only to its new chapter') end
local exit=a.steps[#a.steps]
assert(exit.levelRecovery and exit.zone=='Ashenvale' and exit.text:find('Foulweald Warrior',1,true))
UnitLevel=function() return 23 end
UnitXP=function() return 1000 end
UnitXPMax=function() return 4000 end
assert(not F.GuideEngine:Done(exit),'23 with partial XP must not satisfy level 24')
assert(F.UI:TaskText(exit):find('3000 XP to next level',1,true),'live shortfall remains visible')
UnitLevel=function() return 24 end
assert(F.GuideEngine:Done(exit))
local final=F.GuideLibrary.guides['alliance-kalimdor-27-30']
assert(final.steps[#final.steps].text:find('Ghostpaw Alpha',1,true))
''')
print('PASS: required local work, single chapter ownership, live XP shortfall and suitable exit recovery')
