from pathlib import Path
base=Path(__file__).with_name('validate.py');setup=base.read_text().split("lua.execute(r'''",2)
ns={'__file__':str(base)};exec(setup[0]+"lua.execute(r'''"+setup[1],ns)
ns['lua'].execute(r'''
local P=F.StepPins
assert(select(1,P:MapPosition(42,.2,.7,42))==.2)
C_Map.GetWorldPosFromMapPos=function(map,v)
 if map==42 then return 1,CreateVector2D(v.x*100,v.y*100) end
 if map==10 then return 1,CreateVector2D((v.x-.1)*200,(v.y-.2)*200) end
 return 2,CreateVector2D(v.x*100,v.y*100)
end
C_Map.GetMapPosFromWorldPos=function(map,v)
 if map==10 then return CreateVector2D(v.x/200+.1,v.y/200+.2) end
end
local x,y=P:MapPosition(42,.2,.7,10)
assert(x==.2 and y==.55,'zone pin projects onto broader map')
assert(not P:MapPosition(42,.2,.7,99),'unrelated map stays empty')
assert(not P:MapPosition(42,.2,.7,11),'missing conversion stays empty')
C_Map.GetMapPosFromWorldPos=function() return CreateVector2D(.9,.9) end
assert(not P:MapPosition(42,.2,.7,10),'mismatched inverse conversion stays empty')
''')
print('PASS: map projection and unrelated-map safety')
