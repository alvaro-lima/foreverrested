"""Audit cross-zone quest actions in every bundled guide (Python + lupa)."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parents[1]
base = root / "tests/validate.py"
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
lua = namespace["lua"]
report = lua.execute(r'''
F.LoadDatabase()
F.db.knownFlightPaths={}
local lines={'# Travel route audit','',
 'Generated from all bundled guides and quest location facts, including generated class unlock detours across all nine supported classes and four standard Alliance races.',
 '', 'This checks transport coverage, not fastest quest ordering. Distances, flight time, terrain, contention and quest availability still need in-game evidence.',
 '', '| Guide | Cross-zone quest actions | Connections without reviewed transport |',
 '| --- | ---: | --- |'}
local details={}
for _,id in ipairs(F.GuideLibrary.order) do
 local guide=F.GuideLibrary.guides[id]
 if guide.status=='draft' then
  F.Guide=guide
  local name=guide.name or guide.title or guide.id
  UnitLevel=function() return guide.maxLevel or 30 end
  for _,race in ipairs({'Human','Dwarf','NightElf','Gnome'}) do
   UnitRace=function() return race,race end
   for _,class in ipairs({'WARRIOR','PALADIN','HUNTER','ROGUE','PRIEST','MAGE','WARLOCK','DRUID','SHAMAN'}) do
    UnitClass=function() return class,class end
    F.QuestPolicy:EnsureUnlockSteps(guide)
   end
  end
  local count,missing=0,{}
  for _,step in ipairs(guide.steps) do
   if not step.travelQuestID and not step.flightPathTravel then
    for _,task in ipairs(step.tasks or {step}) do
     if task.type=='objective' or task.type=='turnin' then
      local data=F.GuideEngine:Metadata(task.questID)
      local points={}
      for _,p in ipairs(data and data.locations or {}) do
       points[p.role]=F.Travel:ReferenceLocation(data,p.role)
      end
      local start=task.type=='objective' and points.start or points.requirement or points.sourcerequirement or points.start
      local target=task.type=='objective' and (points.requirement or points.sourcerequirement) or points['end']
      if start and target and start.zone and target.zone and start.zone~=target.zone then
       count=count+1
       local routeClass=task.classes and task.classes[1]
       if start.zone=='Moonglade' or target.zone=='Moonglade' then routeClass='DRUID' end
       UnitClass=function() return routeClass,routeClass end
       local legs=F.Travel:Route(start.zone,target.zone)
       local unknown=false
       for _,leg in ipairs(legs) do if leg.text:find('no reviewed transport route',1,true) then unknown=true end end
       if unknown then missing[start.zone..' → '..target.zone]=true end
       details[#details+1]='| '..name..' | '..step.id..' | '..task.questID..' | '..start.zone..' → '..target.zone..' | '..(unknown and 'Needs route evidence' or 'Reviewed transport connection')..' |'
      end
     end
    end
   end
  end
  local gaps={};for pair in pairs(missing) do gaps[#gaps+1]=pair end;table.sort(gaps)
  lines[#lines+1]='| '..name..' | '..count..' | '..(#gaps>0 and table.concat(gaps,'; ') or 'None found')..' |'
 end
end
lines[#lines+1]=''
lines[#lines+1]='## Cross-zone actions'
lines[#lines+1]=''
lines[#lines+1]='| Guide | Step ID | Quest | Connection | Coverage |'
lines[#lines+1]='| --- | --- | ---: | --- | --- |'
for _,line in ipairs(details) do lines[#lines+1]=line end
return table.concat(lines,'\n')..'\n'
''')
output = root / "Data/TRAVEL_AUDIT.md"
output.write_text(report, encoding="utf-8")
print(f"Wrote {output}")
