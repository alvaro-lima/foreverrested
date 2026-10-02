local _, F = ...
local E = {}
F.GuideEngine = E
function E:SelectStep(index)
    self.selectedStep = math.max(1, math.min(#F.Guide.steps, index))
    -- Expanding a different row must not shift the list's first visible step.
    F.Tracker.topOffset = F.Tracker.offset
    F.UI:Refresh()
end
function E:Metadata(id)
    return id and ((F.Guide.questData and F.Guide.questData[id]) or (F.AllianceQuestData and F.AllianceQuestData[id])
        or (F.ForeverUnlockFacts and F.ForeverUnlockFacts[id])
        or (F.ClassicQuestPolicy and F.ClassicQuestPolicy.records[id]))
end
function E:Applies(task)
    if task.classes then
        local _, class = F.Call(UnitClass, "player")
        local matches = false
        for _, candidate in ipairs(task.classes) do if candidate == class then matches = true end end
        if not matches then return false end
    end
    if task.requiredRaces and task.requiredRaces > 0 and task.requiredRaces < 2^32 then
        local _, race = F.Call(UnitRace, "player")
        local bit = ({Human=1, Dwarf=4, NightElf=8, Gnome=64})[race]
        if bit and math.floor(task.requiredRaces / bit) % 2 == 0 then return false end
    end
    local level = F.Call(UnitLevel, "player")
    if task.minLevel and F.Number(level) and level < task.minLevel then return false end
    if task.activeOnly then
        local id, quest = self:Resolve(task)
        if not quest and not F.QuestLog:TurnedIn(id) then return false end
    end
    return true
end
function E:Current()
    F.db.step = math.max(1, math.min(#F.Guide.steps, F.db.step))
    local step = F.Guide.steps[F.db.step]
    local id = step.questID or (step.slot and F.db.bindings[step.slot])
    return step, id, id and F.QuestLog.byID[id]
end
function E:Done(step, id, q)
    if not self:Applies(step) then return true end
    if step.flightPathStop and F.Travel:KnowsFlightPath(step.flightPathStop) then return true end
    if step.flightPathQuestID and F.QuestLog:TurnedIn(step.flightPathQuestID) then return true end
    -- The completed unlock proves its earlier stages were finished, even if
    -- the beta client no longer reports every replaced breadcrumb flag.
    if step.unlockTerminal and F.QuestPolicy:Satisfied(step.unlockTerminal) then return true end
    if step.travelQuestID then
        if F.QuestLog:TurnedIn(step.travelQuestID) then return true end
        local quest=F.QuestLog.byID[step.travelQuestID]
        if step.travelAction=='objective' and quest and quest.complete then return true end
        -- Being in a return-route zone before doing the objective does not
        -- prove that the return journey has happened.
        if step.travelAction=='turnin' and not (quest and quest.complete) then return false end
        if F.Call(UnitOnTaxi,'player')==true then return false end
        local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
        local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
        if info then
            for index=step.travelLeg,#step.travelZones do
                if info.name==step.travelZones[index] then
                    if not step.travelFinal then return true end
                    -- Arrival must match the arrow's live/cached/fallback destination.
                    local targetMap,tx,ty=F.Navigation:TravelWaypoint(step)
                    local x,y=F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,targetMap,'player'))
                    if targetMap and F.Number(x) and F.Number(y) and F.Number(tx) and F.Number(ty)
                        and (x~=0 or y~=0) and (x-tx)^2+(y-ty)^2<=.03^2 then return true end
                end
            end
        end
    end
    -- Confirming a trainer visit is not evidence of completing its unlocks.
    if F.QuestPolicy and step.confirmOnNext then
        for _, task in ipairs(step.alongside or {}) do
            if F.QuestPolicy:Critical(task) and not F.QuestLog:TurnedIn(self:Resolve(task)) then return false end
        end
    end
    if step.confirmOnNext and F.db.confirmedSteps and F.db.confirmedSteps[step.id] then return true end
    if step.targetLevel then
        local level = F.Call(UnitLevel, "player")
        return F.Number(level) and level >= step.targetLevel
    end
    if step.tasks then
        local required = 0
        for _, task in ipairs(step.tasks) do
            if not task.optional and self:Applies(task) then
                required = required + 1
                local taskID, quest = self:Resolve(task)
                if not self:Done(task, taskID, quest) then return false end
            end
        end
        return required > 0
    end
    if not id then return false end
    if F.QuestLog:TurnedIn(id) then
        return step.type == "pickup" or step.type == "objective" or step.type == "turnin"
    end
    if step.type == "pickup" then return q ~= nil end
    if step.type == "objective" and q and not q.failed then
        if not step.objective then return q.complete == true end
        local objective = q.objectives[step.objective or 1]
        return objective and objective.finished == true or q.complete == true
    end
    -- Travel, trainer, grind and notes require manual confirmation by default.
    return false
end
function E:Resolve(task)
    local id = task.questID or (task.slot and F.db.bindings[task.slot])
    return id, id and F.QuestLog.byID[id]
end
function E:TaskState(task)
    local id, q = self:Resolve(task)
    if self:Done(task, id, q) then return "complete" end
    if q and q.failed then return "failed" end
    if task.type == "turnin" then
        if q and q.complete then return "ready" end
        return q and "notready" or "waiting"
    end
    if q and task.type == "objective" then return "ongoing" end
    return "waiting"
end
function E:StepState(index)
    local step = F.Guide.steps[index]
    if not step then return "waiting" end
    local id, q = self:Resolve(step)
    if self:Done(step, id, q) then return "complete" end
    if F.db.skipped[index] then return "skipped" end
    local required, ready, ongoing = 0, 0, false
    for _, task in ipairs(self:Tasks(step)) do
        if not task.optional then
            required = required + 1
            local state = self:TaskState(task)
            if state == "failed" then return "failed" end
            if state == "ready" or state == "complete" then ready = ready + 1 end
            if state == "ongoing" then ongoing = true end
        end
    end
    if required > 0 and ready == required then return "ready" end
    if ongoing or index == F.db.step then return "ongoing" end
    return "waiting"
end
function E:Tasks(step, includeSide)
    step = step or self:Current()
    local tasks = {}
    for _, task in ipairs(step.tasks or {step}) do if self:Applies(task) then tasks[#tasks + 1] = task end end
    if includeSide then
        for _, task in ipairs(step.alongside or {}) do if self:Applies(task) then tasks[#tasks + 1] = task end end
    end
    return tasks
end
function E:Focus()
    local step = self:Current()
    for _, task in ipairs(self:Tasks(step, true)) do
        local id, q = self:Resolve(task)
        if not self:Done(task, id, q) then return task, id, q end
    end
    return step, self:Resolve(step)
end
function E:NextRelevantIndex()
    for index=F.db.step+1,#F.Guide.steps do
        local step=F.Guide.steps[index]
        local id,q=self:Resolve(step)
        if not F.db.skipped[index] and not self:Done(step,id,q) then return index end
    end
end
function E:Targets()
    local targets, used = {}, {}
    for _, task in ipairs(self:Tasks(nil, true)) do
        local id, q = self:Resolve(task)
        if task.type == "objective" and q and not q.failed and not q.complete and not F.QuestLog:TurnedIn(id) then
            for index, objective in ipairs(q.objectives) do
                if (not task.objective or task.objective == index) and not objective.finished then
                    local fixture = task.slot and F.Guide.quests[task.slot]
                    local mob = task.mob or (index == 1 and fixture and q.title == fixture.title and fixture.mob)
                    if not mob then mob = self:MappedTarget(q, objective, index) end
                    if not mob and objective.type == "monster" and objective.text then
                        mob = objective.text:match("^(.+):%s*%d+%s*/%s*%d+")
                            or objective.text:match("^%s*%d+%s*/%s*%d+%s+(.+)$")
                        if mob then mob = mob:gsub("%s+slain$", ""):gsub("%s+killed$", "") end
                    end
                    if mob and not used[mob] then
                        used[mob] = true
                        targets[#targets + 1] = {mob = mob, questID = id, text = objective.text or F.QuestLog:Progress(objective)}
                    end
                end
            end
        end
    end
    return targets
end
function E:MappedTarget(q, objective, index)
    local record = self:TargetRecord(q)
    if not record then
        local data = self:Metadata(q.id)
        local candidates = {}
        if not data or q.title ~= data.title or type(objective.text) ~= "string" then return end
        for _, location in ipairs(data.locations) do
            if location.entityType == 1 and location.name then
                if location.role == "requirement" and objective.type == "monster" and objective.text:find(location.name, 1, true)
                    or location.role == "sourcerequirement" and location.item and objective.text:find(location.item, 1, true) then
                    candidates[#candidates + 1] = location
                end
            end
        end
        local map = F.Call(C_Map and C_Map.GetBestMapForUnit, "player")
        local info = F.Call(C_Map and C_Map.GetMapInfo, map)
        local px, py = F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition, map, "player"))
        table.sort(candidates, function(a, b)
            if a.role ~= b.role then return a.role == "requirement" end
            if a.role == "requirement" and #a.name ~= #b.name then return #a.name > #b.name end
            local ax, ay = a.x or 0, a.y or 0
            local bx, by = b.x or 0, b.y or 0
            if info and info.name == a.zone and a.zone == b.zone and F.Number(px) and F.Number(py) then
                return (ax-px)^2 + (ay-py)^2 < (bx-px)^2 + (by-py)^2
            end
            return a.name < b.name
        end)
        return candidates[1] and candidates[1].name
    end
    local objectID = objective.objectID or objective.objectId
    for _, source in ipairs(record.objectives) do
        if source.index == index then
            local exactID = F.Number(objectID) and objectID == source.itemID
            local textMatch = type(objective.text) == "string" and objective.text:find(source.item, 1, true)
            if exactID or textMatch or (F.QuestTargets[q.id] == record and objectID == nil) then return source.mob end
        end
    end
end
function E:TargetRecord(q)
    if not q then return end
    local record = F.QuestTargets[q.id]
    -- English-title fallback is constrained by matching objective data too.
    if not record then
        for _, candidate in pairs(F.QuestTargets) do
            if candidate.title == q.title then record = candidate; break end
        end
    end
    return record
end
function E:AdvanceSafe()
    -- Manual Back holds the selected step until Next/Skip, avoiding snap-forward.
    if self.manualHold then return end
    for _ = 1, #F.Guide.steps do
        local step, id, q = self:Current()
        if F.db.step >= #F.Guide.steps or (not F.db.skipped[F.db.step] and not self:Done(step, id, q)) then break end
        F.db.step = F.db.step + 1
    end
end
function E:CatchUpOnLoad()
    if not self.catchUpPending then return end
    -- An explicit From choice takes precedence over automatic level catch-up.
    if F.db.restartStepID then self.catchUpPending = nil; return end
    local level = F.Call(UnitLevel, "player")
    -- Login may load saved variables before the player's level is available.
    if not F.Number(level) or level < 1 then return end
    self.catchUpPending = nil
    if F.QuestPolicy then F.QuestPolicy:PrepareGuide() end
    local boundary = 1
    if F.Guide.status ~= "test" and level > (F.Guide.minLevel or 1) then
        -- Explicit checkpoints define route sections. Quest levels provide a
        -- fallback for routes without intermediate checkpoints; never use the
        -- minimum acceptance level as a recommended leveling level.
        local checkpoint = 0
        for index, step in ipairs(F.Guide.steps) do
            if step.targetLevel and level >= step.targetLevel then checkpoint = index end
        end
        boundary = checkpoint + 1
        for index = boundary, #F.Guide.steps do
            local step = F.Guide.steps[index]
            local recommended = step.level or step.targetLevel
            for _, task in ipairs(self:Tasks(step)) do
                local id = self:Resolve(task)
                local data = self:Metadata(id)
                if data and F.Number(data.level) and data.level > 0 then
                    recommended = math.max(recommended or 0, data.level)
                end
            end
            if recommended and recommended >= level then boundary = index; break end
            -- Keep the final manual exit/continuation visible for an outleveled guide.
            boundary = index
        end
    end
    self.catchUpReasons = F.QuestPolicy and F.QuestPolicy:ProtectedSteps(boundary) or {}
    if F.QuestPolicy then boundary, self.catchUpReasons = F.QuestPolicy:InsertRecovery(boundary, self.catchUpReasons) end
    if F.Travel and F.Guide.faction then
        -- Recovery quests can also introduce journeys. Preserve protection and
        -- the section boundary by stable ID when inserting their travel rows.
        local boundaryStep=F.Guide.steps[boundary]
        local reasons={}
        for index,step in ipairs(F.Guide.steps) do reasons[step.id]=self.catchUpReasons[index] end
        F.Travel:EnsureSteps(F.Guide,true)
        self.catchUpReasons={}
        for index,step in ipairs(F.Guide.steps) do
            self.catchUpReasons[index]=reasons[step.id] or step.travelQuestID and step.criticalReason or nil
            if boundaryStep and step.id==boundaryStep.id then boundary=index end
        end
    end
    for index, step in ipairs(F.Guide.steps) do
        -- Check every quest, including optional and later actions, against the
        -- character's completion history before deciding what to skip.
        for _, task in ipairs(step.tasks or {step}) do F.QuestLog:TurnedIn(self:Resolve(task)) end
        for _, task in ipairs(step.alongside or {}) do F.QuestLog:TurnedIn(self:Resolve(task)) end
        local id, q = self:Resolve(step)
        if self:Done(step, id, q) then F.db.skipped[index] = nil
        elseif F.db.manualSkippedSteps and F.db.manualSkippedSteps[step.id] then F.db.skipped[index] = true
        elseif self.catchUpReasons[index] then F.db.skipped[index] = nil
        elseif index < boundary then F.db.skipped[index] = true end
    end
    self.manualHold, self.selectedStep = nil, nil
    F.db.step = 1
end
function E:ResumeAuto()
    -- Next/Back browse the guide; neither proves a quest is finished. Reconcile
    -- from the beginning so Auto can recover from browsing beyond live progress.
    self.manualHold = nil
    self.selectedStep = nil
    F.db.step = 1
    F.Refresh()
    F.Tracker:ShowCurrentAtTop()
end
function E:Move(delta, skip)
    local index = self.selectedStep or F.db.step
    local step = F.Guide.steps[index]
    if delta > 0 or skip then self.manualHold = nil end
    if delta > 0 and not skip and step.confirmOnNext then
        if F.QuestPolicy then
            for _, task in ipairs(step.alongside or {}) do
                if F.QuestPolicy:Critical(task) and not F.QuestLog:TurnedIn(self:Resolve(task)) then
                    F.Print("This stop has an unfinished essential class quest. Complete it, or use Skip to bypass it explicitly.")
                    return
                end
            end
        end
        F.db.confirmedSteps = F.db.confirmedSteps or {}; F.db.confirmedSteps[step.id] = true
    end
    if skip then
        F.db.skipped[index] = true
        F.db.manualSkippedSteps = F.db.manualSkippedSteps or {}
        F.db.manualSkippedSteps[step.id] = true
    end
    self.selectedStep = math.max(1, math.min(#F.Guide.steps, index + delta))
    if skip or delta > 0 and step.confirmOnNext then F.Refresh() else F.UI:Refresh() end
end
function E:ResetFrom(index)
    index = index or self.selectedStep or F.db.step
    if not F.Number(index) or index % 1 ~= 0 or not F.Guide.steps[index] then
        F.Print("Choose a step between 1 and " .. #F.Guide.steps .. ".")
        return
    end
    F.db.skipHistory = F.db.skipHistory or {}
    -- Preserve skips independently of the currently chosen starting point.
    for position, step in ipairs(F.Guide.steps) do
        if F.db.skipped[position] then F.db.skipHistory[step.id] = true end
    end
    for position, step in ipairs(F.Guide.steps) do
        F.db.skipped[position] = position < index and F.db.skipHistory[step.id] or nil
        if position >= index and F.db.confirmedSteps then F.db.confirmedSteps[step.id] = nil end
    end
    F.db.restartStepID = F.Guide.steps[index].id
    self.catchUpPending = nil
    F.db.step = index
    self.selectedStep = nil
    -- Keep the chosen starting point visible even if live quests are complete.
    self.manualHold = true
    F.Refresh()
    F.Tracker:ShowCurrentAtTop()
end
function E:Reset()
    F.db.step, F.db.bindings, F.db.skipped = 1, {}, {}
    F.db.confirmedSteps = {}
    F.db.manualSkippedSteps = {}
    F.db.skipHistory, F.db.restartStepID = {}, nil
    self.manualHold = nil
    self.selectedStep = nil
    F.Refresh()
end
