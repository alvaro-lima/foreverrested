local _, F = ...
local L = {guides = {}, order = {}, brackets = {
    {min = 1, max = 10}, {min = 10, max = 20}, {min = 20, max = 30},
    {min = 30, max = 40}, {min = 40, max = 50}, {min = 50, max = 60},
}}
F.GuideLibrary = L
function L:BracketIndex(level)
    level = tonumber(level) or 1
    for index, bracket in ipairs(self.brackets) do
        if level < bracket.max then return index end
    end
    return #self.brackets
end
function L:GuidesForBracket(index)
    local result = {}
    local bracket = self.brackets[index]
    if not bracket then return result end
    for _, id in ipairs(self.order) do
        local guide = self.guides[id]
        if not guide.retired and guide.minLevel >= bracket.min and guide.minLevel < bracket.max and guide.maxLevel <= bracket.max then
            result[#result + 1] = id
        end
    end
    return result
end
function L:Register(guide)
    -- Published routes must supply explicit IDs; IDs survive insertions/reorders.
    guide.revision = guide.revision or 1
    if guide.status == "draft" and not guide.actionSteps then
        local actions = {}
        for _, group in ipairs(guide.steps) do
            if group.tasks and #group.tasks > 0 and not group.confirmOnNext then
                for _, task in ipairs(group.tasks) do
                    local step = {}
                    for key,value in pairs(group) do step[key] = value end
                    for key,value in pairs(task) do step[key] = value end
                    step.id = #group.tasks == 1 and group.id or group.id .. ":" .. task.type .. ":" .. task.questID
                    step.legacyGroupID = group.id
                    step.tasks, step.alongside = {task}, {}
                    local data = guide.questData and guide.questData[task.questID]
                    local action = ({pickup="Accept",objective="Complete",turnin="Turn in"})[task.type] or task.type
                    step.text = action .. ": " .. (data and data.title or task.text or "Quest")
                    step.clusterText = group.text
                    -- Other required actions already have their own numbered
                    -- rows. Repeating them as optional side work obscures which
                    -- action the completion badge describes.
                    for _,side in ipairs(group.alongside or {}) do step.alongside[#step.alongside+1] = side end
                    actions[#actions+1] = step
                end
            else actions[#actions+1] = group end
        end
        guide.steps, guide.actionSteps, guide.revision = actions, true, guide.revision * 100 + 2
    end
    local seen = {}
    for _, step in ipairs(guide.steps) do
        assert(type(step.id) == "string" and not seen[step.id], "Guide " .. guide.id .. " requires unique stable step IDs: " .. tostring(step.id))
        seen[step.id] = true
    end
    if not self.guides[guide.id] then self.order[#self.order + 1] = guide.id end
    self.guides[guide.id] = guide
end
function L:SaveCurrent()
    if not F.db.guideID then return end
    local guide, skippedIDs = self.guides[F.db.guideID], {}
    for index in pairs(F.db.skipped) do
        if guide.steps[index] then skippedIDs[guide.steps[index].id] = true end
    end
    local current = guide.steps[F.db.step]
    local saved = {step = F.db.step, stepID = current and (current.resumeStepID or current.id), revision = guide.revision,
        bindings = F.db.bindings, skipped = F.db.skipped, skippedIDs = skippedIDs, confirmedSteps = F.db.confirmedSteps,
        manualSkippedSteps = F.db.manualSkippedSteps, skipHistory = F.db.skipHistory, restartStepID = F.db.restartStepID}
    F.db.guides[F.db.guideID] = saved
    F.db.stepID, F.db.guideRevision, F.db.skippedIDs = saved.stepID, saved.revision, skippedIDs
end
function L:ApplyState(guide, saved)
    saved = saved or {}
    if F.QuestPolicy then F.QuestPolicy:EnsureUnlockSteps(guide) end
    if F.Travel and guide.faction then F.Travel:EnsureSteps(guide) end
    local index, skipped, confirmed = nil, {}, {}
    for position, step in ipairs(guide.steps) do
        if step.id == saved.stepID or not index and step.legacyGroupID == saved.stepID then index = position end
        if saved.skippedIDs and (saved.skippedIDs[step.id] or saved.skippedIDs[step.legacyGroupID]) then skipped[position] = true end
        if step.confirmOnNext and saved.confirmedSteps and saved.confirmedSteps[step.id] then confirmed[step.id] = true end
    end
    local revised = saved.revision ~= nil and saved.revision ~= guide.revision
    if not index then
        index = not revised and not saved.stepID and tonumber(saved.step) or 1
        if (revised or saved.stepID) and not (type(saved.stepID)=="string" and saved.stepID:match("^catchup:")) then
            F.Print("Guide updated; the previous step was removed. Rechecking progress from the start.")
        end
    end
    if not revised and not saved.skippedIDs then skipped = saved.skipped or {} end
    if index and not saved.restartStepID then
        local action=guide.steps[index]
        local task=action and action.tasks and #action.tasks==1 and action.tasks[1] or action
        local questID=task and F.GuideEngine:Resolve(task)
        while index>1 do
            local travel=guide.steps[index-1]
            if not questID or travel.travelQuestID~=questID or travel.travelAction~=task.type then break end
            if saved.confirmedSteps and saved.confirmedSteps[travel.id] or skipped[index-1] then break end
            index=index-1
        end
    end
    F.db.step = math.max(1, math.min(#guide.steps, math.floor(index)))
    F.db.bindings, F.db.skipped = saved.bindings or {}, skipped
    F.db.confirmedSteps = confirmed
    F.db.skipHistory = {}
    F.db.restartStepID = nil
    for _, step in ipairs(guide.steps) do
        if saved.skipHistory and (saved.skipHistory[step.id] or saved.skipHistory[step.legacyGroupID]) then
            F.db.skipHistory[step.id] = true
        end
        if step.id == saved.restartStepID or step.legacyGroupID == saved.restartStepID and saved.restartStepID then
            F.db.restartStepID = step.id
        end
    end
    F.db.manualSkippedSteps = {}
    for stepID,value in pairs(saved.manualSkippedSteps or {}) do
        if value then F.db.manualSkippedSteps[stepID] = true end
    end
    F.db.stepID, F.db.guideRevision, F.db.skippedIDs = guide.steps[F.db.step].id, guide.revision, nil
    F.GuideEngine.catchUpPending = true
    if F.Travel then F.Travel.entryPending=true end
end
function L:Recommended()
    local level = F.Call(UnitLevel, "player") or 1
    local map = F.Call(C_Map and C_Map.GetBestMapForUnit, "player")
    local info = F.Call(C_Map and C_Map.GetMapInfo, map)
    local _, race, raceID = F.Call(UnitRace, "player")
    if raceID==4 then race='NightElf' end
    if level>=30 then return nil,'No guide is available for your level yet.' end
    local starts={Human='alliance-northshire-01-05',Dwarf='alliance-coldridge-01-05',Gnome='alliance-coldridge-01-05',
        NightElf='alliance-shadowglen-01-05',Skyborne='alliance-zephras-grove-01-05'}
    local preferred,walk={},starts[race]
    local _,class=F.Call(UnitClass,'player')
    if not walk and class=='DRUID' then walk=starts.NightElf end
    while walk and self.guides[walk] and not preferred[walk] do
        preferred[walk]=true;walk=self.guides[walk].nextGuideID
    end
    local candidate,best,bestActive
    local zone=F.Call(GetRealZoneText) or info and info.name
    local continent=F.Travel and F.Travel:Continent(zone)
    for _,id in ipairs(self.order) do
        local g=self.guides[id]
        if not g.retired and g.status=='draft' and g.sourceGuideID then
            local distance=level<g.minLevel and g.minLevel-level or level>=g.maxLevel and level-g.maxLevel+1 or 0
            local score=-distance*100+(preferred[id] and 30 or 0)
            local routeContinent=g.routeGroup and g.routeGroup:match('^(%a+)%-')
            if continent and routeContinent and routeContinent~=continent then score=score-60 end
            local nearby=info and info.name==g.zone
            if nearby then score=score+40 end
            local active,seen=0,{}
            for _,step in ipairs(g.steps) do
                for _,task in ipairs(step.tasks or {step}) do
                    local questID=task.questID
                    if questID and not seen[questID] and F.GuideEngine:Applies(task) then
                        seen[questID]=true
                        if F.QuestLog.byID[questID] then active=active+1 end
                    end
                end
            end
            score=score+math.min(active,4)*12
            if level<g.minLevel then score=score-50 end
            if not best or score>best then candidate,best,bestActive=id,score,active end
        end
    end
    if candidate then
        local g=self.guides[candidate]
        return candidate,'Suggested for level '..level..(info and info.name==g.zone and '; you are nearby' or '')..
            (bestActive>0 and '; '..bestActive..' accepted quest'..(bestActive==1 and '' or 's')..' here' or '')..
            '. Missing essential quests are loaded first.'
    end
    return nil,'No suitable guide is available.'
end
function L:Initialize()
    F.db.guides = type(F.db.guides) == "table" and F.db.guides or {}
    local old=self.guides[F.db.guideID]
    if old and old.retired then
        local stepID=F.db.stepID or old.steps[F.db.step] and old.steps[F.db.step].id
        local skippedIDs={}
        for index in pairs(F.db.skipped or {}) do
            if old.steps[index] then skippedIDs[old.steps[index].id]=true end
        end
        local migration={stepID=stepID,revision=F.db.guideRevision,skippedIDs=F.db.skippedIDs or skippedIDs,
            confirmedSteps=F.db.confirmedSteps,manualSkippedSteps=F.db.manualSkippedSteps,
            skipHistory=F.db.skipHistory,bindings=F.db.bindings}
        F.db.guides[old.id]=migration
        local replacement
        for _,id in ipairs(self.order) do
            local guide=self.guides[id]
            if guide.sourceGuideID==old.id and not guide.retired then
                for _,step in ipairs(guide.steps) do
                    if step.id==stepID or step.legacyGroupID==stepID then replacement=id;break end
                end
            end
            if replacement then break end
        end
        F.db.guideID=replacement or self:Recommended()
        for _,id in ipairs(self.order) do
            local guide=self.guides[id]
            if guide.sourceGuideID==old.id and not F.db.guides[id] then
                F.db.guides[id]={step=1,skippedIDs=migration.skippedIDs,
                    confirmedSteps=migration.confirmedSteps,manualSkippedSteps=migration.manualSkippedSteps,
                    skipHistory=migration.skipHistory}
            end
        end
        local saved=F.db.guides[F.db.guideID] or {}
        saved.stepID=replacement and stepID or nil
        self:ApplyState(self.guides[F.db.guideID],saved)
        F.db.guideRevision=nil
        F.Print('Regional guides updated; continuing in '..self.guides[F.db.guideID].title..'.')
    end
    if not self.guides[F.db.guideID] then
        F.db.guideID = self:Recommended() or "alliance-coldridge-01-05"
        F.db.step, F.db.skipped, F.db.bindings = 1, {}, {}
        F.db.stepID, F.db.guideRevision, F.db.skippedIDs, F.db.confirmedSteps = nil, nil, nil, {}
    end
    F.Guide = self.guides[F.db.guideID]
    self:ApplyState(F.Guide, {step = F.db.step, stepID = F.db.stepID, revision = F.db.guideRevision,
        bindings = F.db.bindings, skipped = F.db.skipped, skippedIDs = F.db.skippedIDs, confirmedSteps = F.db.confirmedSteps,
        manualSkippedSteps = F.db.manualSkippedSteps, skipHistory = F.db.skipHistory, restartStepID = F.db.restartStepID})
end
function L:Continue()
    local id=F.Guide.nextGuideID
    if not id or not self.guides[id] then return false end
    self:SaveCurrent()
    F.db.guideID=id;F.Guide=self.guides[id]
    self:ApplyState(F.Guide,F.db.guides[id] or {step=1})
    -- A skipped quest stays skipped when its later actions occur in another visit.
    local skippedQuests={}
    for _,guideID in ipairs(self.order) do
        local guide=self.guides[guideID]
        local saved=F.db.guides[guideID]
        if guide.routeGroup==F.Guide.routeGroup and saved then
            for _,step in ipairs(guide.steps) do
                if saved.manualSkippedSteps and saved.manualSkippedSteps[step.id] then
                    for _,task in ipairs(step.tasks or {step}) do
                        if task.questID and task.type~='travel' then skippedQuests[task.questID]=true end
                    end
                end
            end
        end
    end
    for index,step in ipairs(F.Guide.steps) do
        for _,task in ipairs(step.tasks or {step}) do
            if task.questID and skippedQuests[task.questID] then
                F.db.skipped[index]=true
                F.db.manualSkippedSteps[step.id]=true
            end
        end
    end
    F.GuideEngine.manualHold,F.GuideEngine.selectedStep=nil,nil
    F.Tracker.offset=0
    return true
end
function L:Select(id, recommended)
    if not self.guides[id] then return end
    self:SaveCurrent()
    local saved = F.db.guides[id] or {step = 1, bindings = {}, skipped = {}}
    F.db.guideID = id; F.Guide = self.guides[id]
    self:ApplyState(F.Guide, saved)
    if recommended then F.db.restartStepID=nil end
    F.GuideEngine.manualHold = nil
    F.GuideEngine.selectedStep = nil
    F.Tracker.offset = 0
    F.Refresh()
end
