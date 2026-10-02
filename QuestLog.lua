local _, F = ...
local Q = {list = {}, byID = {}}
F.QuestLog = Q
function Q:Refresh()
    self.list, self.byID = {}, {}
    local api = C_QuestLog or {}
    local count = F.Call(api.GetNumQuestLogEntries) or F.Call(GetNumQuestLogEntries) or 0
    local zone = "Active Quests"
    for index = 1, count do
        local info = F.Call(api.GetInfo, index)
        if not info then
            local title, level, _, header, _, complete, _, id = F.Call(GetQuestLogTitle, index)
            if title then info = {title = title, level = level, isHeader = header, isComplete = complete, questID = id} end
        end
        if info and info.isHeader then zone = info.title or zone
        elseif info and F.Number(info.questID) and info.questID > 0 then
            local q = {id = info.questID, title = info.title or "Quest", level = info.level or 0,
                zone = zone, index = index, failed = info.isComplete == -1 or info.isFailed == true}
            q.complete = F.Call(api.IsComplete, q.id)
            if q.complete == nil then q.complete = info.isComplete == true or info.isComplete == 1 end
            if q.failed then q.complete = false end
            q.objectives = F.Call(api.GetQuestObjectives, q.id) or {}
            if #q.objectives == 0 then
                for objective = 1, F.Call(GetNumQuestLeaderBoards, index) or 0 do
                    local text, kind, finished = F.Call(GetQuestLogLeaderBoard, objective, index)
                    q.objectives[#q.objectives + 1] = {text = text, type = kind, finished = finished}
                end
            end
            self.list[#self.list + 1], self.byID[q.id] = q, q
        end
    end
    self:BindTests()
    F.QuestData:ObserveLog(self.list)
end
function Q:BindTests()
    if F.Guide.status ~= "test" then return end
    local used = {}
    for _, id in pairs(F.db.bindings) do used[id] = true end
    -- Prefer exact live title matches before using arbitrary live quests.
    for slot, fixture in ipairs(F.Guide.quests) do
        if not F.db.bindings[slot] then
            for _, q in ipairs(self.list) do
                if q.title == fixture.title and not used[q.id] then
                    F.db.bindings[slot], used[q.id] = q.id, true
                    break
                end
            end
        end
    end
    for slot = 1, #F.Guide.quests do
        if not F.db.bindings[slot] then
            for _, q in ipairs(self.list) do
                if not used[q.id] then
                    F.db.bindings[slot], used[q.id] = q.id, true
                    break
                end
            end
        end
    end
end
function Q:TurnedIn(id)
    if not id then return false end
    local completed = F.db.completed[id] == true or F.Call(C_QuestLog and C_QuestLog.IsQuestFlaggedCompleted, id) == true
        or F.Call(IsQuestFlaggedCompleted, id) == true
    if completed then F.db.completed[id] = true end
    return completed
end
function Q:Progress(objective)
    if not objective then return "Waiting for live quest data" end
    if F.Number(objective.numFulfilled) and F.Number(objective.numRequired) then
        return objective.numFulfilled .. "/" .. objective.numRequired
    end
    return objective.finished and "COMPLETE" or (objective.text or "In progress")
end
