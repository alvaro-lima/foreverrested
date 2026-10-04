local _,F=...
local D,L=F.GuideDraft,F.GuideLibrary
-- Unreliable rare loot and the bought-tube / high-level ogre branch are bonuses.
local optionalAudit={[470]=true,[174]=true,[175]=true,[177]=true,[181]=true}
-- Finish the normal worgen chain at 29; its enemies are locally level 29-31.
local requiredAudit={[222]=true,[223]=true,[1093]=true}
local function recovery(g,id,target)
 local p=assert(F.Audit2030Recovery[g.id])
 if p.early and target<=23 then p=p.early end
 return {id=id,type='grind',levelRecovery=true,targetLevel=target,
  zone=p.zone,x=p.x,y=p.y,
  text='Required XP recovery: reach level '..target..' - '..p.name,
  note='If below level '..target..', fight suitable '..p.name..' with safe single pulls. These local reference enemies are level '..p.minLevel..'-'..p.maxLevel..'. Choose enemies that still grant XP; avoid named or elite pulls. This step uses actual level and completes automatically at '..target..'. Optional quest XP is not assumed. Skip explicitly bypasses it.'}
end
local function auditProgression(g)
 local steps,threshold={},g.minLevel
 for _,s in ipairs(g.steps) do
  if s.questID and requiredAudit[s.questID] then
   s.optional=nil;s.activeOnly=nil
   local tasks={};for _,t in ipairs(s.tasks or {}) do local c={};for k,v in pairs(t) do c[k]=v end;c.optional=nil;c.activeOnly=nil;tasks[#tasks+1]=c end
   if s.tasks then s.tasks=tasks end
  end
  if s.questID and optionalAudit[s.questID] then
   s.optional=true;s.activeOnly=nil
   local tasks={};for _,t in ipairs(s.tasks or {}) do local c={};for k,v in pairs(t) do c[k]=v end;c.optional=true;c.activeOnly=nil;tasks[#tasks+1]=c end
   if s.tasks then s.tasks=tasks end
   s.note=(s.note or '')..' Optional audit branch: its XP is excluded from required progression.'
  end
  if s.type=='pickup' and s.questID and not s.optional and not s.classes then
   local level=F.AllianceQuestData[s.questID].minLevel or 1
   if level>threshold and level<=30 then steps[#steps+1]=recovery(g,'xp-before:'..s.id,level);threshold=level end
  end
  steps[#steps+1]=s
 end
 steps[#steps+1]=recovery(g,'xp-exit:'..g.id,g.maxLevel)
 g.steps=steps;g.revision=(g.id=='alliance-kalimdor-20-24' or g.id=='alliance-kalimdor-24-27') and 7 or 6
end
-- Short visits built from our own sourced quest circuits, never third-party routes.
local function append(g,source,startKey,endKey)
    local active=startKey==nil
    for _,step in ipairs(L.guides[source].steps) do
        local key=step.legacyGroupID or step.id
        if key==endKey then break end
        if key==startKey then active=true end
        if active and step.id~='entry-class' and (step.type~='grind' or step.id=='ashenvale-before-foulweald')
            and not step.id:find('%-finish$') and not step.id:find('%-class30$')
            and not (g.id=='alliance-kalimdor-20-24' and
             (key=='stonetalon-city-detours' or (key=='stonetalon-side-work' and step.questID~=1093))) then
            local copy={};for k,v in pairs(step) do copy[k]=v end
            if step.id=='ashenvale-before-foulweald' then
                copy=recovery(g,step.id,23)
            end
            g.steps[#g.steps+1]=copy
        end
    end
end
local wet='alliance-wetlands-20-30'
local dusk='alliance-duskwood-20-30'
local ash='alliance-ashenvale-20-30'
local specs={
 {'eastern-20-22','20-22 Wetlands: Coast and Greenwarden',wet,'algaz-entry','greenwarden-fire-pickup',20,22,'Wetlands'},
 {'eastern-22-24','22-24 Duskwood: road and introductions',dusk,'redridge-cleanup','darkshire-second-pickup',22,24,'Duskwood'},
 {'eastern-24-25','24-25 Wetlands: gnolls and excavation',wet,'greenwarden-fire-pickup','wetlands-level24',24,25,'Wetlands'},
 {'eastern-25-26','25-26 Duskwood: Raven Hill investigations',dusk,'darkshire-second-pickup','duskwood-train26',25,26,'Duskwood'},
 {'eastern-26-27','26-27 Wetlands: relics and coastal goods',wet,'ormer-second-pickup','wetlands-level27',26,27,'Wetlands'},
 {'eastern-27-28','27-28 Duskwood: worgen and the hermit',dusk,'duskwood-train26','duskwood-level28',27,28,'Duskwood'},
 {'eastern-28-29','28-29 Wetlands: shipwrecks and final raptors',wet,'cursed-crew-objectives','wetlands-train28',28,29,'Wetlands'},
 {'eastern-29-30','29-30 Duskwood: final patrols',dusk,'night-watch-final-pickup','duskwood-level30',29,30,'Duskwood'},
 {'kalimdor-20-24','20-24 Ashenvale / Stonetalon: introductions',ash,'ashenvale-arrival','ashenvale-train24',20,24,'Ashenvale'},
 {'kalimdor-24-27','24-27 Ashenvale: eastern camps',ash,'culling-threat-objectives','ashenvale-level27',24,27,'Ashenvale'},
 {'kalimdor-27-30','27-30 Ashenvale: cleansing and lake circuits',ash,'raene-first-components-pickup','ashenvale-level30',27,30,'Ashenvale'},
}
for i,spec in ipairs(specs) do
    local g=D:New('alliance-'..spec[1],spec[2],spec[8],{},spec[6],spec[7])
    g.actionSteps=true;g.revision=2;g.sourceGuideID=spec[3]
    g.routeGroup=i<=8 and 'eastern-20-30' or 'kalimdor-20-30'
    g.description='Quest circuits plus required combat recovery; quest XP alone does not fill the stated level band. Optional loot, group and equipment-dependent branches are bonus XP.'
    append(g,spec[3],spec[4],spec[5])
    if i==9 then
        local circuit,remaining={},{}
        for _,step in ipairs(g.steps) do
            if step.questID==1093 then circuit[#circuit+1]=step
            else remaining[#remaining+1]=step end
        end
        for index,step in ipairs(remaining) do
            if step.questID==1071 and step.type=='turnin' then
                for number,action in ipairs(circuit) do table.insert(remaining,index+number,action) end
                break
            end
        end
        g.steps=remaining
    end
    -- New Forever quests get real actions, rather than a hidden optional bundle.
    if i==1 then
        for _,id in ipairs({98197,98282}) do
            for _,kind in ipairs({'pickup','objective','turnin'}) do
                local task=D:Task(kind,id,true)
                task.activeOnly=nil
                task.id='forever-wetlands:'..id..':'..kind
                task.text=({pickup='Accept ',objective='Complete ',turnin='Turn in '})[kind]..F.AllianceQuestData[id].title
                g.steps[#g.steps+1]=task
            end
        end
    end
    if i~=8 and i~=11 then g.nextGuideID='alliance-'..specs[i+1][1] end
    if i==8 or i==11 then
        D:Note(g,'route-finish:'..g.routeGroup,'Regional route finished','Check your actual level. Finish accepted objectives or select the other regional route for unfinished quests if below 30. Group quests remain optional.')
    end
    auditProgression(g)
    L:Register(g)
end
-- Retired circuits remain readable for migration but are absent from the chooser.
for _,id in ipairs({wet,dusk,ash,'alliance-eastern-20-25','alliance-eastern-25-30'}) do
    if L.guides[id] then L.guides[id].retired=true end
end
