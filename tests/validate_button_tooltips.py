"""Guide button help appears on hover, including replaced help text."""
from pathlib import Path

base = Path(__file__).with_name("validate.py")
setup = base.read_text().split("lua.execute(r'''", 2)
namespace = {"__file__": str(base)}
exec(setup[0] + "lua.execute(r'''" + setup[1], namespace)
namespace["lua"].execute(r'''
F.LoadDatabase(); F.UI:Create()
for _,button in ipairs(F.UI.footerButtons) do
 GameTooltip:Hide()
 button.scripts.OnEnter(button)
 assert(GameTooltip:IsShown() and GameTooltip.owner==button)
 assert(GameTooltip.text==button:GetText() and not F.Tooltips.pending)
 button.scripts.OnLeave(button)
 assert(not GameTooltip:IsShown())
end
local clear=F.UI.searchClear
clear.scripts.OnEnter(clear)
assert(GameTooltip:IsShown() and GameTooltip.text=="Clear search")
clear.scripts.OnLeave(clear)
local delayed=F.UI.resizeGrip
delayed.scripts.OnEnter(delayed)
assert(not GameTooltip:IsShown())
F.Tooltips:Tick(3.1)
assert(GameTooltip:IsShown() and GameTooltip.owner==delayed)
delayed.scripts.OnLeave(delayed)
''')
print("PASS: immediate footer and Clear button help; delayed controls retain their delay.")
