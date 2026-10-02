local _, F = ...
-- Live observations are build-scoped evidence, not a replacement quest database.
-- No quest selection, map selection, item requests, or protected actions here.
local D = {schemaVersion = 1, limit = 300}
F.QuestData = D
local function text(value)
    return type(value) == "string" and value:sub(1, 512) or nil
end
function D:Build()
    local version, build, _, interface = F.Call(GetBuildInfo)
    return {version = tostring(version or "unknown"), build = tostring(build or "unknown"), interface = interface}
end
function D:Initialize()
    local current = self:Build()
    local saved = F.db.questData
    if type(saved) ~= "table" or saved.schemaVersion ~= self.schemaVersion then
        saved = {schemaVersion = self.schemaVersion, observations = {}}
        F.db.questData = saved
    end
    if type(saved.observations) ~= "table" then saved.observations = {} end
    local key = current.version .. ":" .. current.build .. ":" .. tostring(current.interface)
    self.buildChanged = saved.buildKey ~= nil and saved.buildKey ~= key
    saved.buildKey, saved.client = key, current
    self.saved = saved
    self.capabilities = {
        questInfo = type(C_QuestLog and C_QuestLog.GetInfo) == "function",
        objectives = type(C_QuestLog and C_QuestLog.GetQuestObjectives) == "function",
        dialogueXP = type(GetRewardXP) == "function",
        rewardItems = type(GetQuestItemInfo) == "function" and type(GetQuestItemLink) == "function",
        itemInfo = type(GetItemInfo) == "function",
        itemStats = type(GetItemStats) == "function",
    }
    if self.buildChanged then
        F.Print("Client build changed. Old quest observations are stale until observed again. /fg refresh rescans your live quests.")
    end
end
function D:Record(id)
    if not self.saved or not F.Number(id) or id <= 0 then return end
    local key = tostring(id)
    local record = self.saved.observations[key]
    if not record then
        local count, oldestKey, oldest = 0, nil, math.huge
        for existing, value in pairs(self.saved.observations) do
            count = count + 1
            local time = tonumber(value.lastSeen) or 0
            if time < oldest then oldestKey, oldest = existing, time end
        end
        if count >= self.limit and oldestKey then self.saved.observations[oldestKey] = nil end
    end
    -- A changed build invalidates reward/objective evidence independently of IDs.
    if not record or record.buildKey ~= self.saved.buildKey then
        record = {questID = id, buildKey = self.saved.buildKey, confidence = "observed"}
        self.saved.observations[key] = record
    end
    record.lastSeen = F.Call(time) or 0
    return record
end
function D:ObserveLog(quests)
    if not self.saved then return end
    for _, quest in ipairs(quests) do
        local record = self:Record(quest.id)
        record.title, record.questLevel, record.zone = text(quest.title), quest.level, text(quest.zone)
        record.objectives = {}
        for index, objective in ipairs(quest.objectives) do
            if index > 20 then break end
            record.objectives[index] = {index = index, text = text(objective.text), type = text(objective.type),
                objectiveType = objective.objectiveType, objectID = objective.objectID or objective.objectId,
                required = objective.numRequired}
        end
    end
end
function D:Items(kind, count)
    local result = {}
    for index = 1, math.min(tonumber(count) or 0, 20) do
        local name, _, quantity, quality, usable = F.Call(GetQuestItemInfo, kind, index)
        local link = F.Call(GetQuestItemLink, kind, index)
        local id = type(link) == "string" and tonumber(link:match("item:(%d+)")) or nil
        if id then
            local _, _, itemQuality, itemLevel, requiredLevel, itemType, subtype, _, equipLoc = F.Call(GetItemInfo, link)
            local rawStats = F.Call(GetItemStats, link)
            local stats = {}
            if type(rawStats) == "table" then
                for stat, value in pairs(rawStats) do
                    if type(stat) == "string" and F.Number(value) then stats[stat] = value end
                end
            end
            result[#result + 1] = {itemID = id, name = text(name), quantity = quantity,
                quality = itemQuality or quality, usable = usable, itemLevel = itemLevel,
                requiredLevel = requiredLevel, itemType = text(itemType), subtype = text(subtype),
                equipLoc = text(equipLoc), stats = next(stats) and stats or nil,
                detailsCached = itemLevel ~= nil}
        end
    end
    return result
end
function D:ObserveDialogue()
    local id = F.Call(GetQuestID)
    local record = self:Record(id)
    if not record then return end
    record.title = text(F.Call(GetTitleText)) or record.title
    local xp = F.Call(GetRewardXP)
    if F.Number(xp) and xp >= 0 then
        record.rewardXPObserved = {value = xp, playerLevel = F.Call(UnitLevel, "player"),
            context = "quest-dialogue", buildKey = self.saved.buildKey}
    end
    local rewards, choices = F.Call(GetNumQuestRewards), F.Call(GetNumQuestChoices)
    if F.Number(rewards) then record.guaranteedRewards = self:Items("reward", rewards) end
    if F.Number(choices) then record.choiceRewards = self:Items("choice", choices) end
end
function D:TurnedIn(id, xp)
    local record = self:Record(id)
    if record and F.Number(xp) and xp >= 0 then
        local dialogue = record.rewardXPObserved
        local before = dialogue and dialogue.context == "quest-dialogue" and dialogue.playerLevel or nil
        record.rewardXPObserved = {value = xp, playerLevel = before, playerLevelAfterEvent = F.Call(UnitLevel, "player"),
            context = "QUEST_TURNED_IN", buildKey = self.saved.buildKey}
    end
end
local function quote(value)
    return '"' .. value:gsub('[%z\1-\31\\"]', function(char)
        return string.format("\\u%04x", string.byte(char))
    end) .. '"'
end
local function json(value)
    local kind = type(value)
    if kind == "string" then return quote(value) end
    if kind == "boolean" then return value and "true" or "false" end
    if kind == "number" then return F.Number(value) and tostring(value) or "null" end
    if kind ~= "table" then return "null" end
    local entries, keys, array = {}, {}, true
    for key in pairs(value) do
        keys[#keys + 1] = key
        if type(key) ~= "number" or key < 1 or key ~= math.floor(key) then array = false end
    end
    if array and #keys == #value then
        for index = 1, #value do entries[#entries + 1] = json(value[index]) end
        return "[" .. table.concat(entries, ",") .. "]"
    end
    table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)
    for _, key in ipairs(keys) do entries[#entries + 1] = quote(tostring(key)) .. ":" .. json(value[key]) end
    return "{" .. table.concat(entries, ",") .. "}"
end
function D:Export()
    local quests, stale = {}, 0
    for _, record in pairs(self.saved.observations) do
        if record.buildKey == self.saved.buildKey then quests[#quests + 1] = record else stale = stale + 1 end
    end
    table.sort(quests, function(a, b) return a.questID < b.questID end)
    return json({schemaVersion = self.schemaVersion, source = {game = "forever", kind = "live-observation",
        client = self.saved.client, buildKey = self.saved.buildKey}, capabilities = self.capabilities,
        staleExcluded = stale, quests = quests})
end
function D:Get(id)
    if not self.saved then return nil, "unknown" end
    local key = tostring(id)
    local live = self.saved.observations[key]
    local imported = F.QuestCatalog and F.QuestCatalog.quests[key]
    if live and live.buildKey == self.saved.buildKey then
        local combined = {}
        if imported and imported.buildKey == self.saved.buildKey then
            for field, value in pairs(imported) do combined[field] = value end
        end
        for field, value in pairs(live) do combined[field] = value end
        return combined, "observed"
    end
    if imported and imported.buildKey == self.saved.buildKey then return imported, imported.confidence end
    return nil, (live or imported) and "stale" or "unknown"
end
function D:ShowExport()
    if not self.window then
        local window = F.UI:Panel(UIParent, 560, 400)
        self.window = window; window:SetPoint("CENTER"); window:SetFrameStrata("DIALOG")
        F.UI:Text(window, "GameFontNormal", "TOPLEFT", 12, -12, 536):SetText("Forever quest data — current build")
        F.UI:Text(window, "GameFontHighlightSmall", "TOPLEFT", 12, -37, 536):SetText("Ctrl+A, Ctrl+C to copy. Paste into a JSON file for offline import.")
        local scroll = F.Frame("ScrollFrame", nil, window, "UIPanelScrollFrameTemplate")
        scroll:SetPoint("TOPLEFT", 12, -72); scroll:SetSize(508, 278)
        local edit = CreateFrame("EditBox", nil, scroll)
        self.edit = edit; edit:SetMultiLine(true); edit:SetAutoFocus(false); edit:SetFontObject("GameFontHighlightSmall")
        edit:SetWidth(500); edit:SetHeight(278); scroll:SetScrollChild(edit)
        edit:SetScript("OnTextChanged", function()
            edit:SetHeight(math.max(278, (F.Call(edit.GetNumLines, edit) or 1) * 14 + 20))
        end)
        edit:SetScript("OnEscapePressed", function() window:Hide() end)
        F.UI:Button(window, "Close", 92, "BOTTOMLEFT", 12, 12, function() window:Hide() end)
    end
    self.edit:SetText(self:Export()); self.window:Show(); self.edit:SetFocus(); self.edit:HighlightText()
end
