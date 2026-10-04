"""Audit every bundled guide and exercise shared row/tooltip deduplication."""
from pathlib import Path

base = Path(__file__).with_name('validate.py')
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {'__file__': str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace['lua'].execute(r'''
F.LoadDatabase();F.UI:Create()
local U=F.UI
assert(U:UniqueText('|cffffff80Fly to Thelsamar.|r\n  Fly to Thelsamar.')=='|cffffff80Fly to Thelsamar.|r')
local seen={}
U:UniqueText('Accept Report to Mountaineer Rockgar',seen)
assert(U:UniqueText('|cffffd100Accept: Report to Mountaineer Rockgar|r\nNOT STARTED\nListed XP ~165',seen)=='NOT STARTED\nListed XP ~165')
assert(U:UniqueText('Fly to Thelsamar.\nLearn the flight path, then fly to Thelsamar.')=='Fly to Thelsamar.\nLearn the flight path, then fly to Thelsamar.')
assert(U:UniqueText('NOT STARTED\nNOT STARTED')=='NOT STARTED\nNOT STARTED')
local count,repeated=0,0
for _,guide in pairs(F.GuideLibrary.guides) do
 F.Guide=guide
 for _,step in ipairs(guide.steps) do
  count=count+1
  local title=U:ActionTitle(step)
  local note=F.Travel:Note(step)
  local text=title
  for _,task in ipairs(F.GuideEngine:Tasks(step)) do
   text=text..'\n'..U:ActionBody(task)
  end
  if note then text=text..'\n'..note end
  local clean=U:UniqueText(text)
  if clean~=text then repeated=repeated+1 end
  assert(U:UniqueText(clean)==clean,'deduplication must be stable')
 end
end
print('Audited '..count..' steps; '..repeated..' expanded descriptions contained repeated lines.')
F.Guide={title='Duplicate travel',quests={},steps={{type='travel',text='Fly to Thelsamar.',note='Fly to Thelsamar.',optional=true}}}
F.db.step=1;F.db.skipped={};F.Tracker:Refresh()
local row=F.Tracker.rows[1];row.stepIndex=1;row.zone=false;row:Show()
local lines={}
GameTooltip.AddLine=function(_,line) lines[#lines+1]=line end
row.scripts.OnEnter(row);F.Tooltips:Tick(2)
local _,occurrences=table.concat(lines,'\n'):gsub('Fly to Thelsamar%.','')
assert(occurrences==1,'travel tooltip must not repeat its title')
''')
print('PASS: shared duplicate suppression across bundled guides and travel tooltips')
