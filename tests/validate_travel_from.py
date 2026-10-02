"""Arrival at zero yards resumes a travel checkpoint selected with From."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace["lua"].execute(r'''
F.LoadDatabase(); F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create()
local E=F.GuideEngine
F.Guide={id='arrival-test',steps={
 {id='arrival',type='travel',travelQuestID=101,travelAction='objective',
  travelFinal=true,travelLeg=1,travelZones={'Ashenvale'},
  travelFrom='Darkshore',travelTo='Ashenvale',confirmOnNext=true},
 {id='collect',type='objective',questID=101},
}}
F.db.step=1
C_Map.GetMapInfo=function() return {name='Ashenvale',parentMapID=0} end
C_Map.GetPlayerMapPosition=function() return CreateVector2D(.5,.4) end
E:ResetFrom(1)
F.Navigation:Update();F.Arrow:Update()
assert(E.manualHold and F.db.step==1,'From reproduces held travel step')
assert(F.Navigation.distance==0 and F.Arrow.frame:IsShown(),'arrow shows zero yards')
F.Travel:Tick()
assert(not E.manualHold and F.db.step==2,'arrival automatically releases hold and advances')
E:ResetFrom(2)
F.Travel:Tick()
assert(E.manualHold and F.db.step==2,'quest restart points retain their hold')
''')
print("PASS: zero-yard travel arrival after From advances automatically; quest restart hold is preserved.")
