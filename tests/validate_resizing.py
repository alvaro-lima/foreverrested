"""Resize drags coalesce layout events and defer full guide reflow to release."""
from pathlib import Path
import sys

sys.dont_write_bytecode = True
base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace["lua"].execute(r'''
F.LoadDatabase(); F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create()
F.GuideLibrary:Select('alliance-dun-morogh-01-10')
local U,T=F.UI,F.Tracker
local entries=T.entries
local refresh,layout=T.Refresh,U.Layout
local rebuilds,layouts=0,0
T.Refresh=function(self,...) rebuilds=rebuilds+1; return refresh(self,...) end
U.Layout=function(self,...) layouts=layouts+1; return layout(self,...) end
U.resizeGrip.scripts.OnMouseDown(nil,'LeftButton')
for width=401,500 do U.frame.scripts.OnSizeChanged(U.frame,width,600) end
assert(layouts==0 and rebuilds==0)
U.frame.scripts.OnUpdate(U.frame,.02)
assert(layouts==0)
U.frame.scripts.OnUpdate(U.frame,.03)
assert(layouts==1 and rebuilds==0 and T.entries==entries)
assert(T.frame:GetWidth()==484,'latest resize event wins')
U.frame:SetSize(510,620)
U.frame.scripts.OnSizeChanged(U.frame,510,620)
U.resizeGrip.scripts.OnMouseUp()
assert(layouts==2 and rebuilds==1 and T.entries~=entries)
assert(not U.resizing and not U.pendingSize)
assert(F.db.windowSize.width==510 and F.db.windowSize.height==620)
U.frame.scripts.OnUpdate(U.frame,.1)
assert(layouts==2,'release cancels queued layout')
T.Refresh=refresh; U.Layout=layout
''')
print("PASS: resize events coalesce; drag reuses cached rows; release reflows once and saves final size.")
