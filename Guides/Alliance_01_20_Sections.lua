local _,F=...
local D,L=F.GuideDraft,F.GuideLibrary
local specs={
 {'coldridge-01-05','1-5 Coldridge Valley','alliance-dun-morogh-01-10',nil,'pass-mail',1,5,'Dun Morogh','dun-morogh-05-10'},
 {'dun-morogh-05-10','5-8 Dun Morogh: Kharanos circuits','alliance-dun-morogh-01-10','pass-mail','kharanos-refresh',5,8,'Dun Morogh','dun-morogh-east-08-10'},
 {'dun-morogh-east-08-10','8-10 Dun Morogh: quarry and eastern road','alliance-dun-morogh-01-10','kharanos-refresh',nil,8,10,'Dun Morogh','loch-west-10-13'},
 {'northshire-01-05','1-5 Northshire','alliance-elwynn-01-10',nil,'goldshire-mail-pickup',1,5,'Elwynn Forest','elwynn-05-10'},
 {'elwynn-05-10','5-10 Elwynn Forest','alliance-elwynn-01-10','goldshire-mail-pickup',nil,5,10,'Elwynn Forest','westfall-10-15'},
 {'shadowglen-01-05','1-5 Shadowglen','alliance-teldrassil-01-10',nil,'dolanaar-mail-pickup',1,5,'Teldrassil','teldrassil-05-10'},
 {'teldrassil-05-10','5-10 Teldrassil','alliance-teldrassil-01-10','dolanaar-mail-pickup',nil,5,10,'Teldrassil','darkshore-10-13'},
 {'zephras-grove-01-05','1-5 Zephras: Thendal Grove','alliance-zephras-01-10',nil,'next-step-pickup',1,5,'Zephras Isle','zephras-village-05-08'},
 {'zephras-village-05-08','5-8 Zephras: village and highlands','alliance-zephras-01-10','next-step-pickup','valanaar-pickup',5,8,'Zephras Isle','zephras-west-08-10'},
 {'zephras-west-08-10','8-10 Zephras: Windfield and scholar','alliance-zephras-01-10','valanaar-pickup',nil,8,10,'Zephras Isle','zephras-10-14-route'},
 {'westfall-10-15','10-12 Westfall: farms and first militia','alliance-westfall-10-20',nil,'militia-second-pickup',10,12,'Westfall','westfall-militia-12-15'},
 {'westfall-militia-12-15','12-15 Westfall: militia and Defias','alliance-westfall-10-20','militia-second-pickup','westfall-redridge-train',12,15,'Westfall','redridge-human-15-20'},
 {'redridge-human-15-20','15-20 Redridge (Westfall arrival)','alliance-westfall-10-20','westfall-redridge-train',nil,15,20,'Redridge Mountains','eastern-20-22'},
 {'loch-west-10-13','10-13 Loch Modan: western shore','alliance-loch-modan-10-20',nil,'excavation-pickup',10,13,'Loch Modan','loch-east-13-15'},
 {'loch-east-13-15','13-15 Loch Modan: excavation and lodge','alliance-loch-modan-10-20','excavation-pickup','loch-redridge-train',13,15,'Loch Modan','redridge-dwarf-15-20'},
 {'redridge-dwarf-15-20','15-20 Redridge (Loch Modan arrival)','alliance-loch-modan-10-20','loch-redridge-train',nil,15,20,'Redridge Mountains','eastern-20-22'},
 {'darkshore-10-13','10-13 Darkshore: coast and ruins','alliance-darkshore-10-20',nil,'north-pickup',10,13,'Darkshore','darkshore-13-17'},
 {'darkshore-13-17','13-17 Darkshore: northern circuits','alliance-darkshore-10-20','north-pickup','mathystra-pickup',13,17,'Darkshore','darkshore-17-20'},
 {'darkshore-17-20','17-20 Darkshore: ruins and final work','alliance-darkshore-10-20','mathystra-pickup',nil,17,20,'Darkshore','kalimdor-20-24'},
 {'zephras-10-14-route','10+ Zephras: service and wind','alliance-zephras-10-14',nil,'tower-intro-pickup',10,14,'Zephras Isle','zephras-tower-12-14'},
 {'zephras-tower-12-14','10+ Zephras: tower and village','alliance-zephras-10-14','tower-intro-pickup','hermit-hunts',10,14,'Zephras Isle','zephras-exit-12-14'},
 {'zephras-exit-12-14','10+ Zephras: optional work and exit','alliance-zephras-10-14','hermit-hunts',nil,10,14,'Zephras Isle','westfall-10-15'},
}
local prepared={}
local demotedLochIDs={
 [257]={pickup='lodge-pickup:pickup:257',objective='lodge-loop:objective:257',turnin='lodge-return:turnin:257'},
 [258]={pickup='lodge-challenge-pickup',objective='lodge-challenge-objectives',turnin='lodge-challenge-return'},
 [217]={pickup='south-final-pickup',objective='south-final-objectives',turnin='south-final-return'},
}
local combatSafetyLevels={[9]=12,[14]=15,[237]=11,[263]=12,[963]=13}
local promotedStarterQuests={
 ['alliance-dun-morogh-01-10']={[315]=true},
 ['alliance-elwynn-01-10']={[83]=true,[5545]=true},
 ['alliance-teldrassil-01-10']={[488]=true,[489]=true,[997]=true,[487]=true,[2541]=true,[2561]=true},
 ['alliance-westfall-10-20']={[151]=true,[22]=true,[102]=true,[153]=true,[3741]=true,[127]=true},
 ['alliance-loch-modan-10-20']={[3741]=true,[127]=true},
 ['alliance-darkshore-10-20']={[3524]=true,[963]=true,[958]=true},
}
-- Explicit local fallback for shortfalls; optional quests never supply assumed XP.
-- Quest identities select sourced areas only, without scheduling extra objectives.
local starterRecovery={
 ['coldridge-01-05']={182,'Frostmane Troll Whelps outside the southern cave'},
 ['dun-morogh-05-10']={319,'Ice Claw Bears and Elder Crag Boars on the western circuit'},
 ['dun-morogh-east-08-10']={432,'Rockjaw Skullthumpers around Gol\'Bolar Quarry'},
 ['northshire-01-05']={21,'Kobold Laborers at Echo Ridge'},
 ['elwynn-05-10']={11,'Riverpaw Runts and Outrunners near Westbrook'},
 ['shadowglen-01-05']={916,'Webwood Spiders outside the cave'},
 ['teldrassil-05-10']={2459,'Gnarlpine Mystics near Starbreeze Village'},
 ['zephras-grove-01-05']={92470,'Ursera Scavengers west of Thendal Grove'},
 ['zephras-village-05-08']={92517,'Highlands Bandits near the village'},
 ['zephras-west-08-10']={92682,'Hungry Bandits on the Windfield circuit'},
 ['westfall-10-15']={12,'Defias Trappers and Smugglers on the northern farm circuit'},
 ['westfall-militia-12-15']={13,'Defias Looters outside Moonbrook; avoid pulling Pillager groups'},
 ['redridge-human-15-20']={122,'Redridge Whelps on the eastern road'},
 ['loch-west-10-13']={224,'Stonesplinter Troggs and Scouts near the southern gate'},
 ['loch-east-13-15']={385,'Loch Crocolisks on the eastern shore'},
 ['redridge-dwarf-15-20']={122,'Redridge Whelps on the eastern road'},
 ['darkshore-10-13']={985,'Blackwood Pathfinders and Windtalkers on the nearby furbolg circuit',983,'Pygmy Tide Crawlers on the beach south of Auberdine'},
 ['darkshore-13-17']={1002,'Moonstalkers along the northern road'},
 ['darkshore-17-20']={1003,'Grizzled Thistle Bears on the southern road'},
}
local function recoveryStep(g,key,target,questID,label)
 local data=F.AllianceQuestData[questID];local point
 for _,p in ipairs(data.locations or {}) do
  if (p.role=='requirement' or p.role=='sourcerequirement') and p.entityType==1 then point=p;break end
 end
 return {id=key,type='grind',targetLevel=target,levelRecovery=true,
  text='Required XP recovery: reach level '..target..' - '..label,
  zone=point and point.zone or g.zone,x=point and point.x,y=point and point.y,
  note='If below level '..target..', fight '..label..' with safe single pulls. Choose enemies that still grant XP and are suitable for your current level; avoid named or elite enemies. This step completes automatically at level '..target..'. Optional quests are bonus XP; none are assumed. Skip explicitly bypasses this recovery step.'}
end
local function starterLevelRecovery(g,spec)
 local fallback=starterRecovery[spec[1]]
 if not fallback then return end
 local actions,threshold,lastQuest,lastLabel={},g.minLevel,nil,nil
 for _,step in ipairs(g.steps) do
  local safe=step.type=='objective' and not step.optional and combatSafetyLevels[step.questID]
  if safe and safe>threshold then
   actions[#actions+1]=recoveryStep(g,'xp-combat:'..step.id,safe,fallback[1],fallback[2])
   threshold=safe
  end
  if step.type=='pickup' and step.questID and not step.optional then
   local data=F.AllianceQuestData[step.questID]
   local required=data and data.minLevel or 1
   if required>threshold then
    -- Use already scheduled, already visited combat areas for acceptance gaps.
    local source=lastQuest or fallback[3] or fallback[1]
    actions[#actions+1]=recoveryStep(g,'xp-before:'..step.id,required,source,lastLabel or fallback[4] or fallback[2])
    threshold=required
   end
  end
  actions[#actions+1]=step
  if step.type=='objective' and step.questID and not step.optional then
   local data=F.AllianceQuestData[step.questID]
   for _,p in ipairs(data and data.locations or {}) do
    if (p.role=='requirement' or p.role=='sourcerequirement') and p.entityType==1 then
     -- Special talk/escort objectives must never become grinding targets.
     for _,o in ipairs(data.objectives or {}) do
      if o.action=='kill' and o.id==p.entityID or o.action=='collect' and p.role=='sourcerequirement' and p.item==o.name then
       lastQuest,lastLabel=step.questID,p.name;break
      end
     end
     break
    end
   end
  end
 end
 actions[#actions+1]=recoveryStep(g,'xp-exit:'..g.id,g.maxLevel,fallback[1],fallback[2])
 g.steps=actions;g.revision=3
end
local function prepare(id)
 if prepared[id] then return prepared[id] end
 local source=L.guides[id];local core,emitted,result={},{},{}
 for _,s in ipairs(source.steps) do
  -- Retain the former optional action identity when local work becomes core.
  -- This preserves saved positions and explicit skips across the audit update.
  if s.questID and promotedStarterQuests[id] and promotedStarterQuests[id][s.questID] then
   s.id='optional:'..id..':'..s.type..':'..s.questID
  end
  local priorID=s.questID and F.EarlyAuditActionIDs and F.EarlyAuditActionIDs[id] and F.EarlyAuditActionIDs[id][s.type..':'..s.questID]
  if priorID then s.id=priorID end
  for _,t in ipairs(s.tasks or {s}) do
   if t.questID then core[t.type..':'..t.questID]=true end
  end
 end
 for _,s in ipairs(source.steps) do
  if s.type~='grind' and s.id~='finish' and not s.id:find('%-finish$') then
   local side=s.type~='trainer' and s.alongside or nil
   local retain=not side or #side==0 or s.tasks and #s.tasks>0 or s.type~='note' and s.type~='group'
   if retain then
    local copy={};for k,v in pairs(s) do copy[k]=v end
    if side then copy.alongside={} end
    result[#result+1]=copy
   end
   for _,t in ipairs(side or {}) do
    local key=t.type..':'..t.questID
    if not core[key] and not emitted[key] then
     local copy={};for k,v in pairs(t) do copy[k]=v end
     copy.id=id=='alliance-loch-modan-10-20' and demotedLochIDs[t.questID] and demotedLochIDs[t.questID][t.type] or 'optional:'..id..':'..key
     copy.legacyGroupID=s.legacyGroupID or s.id
     copy.activeOnly=nil;copy.note=s.note
     copy.text=({pickup='Accept ',objective='Complete ',turnin='Turn in '})[t.type]..F.AllianceQuestData[t.questID].title
     result[#result+1]=copy;emitted[key]=true
    end
   end
  end
 end
 prepared[id]=result;source.retired=true;return result
end
for _,spec in ipairs(specs) do
 local g=D:New('alliance-'..spec[1],spec[2],spec[8],{},spec[6],spec[7])
 g.actionSteps=true;g.revision=2;g.sourceGuideID=spec[3]
 g.routeGroup=(spec[8]=='Teldrassil' or spec[8]=='Darkshore') and 'kalimdor-20-30' or 'eastern-20-30'
 g.nextGuideID='alliance-'..spec[9]
 g.description=spec[8]=='Zephras Isle' and spec[6]>=10 and 'Optional island continuation from level 10. Story clusters do not promise level 12 or 14; leave when transport is available and continuing is no longer useful.' or 'Quest circuits plus required combat recovery; quest XP alone does not fill the stated level band. Optional XP is excluded.'
 local active=spec[4]==nil
 for _,s in ipairs(prepare(spec[3])) do
  local key=s.legacyGroupID or s.id
  if key==spec[5] then break end
  if key==spec[4] then active=true end
  if active then g.steps[#g.steps+1]=s end
 end
 assert(#g.steps>0,'Empty regional section '..g.id)
 starterLevelRecovery(g,spec)
 L:Register(g)
end
