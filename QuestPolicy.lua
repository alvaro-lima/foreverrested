local _, F = ...
local baseline = F.ClassicQuestPolicy or {records={},unlocks={}}
local current = F.ForeverQuestPolicy or {records={},unlocks={}}
local P = {vanilla=baseline.records, forever=current.records, unlocks=baseline.unlocks, foreverUnlocks=current.unlocks}
F.QuestPolicy = P
local raceBits = {Human=1,Orc=2,Dwarf=4,NightElf=8,Scourge=16,Tauren=32,Gnome=64,Troll=128}
function P:Record(id)
    if self.forever[id] ~= nil then return self.forever[id] or {} end
    return self.vanilla[id] or {}
end
function P:Eligible(id, task)
    local record, eligibility = self:Record(id), {}
    for key,value in pairs(task or {}) do eligibility[key]=value end
    eligibility.activeOnly=nil
    eligibility.classes=eligibility.classes or record.classes
    if eligibility.classes and #eligibility.classes==0 then eligibility.classes=nil end
    eligibility.minLevel=eligibility.minLevel or record.minLevel
    eligibility.requiredRaces=eligibility.requiredRaces or record.requiredRaces
    local mask=eligibility.requiredRaces
    if mask and mask>0 and mask<2^32 then
        local _,race=F.Call(UnitRace,'player')
        if not raceBits[race] then return false end
    end
    return F.GuideEngine:Applies(eligibility)
end
function P:UnlockApplies(unlock)
    local _,class=F.Call(UnitClass,'player')
    local _,race=F.Call(UnitRace,'player')
    local level=F.Call(UnitLevel,'player')
    if class~=unlock.class or not F.Number(level) or level<unlock.level then return false end
    if unlock.raceTokens then
        for _,token in ipairs(unlock.raceTokens) do if race==token then return true end end
        return false
    end
    local bit=raceBits[race]
    return unlock.races==0 or bit and math.floor(unlock.races/bit)%2==1
end
function P:Satisfied(id)
    if F.QuestLog:TurnedIn(id) then return true end
    for _,alternate in ipairs(self:Record(id).exclusiveTo or {}) do
        if F.QuestLog:TurnedIn(alternate) then return true end
    end
    return false
end
function P:Critical(task)
    local id=F.GuideEngine:Resolve(task)
    if id and F.db.manualSkippedSteps and F.db.manualSkippedSteps['catchup:'..id..':turnin'] then return false end
    local record=self:Record(id)
    return (task.critical or record.critical or self.requiredQuests and self.requiredQuests[id])
        and self:Eligible(id,task) or false
end
function P:PrepareGuide()
    local guide,skipped=F.Guide,{}
    for index,step in ipairs(guide.steps) do
        if F.db.skipped[index] then skipped[step.id]=true end
    end
    guide.authoredSteps=guide.authoredSteps or guide.steps
    guide.steps=guide.authoredSteps
    F.db.skipped={}
    for index,step in ipairs(guide.steps) do if skipped[step.id] then F.db.skipped[index]=true end end
    self.requiredQuests,self.requiredOrder,self.activeParents,self.issues={},{},{},{}
end
function P:ProtectedSteps(boundary)
    local protected,quests,visited,visiting,order,activeParents={},{},{},{},{},{}
    local tasksByID,positions={},{}
    for index,step in ipairs(F.Guide.steps) do
        for _,task in ipairs(step.tasks or {step}) do
            local id=F.GuideEngine:Resolve(task)
            if id then
                if not tasksByID[id] or task.prerequisites or task.prerequisitesAny or task.critical then tasksByID[id]=task end
                positions[id]=positions[id] or index
            end
        end
    end
    local function choose(ids)
        for _,id in ipairs(ids) do if self:Satisfied(id) then return nil,true end end
        for _,id in ipairs(ids) do if self.forever[id]~=false and self:Eligible(id,tasksByID[id]) and F.QuestLog.byID[id] then return id end end
        local best
        for _,id in ipairs(ids) do
            if self.forever[id]~=false and self:Eligible(id,tasksByID[id]) and positions[id] and (not best or positions[id]<positions[best]) then best=id end
        end
        if best then return best end
        for _,id in ipairs(ids) do if self.forever[id]~=false and self:Eligible(id,tasksByID[id]) then return id end end
        local disabled=true
        for _,id in ipairs(ids) do if self.forever[id]~=false then disabled=false end end
        return nil,disabled
    end
    local requireQuest
    local function alternatives(ids,reason,force)
        if not ids or #ids==0 then return end
        local id,satisfied=choose(ids)
        if id then requireQuest(id,reason,force)
        elseif not satisfied then self.issues[#self.issues+1]='No applicable prerequisite alternative: '..table.concat(ids,', ') end
    end
    requireQuest=function(id,reason,force)
        if not id or self:Satisfied(id) then return end
        -- A prerequisite still ahead in the retained route will be handled in
        -- authored order. Recover only bypassed/missing ancestors, or unlocks.
        if not force and positions[id] and positions[id]>=boundary then return end
        if visiting[id] then self.issues[#self.issues+1]='Cyclic prerequisite data at quest '..id; return end
        if visited[id] then return end
        if not self:Eligible(id,tasksByID[id]) then
            self.issues[#self.issues+1]='Prerequisite '..id..' is unavailable for this class, race or level'; return
        end
        local record,task=self:Record(id),tasksByID[id] or {}
        visited[id],visiting[id],quests[id]=true,true,reason
        -- An accepted descendant proves its acceptance prerequisites were met;
        -- do not send the player back through unflagged/repeatable ancestors.
        if not F.QuestLog.byID[id] then
            for _,prior in ipairs(task.prerequisites or record.prerequisites or {}) do requireQuest(prior,'Prerequisite for quest '..id,true) end
            alternatives(task.prerequisitesAny or record.prerequisitesAny,'Prerequisite for quest '..id,true)
        end
        local parent=task.parentQuest or record.parentQuest
        if parent and parent>0 and not F.QuestLog.byID[parent] and not self:Satisfied(parent) then
            activeParents[parent]=true; requireQuest(parent,'Keep quest '..parent..' active for quest '..id,true)
        end
        visiting[id]=nil
        order[#order+1]=id
    end
    if F.Guide.status~='test' then
        local seen={}
        for _,unlock in ipairs(self.unlocks) do
            seen[unlock.key]=true
            local override=self.foreverUnlocks[unlock.key]
            if override~=false then
                unlock=override or unlock
                if self:UnlockApplies(unlock) then alternatives(unlock.terminals,unlock.reason,true) end
            end
        end
        local additions={}
        for key,unlock in pairs(self.foreverUnlocks) do
            if not seen[key] and type(unlock)=='table' then additions[#additions+1]=key end
        end
        table.sort(additions)
        for _,key in ipairs(additions) do
            local unlock=self.foreverUnlocks[key]
            if self:UnlockApplies(unlock) then alternatives(unlock.terminals,unlock.reason,true) end
        end
    end
    for index,step in ipairs(F.Guide.steps) do
        if step.critical and F.GuideEngine:Applies(step) then protected[index]=step.criticalReason or 'Essential checkpoint' end
        for _,task in ipairs(step.tasks or {step}) do
            local id=F.GuideEngine:Resolve(task)
            local record=self:Record(id)
            if (task.critical or record.critical) and self:Eligible(id,task) then
                requireQuest(id,task.criticalReason or record.reason or 'Essential quest',true)
            end
            local level=F.Call(UnitLevel,'player')
            local due=not record.minLevel or F.Number(level) and level>=record.minLevel
            if index>=boundary and id and due and not task.optional and F.GuideEngine:Applies(task)
                and not F.db.skipped[index] and not F.QuestLog:TurnedIn(id) and not F.QuestLog.byID[id] then
                for _,prior in ipairs(task.prerequisites or record.prerequisites or {}) do requireQuest(prior,'Prerequisite for quest '..id) end
                alternatives(task.prerequisitesAny or record.prerequisitesAny,'Prerequisite for quest '..id)
                local parent=task.parentQuest or record.parentQuest
                if parent and parent>0 and not F.QuestLog.byID[parent] and not self:Satisfied(parent) then
                    activeParents[parent]=true; requireQuest(parent,'Required active parent for quest '..id)
                end
            end
        end
        for _,task in ipairs(step.alongside or {}) do
            local id=F.GuideEngine:Resolve(task)
            local record=self:Record(id)
            if (task.critical or record.critical) and self:Eligible(id,task) and not F.QuestLog:TurnedIn(id) then
                protected[index]=task.criticalReason or record.reason or 'Essential class quest'
                requireQuest(id,protected[index],true)
            end
        end
    end
    for index,step in ipairs(F.Guide.steps) do
        for _,task in ipairs(step.tasks or {step}) do
            local id=F.GuideEngine:Resolve(task)
            if id and quests[id] and self:Eligible(id,task) and (not activeParents[id] or task.type=='pickup') then protected[index]=quests[id] end
        end
    end
    self.requiredQuests,self.requiredOrder,self.activeParents=quests,order,activeParents
    return protected
end
function P:InsertRecovery(boundary,protected)
    if F.Guide.status=='test' then return boundary,protected end
    local prefix,reasons,skipped={},{},{}
    if #self.issues>0 then
        prefix[1]={id='catchup:review',type='note',critical=true,confirmOnNext=true,
            text='Review quest prerequisites',note=table.concat(self.issues,'; ')..'. Check these before continuing; Next acknowledges this review.'}
        reasons[1]='Incomplete prerequisite data'
    end
    for _,id in ipairs(self.requiredOrder or {}) do
        local record=self:Record(id)
        for _,kind in ipairs(self.activeParents[id] and {'pickup'} or {'pickup','objective','turnin'}) do
            prefix[#prefix+1]={id='catchup:'..id..':'..kind,type=kind,questID=id,
                critical=true,criticalReason=self.requiredQuests[id],recovery=true,
                text=(kind=='objective' and 'Complete ' or '')..((F.GuideEngine:Metadata(id) or record).title or ('Quest '..id))}
            reasons[#prefix]=self.requiredQuests[id]
        end
    end
    local count=#prefix
    if count==0 then return boundary,protected end
    for index,step in ipairs(F.Guide.steps) do
        prefix[#prefix+1]=step
        reasons[count+index]=protected[index]
        if F.db.skipped[index] then skipped[count+index]=true end
    end
    F.Guide.steps,F.db.skipped=prefix,skipped
    return boundary+count,reasons
end
