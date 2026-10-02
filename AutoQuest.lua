local _, F = ...
local A = {}
F.AutoQuest = A
function A:Allowed(id, kind)
    if not F.db or not F.Guide or not F.Number(id) or id <= 0 then return false end
    for index = F.db.step, #F.Guide.steps do
        if not F.db.skipped[index] then
            for _, task in ipairs(F.GuideEngine:Tasks(F.Guide.steps[index], true)) do
                local questID = F.GuideEngine:Resolve(task)
                if task.type == kind and questID == id then return true end
            end
        end
    end
    return false
end
function A:Gossip()
    if F.Travel:OpenFlightGossip() then return end
    local api = C_GossipInfo
    if not api then return end
    for _, quest in ipairs(F.Call(api.GetActiveQuests) or {}) do
        if quest.isComplete and self:Allowed(quest.questID,"turnin") then
            F.Call(api.SelectActiveQuest,quest.questID); return
        end
    end
    for _, quest in ipairs(F.Call(api.GetAvailableQuests) or {}) do
        if self:Allowed(quest.questID,"pickup") then
            if F.Call(DoesQuestHaveRequirementsMet,quest.questID) ~= false then
                F.Call(api.SelectAvailableQuest,quest.questID); return
            end
        end
    end
end
function A:GreetingID(title, kind)
    -- The older greeting API exposes titles rather than IDs. Only match a
    -- unique known guide quest, never an unbound draft entry or ambiguous name.
    if type(title) ~= "string" then return end
    local found
    for index = F.db.step, #F.Guide.steps do
        for _, task in ipairs(F.GuideEngine:Tasks(F.Guide.steps[index],true)) do
            local id, q = F.GuideEngine:Resolve(task)
            local data = F.GuideEngine:Metadata(id)
            local name = q and q.title or data and data.title
            if name == title and self:Allowed(id,kind) then
                if found and found ~= id then return end
                found = id
            end
        end
    end
    return found
end
function A:Greeting()
    for index = 1, F.Call(GetNumActiveQuests) or 0 do
        local title, complete = F.Call(GetActiveTitle,index)
        if complete and self:GreetingID(title,"turnin") then F.Call(SelectActiveQuest,index); return end
    end
    for index = 1, F.Call(GetNumAvailableQuests) or 0 do
        local title = F.Call(GetAvailableTitle,index)
        if self:GreetingID(title,"pickup") then F.Call(SelectAvailableQuest,index); return end
    end
end
function A:Handle(event)
    if not F.db or not F.Guide or F.Combat() or F.Call(IsShiftKeyDown) == true then return end
    if event == "GOSSIP_SHOW" then self:Gossip(); return end
    if event == "QUEST_GREETING" then self:Greeting(); return end
    local id = F.Call(GetQuestID)
    if event == "QUEST_DETAIL" then
        if self:Allowed(id,"pickup") and F.Call(IsQuestAutoAccept) ~= true then F.Call(AcceptQuest) end
    elseif self:Allowed(id,"turnin") then
        if F.Call(QuestRequiresGold) == true then return end
        if event == "QUEST_PROGRESS" and F.Call(IsQuestCompletable) == true then
            F.Call(CompleteQuest)
        elseif event == "QUEST_COMPLETE" then
            local choices = F.Call(GetNumQuestChoices)
            if F.Number(choices) and choices >= 0 and choices <= 1 then F.Call(GetQuestReward,choices) end
        end
    end
end
