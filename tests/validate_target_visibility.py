"""Closing the guide preserves targets; minimap toggles both panels."""
from pathlib import Path
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
F.UI.frame=CreateFrame('Frame')
F.UI.Debug=function() end
F.Arrow.Update=function() end
F.StepPins.Update=function() end
F.SecureTarget:Create()
F.SecureTarget:UpdateTasks({{mob='Frostmane Troll Whelp'}})
assert(F.SecureTarget.frame:IsShown())
F.UI:Toggle()
assert(not F.UI.frame:IsShown() and F.SecureTarget.frame:IsShown(),'close keeps targets')
F.SecureTarget:UpdateTasks(F.SecureTarget.desiredTargets)
assert(F.SecureTarget.frame:IsShown(),'refresh keeps targets while main is closed')
F.UI:Toggle(true)
assert(not F.UI.frame:IsShown() and not F.SecureTarget.frame:IsShown(),'minimap hides both after close')
F.UI:Toggle(true)
assert(F.UI.frame:IsShown() and F.SecureTarget.frame:IsShown(),'minimap restores both')
combat=true
F.UI:Toggle(true)
assert(F.SecureTarget.pending,'protected visibility is deferred in combat')
combat=false
F.SecureTarget:UpdateTasks(F.SecureTarget.desiredTargets)
assert(not F.SecureTarget.frame:IsShown(),'deferred hide is applied safely')
''')
print('PASS: independent close, refresh, minimap toggles and combat deferral')
