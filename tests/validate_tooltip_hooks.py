"""Repeated tooltip refresh must not accumulate hide hooks or reenter cancellation."""
from pathlib import Path
import sys
sys.dont_write_bytecode=True
base=Path(__file__).with_name('validate.py')
setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)}
exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
F.LoadDatabase()
local T=F.Tooltips
local button=CreateFrame('Button')
local hooks=0
button.HookScript=function(self,event,callback) hooks=hooks+1;self.hideCallback=callback end
local count=#T.owners
for i=1,2000 do T:Text(button,'Objectives','Help '..i,true) end
assert(hooks==1 and #T.owners==count+1,'refreshes register only one hook and owner')
local hides=0
GameTooltip.Hide=function() hides=hides+1;button.hideCallback(button) end
T.shownOwner=button
button.hideCallback(button)
assert(hides==1 and T.shownOwner==nil,'hide cancellation cannot recurse')
''')
print('PASS: tooltip refresh hook deduplication and nonrecursive cancellation')
