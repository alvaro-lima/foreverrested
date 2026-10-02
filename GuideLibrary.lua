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
        if guide.minLevel == bracket.min and guide.maxLevel == bracket.max then
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
                    for _, other in ipairs(group.tasks) do
                        if other ~= task then
                            local side = {}
                            for key,value in pairs(other) do side[key] = value end
                            side.optional = true
                            side.activeOnly = side.type ~= "pickup" or nil
                            step.alongside[#step.alongside+1] = side
                        end
                    end
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
    local saved = {step = F.db.step, stepID = current and current.id, revision = guide.revision,
        bindings = F.db.bindings, skipped = F.db.skipped, skippedIDs = skippedIDs, confirmedSteps = F.db.confirmedSteps,
        manualSkippedSteps = F.db.manualSkippedSteps, skipHistory = F.db.skipHistory, restartStepID = F.db.restartStepID}
    F.db.guides[F.db.guideID] = saved
    F.db.stepID, F.db.guideRevision, F.db.skippedIDs = saved.stepID, saved.revision, skippedIDs
end
function L:ApplyState(guide, saved)
    saved = saved or {}
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
end
function L:Recommended()
    local level = F.Call(UnitLevel, "player") or 1
    local map = F.Call(C_Map and C_Map.GetBestMapForUnit, "player")
    local info = F.Call(C_Map and C_Map.GetMapInfo, map)
    if info then
        local candidate
        for _, id in ipairs(self.order) do
            local guide = self.guides[id]
            if guide.status == "draft" and guide.zone == info.name and level >= guide.minLevel and level <= guide.maxLevel
                and (not candidate or guide.minLevel > self.guides[candidate].minLevel) then candidate = id end
        end
        if candidate then return candidate end
    end
    local _, race = F.Call(UnitRace, "player")
    if level >= 10 then
        return ({Human="alliance-westfall-10-20", Dwarf="alliance-loch-modan-10-20", Gnome="alliance-loch-modan-10-20",
            NightElf="alliance-darkshore-10-20", Skyborne="alliance-zephras-10-14"})[race]
    end
    return ({Human="alliance-elwynn-01-10", Dwarf="alliance-dun-morogh-01-10", Gnome="alliance-dun-morogh-01-10",
        NightElf="alliance-teldrassil-01-10", Skyborne="alliance-zephras-01-10"})[race]
end
function L:Initialize()
    F.db.guides = type(F.db.guides) == "table" and F.db.guides or {}
    if not self.guides[F.db.guideID] then
        F.db.guideID = self:Recommended() or "alliance-dun-morogh-01-10"
        F.db.step, F.db.skipped, F.db.bindings = 1, {}, {}
        F.db.stepID, F.db.guideRevision, F.db.skippedIDs, F.db.confirmedSteps = nil, nil, nil, {}
    end
    F.Guide = self.guides[F.db.guideID]
    self:ApplyState(F.Guide, {step = F.db.step, stepID = F.db.stepID, revision = F.db.guideRevision,
        bindings = F.db.bindings, skipped = F.db.skipped, skippedIDs = F.db.skippedIDs, confirmedSteps = F.db.confirmedSteps,
        manualSkippedSteps = F.db.manualSkippedSteps, skipHistory = F.db.skipHistory, restartStepID = F.db.restartStepID})
end
function L:Select(id)
    if not self.guides[id] then return end
    self:SaveCurrent()
    local saved = F.db.guides[id] or {step = 1, bindings = {}, skipped = {}}
    F.db.guideID = id; F.Guide = self.guides[id]
    self:ApplyState(F.Guide, saved)
    F.GuideEngine.manualHold = nil
    F.GuideEngine.selectedStep = nil
    F.Tracker.offset = 0
    F.Refresh()
end
