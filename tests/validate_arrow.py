"""Arrow rotation between navigation samples, wraparound and frame-rate behavior."""
from pathlib import Path
import runpy

lua = runpy.run_path(str(Path(__file__).with_name("validate.py")))["lua"]
lua.execute(r'''
local A,N=F.Arrow,F.Navigation
-- Size updates live, persists, and stays within usable bounds.
A:SetSize(64)
assert(F.db.arrowSize==64 and A.compass:GetWidth()==64 and A.frame:GetHeight()==92)
A:SetSize(200);assert(F.db.arrowSize==96 and A.compass:GetWidth()==96)
A:SetSize(1);assert(F.db.arrowSize==24 and A.compass:GetWidth()==24)
A:SetSize(48)
local facing=0
function GetPlayerFacing() return facing end
local renders=0
A.texture.SetRotation=function(_,angle) renders=renders+1;A.rendered=angle end
N.bearing=0;N.angle=0;N.distance=25;N.targetMap=1;N.tx=.5;N.ty=.4
A.displayAngle=nil;A:Update()
local update, tasks=N.Update,F.GuideEngine.Tasks
N.Update=function() error('per-frame arrow must not recalculate maps/waypoints') end
F.GuideEngine.Tasks=function() error('per-frame arrow must not scan quests') end
facing=math.pi/2
A.frame.scripts.OnUpdate(A.frame,1/60)
assert(A.rendered<0 and A.rendered>-math.pi/2,'turn must animate before next 200ms navigation sample')
for i=1,29 do A.frame.scripts.OnUpdate(A.frame,1/60) end
assert(math.abs(A.rendered+math.pi/2)<.0001 and renders>10)
N.Update=update;F.GuideEngine.Tasks=tasks
-- Same elapsed time at different frame rates gives the same response.
local function response(rate)
 A.displayAngle=0
 for i=1,rate do A:Animate(1/rate) end
 return A.displayAngle
end
assert(math.abs(response(30)-response(120))<.000001)
-- The +179 to -179 boundary takes the two-degree arc, not a full revolution.
A.displayAngle=math.rad(179);facing=math.rad(179)
A:Animate(1/60)
assert(math.abs(A.displayAngle)>math.rad(178))
-- A newly selected destination snaps once rather than reusing the old bearing.
N.targetMap=2;N.angle=.3;A:Update();assert(math.abs(A.displayAngle-.3)<.000001)
-- Missing facing / invalid navigation hide and reset the animation safely.
facing=nil;A:Animate(1/60)
assert(not A.frame:IsShown() and A.displayAngle==nil and N.angle==nil)
facing=0;N.bearing=.7;N.angle=.7;A:Update();A:Animate(1/60)
assert(A.frame:IsShown() and math.abs(A.displayAngle-.7)<.000001)
N.bearing=nil;N.angle=nil;N.distance=nil;A:Update()
assert(not A.frame:IsShown() and A.displayAngle==nil)
-- Only an exact creature selected through a secure icon may override the arrow.
local guid,dead='Creature-test',false
function UnitGUID() return guid end
function UnitName() return 'Test Wolf' end
function UnitIsDead() return dead end
function UnitPosition(unit)
 if unit=='target' then return 110,220,0,1 end
 return 100,200,0,1
end
F.SecureTarget:UpdateTasks({{mob='Test Wolf'}})
F.SecureTarget.buttons[1].scripts.PostClick(F.SecureTarget.buttons[1],'LeftButton')
assert(F.SecureTarget.toolTargetGUID==guid)
assert(math.abs(N.followDistance-math.sqrt(500))<.000001 and A.yards.text=='22 yd')
-- Unsupported creature positions retain the safe guide fallback, not a guessed mob position.
UnitPosition=function() return nil end
N:UpdateToolTarget();N.bearing=.7;N.angle=.7;N.distance=25;A:Update()
assert(N.followDistance==nil and A.yards.text=='25 yd')
guid='Another-creature';N:UpdateToolTarget();assert(F.SecureTarget.toolTargetGUID==nil)
guid='Creature-test';F.SecureTarget.toolTargetGUID=guid;dead=true
N:UpdateToolTarget();assert(N.followDistance==nil and F.SecureTarget.toolTargetGUID==nil)
''')
print("PASS: fluid facing updates, shortest-arc rotation, frame-rate independence, secure-click target following and unavailable/dead/changed-target fallback.")
