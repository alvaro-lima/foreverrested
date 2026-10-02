local addon, F = ...
local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
local elapsed, questElapsed, dirty = 0, 0, false
local function initialize()
    F.LoadDatabase()
    F.Travel:ObserveFlightPaths()
    F.Travel:PositionChanged()
    -- Secure frame creation is deferred until combat ends if login is unusual.
    if F.Combat() then F.pendingInit = true; return end
    if F.UI.frame then return end
    F.UI:Create(); F.SecureTarget:Create(); F.Minimap:Create(); F.Refresh()
    F.Print("Alliance 1-30 guides ready. Minimap or /fg guides chooses a route. /fg debug shows diagnostics.")
end
frame:SetScript("OnEvent", function(_, event, ...)
    if event == "ADDON_LOADED" then
        if ... ~= addon then return end
        local events = {"PLAYER_LOGIN", "PLAYER_ENTERING_WORLD", "QUEST_LOG_UPDATE", "QUEST_ACCEPTED",
            "QUEST_TURNED_IN", "QUEST_REMOVED", "QUEST_POI_UPDATE", "ZONE_CHANGED_NEW_AREA", "PLAYER_REGEN_ENABLED", "PLAYER_LOGOUT", "PLAYER_TARGET_CHANGED",
            "QUEST_DETAIL", "QUEST_COMPLETE", "QUEST_PROGRESS", "GOSSIP_SHOW", "QUEST_GREETING", "PLAYER_LEVEL_UP",
            "GET_ITEM_INFO_RECEIVED", "PLAYER_EQUIPMENT_CHANGED", "SKILL_LINES_CHANGED",
            "TAXIMAP_OPENED", "TAXIMAP_CLOSED", "TAXI_NODE_STATUS_CHANGED", "NEW_TAXI_PATH"}
        for _, name in ipairs(events) do
            if not C_EventUtils or not C_EventUtils.IsEventValid or F.Call(C_EventUtils.IsEventValid, name) then
                F.Call(frame.RegisterEvent, frame, name)
            end
        end
        return
    end
    if event == "PLAYER_LOGIN" then initialize(); return end
    if event == "PLAYER_REGEN_ENABLED" then
        if F.pendingInit then F.pendingInit = nil; initialize() end
        if F.db and F.UI.frame then F.SecureTarget:UpdateTasks(F.SecureTarget.desiredTargets); dirty = true end
    end
    if not F.db then return end
    if event == "PLAYER_ENTERING_WORLD" or event == "ZONE_CHANGED_NEW_AREA" then
        F.Travel:PositionChanged()
    end
    if event == "TAXIMAP_OPENED" or event == "TAXI_NODE_STATUS_CHANGED" then
        F.Travel:ObserveFlightPaths(true)
        if event == "TAXIMAP_OPENED" then F.Travel:FlightMapOpened() end
    elseif event == "TAXIMAP_CLOSED" then
        F.Travel.flightAttempts=nil
    elseif event == "PLAYER_ENTERING_WORLD" or event == "NEW_TAXI_PATH" then
        F.Travel:ObserveFlightPaths()
    end
    if event == "PLAYER_LEVEL_UP" then F.GuideEngine.unlockRefreshPending = true end
    if event == "QUEST_DETAIL" or event == "QUEST_COMPLETE" or event == "QUEST_PROGRESS" then
        F.QuestData:ObserveDialogue(); F.AutoQuest:Handle(event); return
    end
    if event == "GOSSIP_SHOW" or event == "QUEST_GREETING" then F.AutoQuest:Handle(event); return end
    if event == "PLAYER_TARGET_CHANGED" then F.SecureTarget:UpdateSelection(); return end
    if event == "PLAYER_LOGOUT" then F.GuideLibrary:SaveCurrent() end
    if event == "QUEST_TURNED_IN" then
        local id, xp = ...
        F.QuestData:TurnedIn(id, xp)
        if F.Number(id) then F.db.completed[id] = true end
    end
    dirty = true
end)
-- 5 Hz navigation and coalesced quest events; no per-frame map calculations.
frame:SetScript("OnUpdate", function(_, dt)
    if not F.db or not F.UI.frame then return end
    elapsed, questElapsed = elapsed + dt, questElapsed + dt
    if dirty and questElapsed >= .15 then
        dirty, questElapsed = false, 0; F.Refresh()
    end
    if elapsed >= .2 then
        elapsed = 0
        F.Travel:FlightMapTick()
        F.Travel:Tick()
        F.UI:NavigationTick()
    end
end)
SLASH_FOREVERRESTED1 = "/fg"
SlashCmdList.FOREVERRESTED = function(message)
    if not F.db or not F.UI.frame then F.Print("Waiting for login / combat end."); return end
    local command = (message or ""):lower():match("^%s*(%S*)")
    if command == "next" then F.GuideEngine:Move(1)
    elseif command == "back" then F.GuideEngine:Move(-1)
    elseif command == "skip" then F.GuideEngine:Move(1, true)
    elseif command == "reset" then
        local argument = message:lower():match("^%s*reset%s+(.+)%s*$")
        if argument then F.GuideEngine:ResetFrom(tonumber(argument) or false)
        else F.GuideEngine:Reset() end
    elseif command == "auto" then F.GuideEngine:ResumeAuto()
    elseif command == "debug" then F.db.debug = not F.db.debug; F.UI:Debug()
    elseif command == "guides" then F.Minimap:ToggleMenu()
    elseif command == "options" then F.UI:ToggleOptions()
    elseif command == "refresh" then F.Refresh(); F.Print("Live quest data refreshed for client build " .. F.QuestData.saved.client.build .. ". /fg data exports observations.")
    elseif command == "data" then F.QuestData:ShowExport()
    elseif command == "" then
        F.UI:Toggle()
    else F.Print("/fg [next | back | skip | reset | debug | auto | guides | options | refresh | data]") end
end
