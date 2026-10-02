"""Scrolling long routes reuses prepared rows without rescanning the guide."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
lua = namespace["lua"]
lua.execute(r'''
local T,E=F.Tracker,F.GuideEngine
F.LoadDatabase(); F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create()
F.GuideLibrary:Select('alliance-dun-morogh-01-10')
T:SetSearch(''); T.offset=0; T.topOffset=nil; T:Refresh()
assert(#T.entries>60 and T.maxOffset>10)
local entries,counts=T.entries,T.progressCounts
local state,markers,useful=E.StepState,F.UI.StepMarkers,F.GearRewards.QuestGear
local probe=T.rows[1].body
local measure=probe.GetStringHeight
local function unexpected() error('scrolling must not rebuild or measure the guide') end
E.StepState=unexpected; F.UI.StepMarkers=unexpected
F.GearRewards.QuestGear=unexpected; probe.GetStringHeight=unexpected
for offset=1,10 do
 T:ScrollTo(offset)
 assert(T.offset==offset and T.rows[1].stepIndex==entries[offset+1].stepIndex)
end
T:ScrollTo(T.maxOffset)
assert(T.rows[T.visibleRows].stepIndex==entries[#entries].stepIndex,'last page includes final step')
for offset=10,0,-1 do T:ScrollTo(offset) end
assert(T.entries==entries and T.progressCounts==counts)
E.StepState=state; F.UI.StepMarkers=markers
F.GearRewards.QuestGear=useful; probe.GetStringHeight=measure
T:Refresh()
assert(T.entries~=entries,'live refresh rebuilds cached content')
T:SetSearch('trainer')
assert(T.entries~=entries and T.searchQuery=='trainer','search rebuilds cached content')
T:SetSearch('')
''')
print("PASS: long-guide scrolling avoids quest scans, reward scoring and text measurement; live refresh and search rebuild the list.")
