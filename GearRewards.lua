local _, F = ...
local G = {requested={}}
F.GearRewards=G
-- Conservative leveling estimates, not a spec-specific best-in-slot list.
local weights={
 WARRIOR={str=2,agi=1,sta=1}, PALADIN={str=2,int=1,sta=1},
 HUNTER={agi=2,sta=1,int=.5}, ROGUE={agi=2,str=1,sta=1},
 SHAMAN={str=1.5,agi=1,int=1.5,spi=.5,sta=1}, DRUID={str=1,agi=1,int=1.5,spi=1,sta=1},
 MAGE={int=2,spi=1,sta=.5}, WARLOCK={int=2,spi=.5,sta=1}, PRIEST={int=2,spi=2,sta=.5},
}
local weapons={
 WARRIOR={[0]=true,[1]=true,[2]=true,[3]=true,[4]=true,[5]=true,[6]=true,[7]=true,[8]=true,[10]=true,[13]=true,[15]=true,[16]=true,[18]=true},
 PALADIN={[0]=true,[1]=true,[4]=true,[5]=true,[6]=true,[7]=true,[8]=true},
 HUNTER={[0]=true,[1]=true,[2]=true,[3]=true,[6]=true,[7]=true,[8]=true,[10]=true,[13]=true,[15]=true,[16]=true,[18]=true},
 ROGUE={[2]=true,[3]=true,[4]=true,[7]=true,[13]=true,[15]=true,[16]=true,[18]=true},
 SHAMAN={[0]=true,[1]=true,[4]=true,[5]=true,[10]=true,[13]=true,[15]=true},
 DRUID={[4]=true,[5]=true,[10]=true,[13]=true,[15]=true},
 MAGE={[7]=true,[10]=true,[15]=true,[19]=true},
 WARLOCK={[7]=true,[10]=true,[15]=true,[19]=true}, PRIEST={[4]=true,[10]=true,[15]=true,[19]=true},
}
local slots={INVTYPE_HEAD={1},INVTYPE_NECK={2},INVTYPE_SHOULDER={3},INVTYPE_CHEST={5},INVTYPE_ROBE={5},
 INVTYPE_WAIST={6},INVTYPE_LEGS={7},INVTYPE_FEET={8},INVTYPE_WRIST={9},INVTYPE_HAND={10},
 INVTYPE_FINGER={11,12},INVTYPE_TRINKET={13,14},INVTYPE_CLOAK={15},INVTYPE_WEAPON={16},
 INVTYPE_2HWEAPON={16},INVTYPE_WEAPONMAINHAND={16},INVTYPE_WEAPONOFFHAND={17},INVTYPE_SHIELD={17},
 INVTYPE_HOLDABLE={17},INVTYPE_RANGED={18},INVTYPE_RANGEDRIGHT={18},INVTYPE_THROWN={18}}
local statNames={str='ITEM_MOD_STRENGTH_SHORT',agi='ITEM_MOD_AGILITY_SHORT',int='ITEM_MOD_INTELLECT_SHORT',
 spi='ITEM_MOD_SPIRIT_SHORT',sta='ITEM_MOD_STAMINA_SHORT',armor='RESISTANCE0_NAME',dps='ITEM_MOD_DAMAGE_PER_SECOND_SHORT'}
local function api(name) return _G[name] or C_Item and C_Item[name] end
function G:Info(id,facts)
 local name,link,quality,level,required,_,_,_,equip,_,_,class,subclass=F.Call(api('GetItemInfo'),id)
 if not name then
  if C_Item and C_Item.RequestLoadItemDataByID and type(id)=='number' and not self.requested[id] then
   self.requested[id]=true; F.Call(C_Item.RequestLoadItemDataByID,id)
  end
  return nil
 end
 local live=F.Call(api('GetItemStats'),link or id)
 if not live and not facts then return nil end
 local stats={}
 for key,value in pairs(facts and facts.stats or {}) do stats[key]=value end
 for key,token in pairs(statNames) do if live and live[token] then stats[key]=live[token] end end
 return {id=id,quality=quality,required=required,equip=equip,class=class,subclass=subclass,stats=stats}
end
function G:Score(item,class)
 local score=0
 for stat,weight in pairs(weights[class] or {}) do score=score+(item.stats[stat] or 0)*weight end
 if item.class==2 then
  local caster=class=='MAGE' or class=='WARLOCK' or class=='PRIEST'
  local ranged=item.equip=='INVTYPE_RANGED' or item.equip=='INVTYPE_RANGEDRIGHT' or item.equip=='INVTYPE_THROWN'
  if not caster and class~='DRUID' and (class~='HUNTER' or ranged) or item.subclass==19 then
   if not item.stats.dps then return nil end
   score=score+item.stats.dps*5
  end
 end
 return score
end
function G:Useful(reward)
 local _,class=F.Call(UnitClass,'player')
 local level=F.Call(UnitLevel,'player') or 1
 if not weights[class] then return false end
 local item=self:Info(reward.itemID,reward)
 if not item or not item.quality or item.quality<2 or (item.required or 0)>level then return false end
 if item.class==2 then
  if not weapons[class][item.subclass] then return false end
 elseif item.class==4 then
  local cap=({WARRIOR=level>=40 and 4 or 3,PALADIN=level>=40 and 4 or 3,
   HUNTER=level>=40 and 3 or 2,SHAMAN=level>=40 and 3 or 2,ROGUE=2,DRUID=2})[class] or 1
  if not item.subclass then return false end
  if item.subclass==6 then
   if class~='WARRIOR' and class~='PALADIN' and class~='SHAMAN' then return false end
  elseif item.subclass>cap then return false end
 else return false end
 -- Let the live client enforce learned proficiencies and Forever changes.
 if F.Call(api('IsUsableItem'),reward.itemID)~=true then return false end
 local candidate=self:Score(item,class)
 if not candidate or candidate<=0 or not slots[item.equip] or not GetInventoryItemLink then return false end
 for _,slot in ipairs(slots[item.equip]) do
  local link=F.Call(GetInventoryItemLink,'player',slot)
  local current=0
  if link then
   local equipped=self:Info(link)
   current=equipped and self:Score(equipped,class)
  end
  -- Compare a two-hander against the whole equipped weapon set.
  if current and item.equip=='INVTYPE_2HWEAPON' then
   local offhand=F.Call(GetInventoryItemLink,'player',17)
   if offhand then local other=self:Info(offhand); local score=other and self:Score(other,class)
    current=score and current+score or nil
   end
  end
  if current and candidate>=current+math.max(1,current*.1) then return true end
 end
 return false
end
function G:QuestUseful(id)
 local data=F.GuideEngine:Metadata(id) or {}
 for _,reward in ipairs(data.rewards or {}) do if self:Useful(reward) then return true end end
 return false
end
