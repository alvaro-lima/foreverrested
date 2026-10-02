"""Class, reward-quality and equipped-gear checks for the swords marker."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
ns={'__file__':str(root/'tests/validate.py')}
exec((root/'tests/validate.py').read_text().split("lua.execute(r'''\nF.LoadDatabase()",1)[0],ns)
ns['lua'].execute(r'''
local class,level='SHAMAN',20
function UnitClass() return class,class end
function UnitLevel() return level end
local items={
 [1]={quality=2,required=10,equip='INVTYPE_CHEST',class=4,subclass=2,stats={ITEM_MOD_INTELLECT_SHORT=5}},
 [2]={quality=2,required=10,equip='INVTYPE_CHEST',class=4,subclass=2,stats={ITEM_MOD_INTELLECT_SHORT=10}},
 [3]={quality=2,required=10,equip='INVTYPE_WEAPON',class=2,subclass=7,stats={ITEM_MOD_DAMAGE_PER_SECOND_SHORT=30}},
 [4]={quality=2,required=10,equip='INVTYPE_CHEST',class=4,subclass=3,stats={ITEM_MOD_INTELLECT_SHORT=10}},
 [5]={quality=1,required=1,equip='INVTYPE_CHEST',class=4,subclass=2,stats={ITEM_MOD_INTELLECT_SHORT=20}},
 [6]={quality=2,required=30,equip='INVTYPE_CHEST',class=4,subclass=2,stats={ITEM_MOD_INTELLECT_SHORT=20}},
 [7]={quality=2,required=1,equip='INVTYPE_CHEST',class=4,subclass=1,stats={ITEM_MOD_STRENGTH_SHORT=10}},
 [8]={quality=2,required=1,equip='',class=9,subclass=0,stats={}},
 [9]={quality=2,required=10,equip='INVTYPE_2HWEAPON',class=2,subclass=5,stats={ITEM_MOD_DAMAGE_PER_SECOND_SHORT=10}},
 [10]={quality=2,required=10,equip='INVTYPE_WEAPON',class=2,subclass=4,stats={ITEM_MOD_DAMAGE_PER_SECOND_SHORT=9}},
 [11]={quality=2,required=10,equip='INVTYPE_SHIELD',class=4,subclass=6,stats={ITEM_MOD_STAMINA_SHORT=10}},
}
local equipped={[5]=1}
function GetInventoryItemLink(_,slot) return equipped[slot] end
function GetItemInfo(id)
 local i=items[id]; if not i then return end
 return 'Item '..id,id,i.quality,1,i.required,'','',1,i.equip,0,0,i.class,i.subclass
end
function GetItemStats(id) return items[id] and items[id].stats end
local usable=true
function IsUsableItem() return usable end
F.LoadDatabase()
local G=F.GearRewards
assert(G:Useful({itemID=2}),'class-appropriate intellect upgrade')
assert(not G:Useful({itemID=1}),'same equipment is not an upgrade')
assert(not G:Useful({itemID=3}),'shaman cannot equip swords')
assert(not G:Useful({itemID=4}),'level-20 shaman cannot equip mail')
assert(not G:Useful({itemID=5}),'common armor is not a notable gear detour')
assert(not G:Useful({itemID=6}),'reward level too high')
assert(not G:Useful({itemID=8}),'recipes are not gear')
assert(not G:Useful({itemID=99}),'uncached reward stays unmarked')
usable=false; assert(not G:Useful({itemID=2}),'unlearned proficiency'); usable=true
equipped[5]=2; assert(not G:Useful({itemID=1}),'reward worse than current gear')
equipped[5]=99; assert(not G:Useful({itemID=2}),'unknown equipped item prevents speculative upgrade')
class='MAGE'; equipped[5]=nil
assert(not G:Useful({itemID=2}),'mage cannot equip leather')
assert(not G:Useful({itemID=7}),'strength-only armor is not useful to mage')
class='SHAMAN'; equipped[16]=10; equipped[17]=11
assert(not G:Useful({itemID=9}),'two-hander must beat main hand plus off hand')
equipped[17]=nil; assert(G:Useful({itemID=9}),'meaningful two-handed weapon upgrade')
class='SHAMAN'; level=40; equipped[5]=1
assert(G:Useful({itemID=4}),'mail becomes eligible at level40')
F.AllianceQuestData[999001]={rewards={{itemID=2}}}
assert(F.UI:TaskPriority({questID=999001})=='Gear')
equipped[5]=2
assert(F.UI:TaskPriority({questID=999001})==nil,'marker updates when gear is equipped')
assert(F.UI:TaskPriority({questID=999001,critical=true})=='Critical')
''')
print('PASS: class compatibility, proficiency, levels, meaningful upgrades, unknown data and dynamic gear markers')
