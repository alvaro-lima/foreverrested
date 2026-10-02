local _, F = ...
local U = {fonts = {}}
F.UI = U
function U:RowIconSize()
    return math.floor((F.db.fontSize or 12) * (28 / 12) + .5)
end
U.stateLabels = {complete = "COMPLETE", ongoing = "ONGOING", ready = "READY TO TURN IN",
    notready = "OBJECTIVES PENDING", waiting = "NOT STARTED", skipped = "SKIPPED", failed = "FAILED"}
function U:StateIcon(state)
    -- Native checkbox art confirmed in the installed AceGUI widget library.
    local size = F.db.fontSize or 12
    local file = state == "complete" and "Interface\\Buttons\\UI-CheckBox-Check" or state == "skipped" and "Interface\\Buttons\\UI-GroupLoot-Pass-Up" or "Interface\\Buttons\\UI-CheckBox-Up"
    return "|T" .. file .. ":" .. size .. ":" .. size .. "|t "
end
U.buttonHelp = {
    Previous = "Review the previous step. Auto returns to your current quest progress.",
    Next = "Browse the next step. This does not mark the current step complete.",
    Skip = "Skip this step. Auto remembers explicitly skipped steps.",
    ["From.."] = "Start again from the selected step. Clears skips and manual confirmations for this step and all later steps. Earlier progress and live quest completion are kept. Next, Skip or Auto resumes automation.",
    Auto = "Return to the first unfinished, unskipped step using your live quest progress.",
    ["Show / Hide"] = "Show or hide the quest window. The arrow and targets remain independent.",
    Options = "Open addon settings, including font size.",
    ["-"] = "Decrease addon text size by one. This setting is saved for this character.",
    ["+"] = "Increase addon text size by one. This setting is saved for this character.",
    Default = "Restore the default font size of 12.",
    Close = "Close this menu or options window.",
    Refresh = "Rescan live quest objectives for the current client build. Imported data updates require /reload.",
    Data = "Open current-build quest observations for copying into the offline data refresh tool.",
}
function U:Text(parent, font, anchor, x, y, width)
    local t = parent:CreateFontString(nil, "OVERLAY", font)
    local face, _, flags = F.Call(t.GetFont, t)
    if face then t:SetFont(face, F.db.fontSize or 12, flags or "") end
    self.fonts[#self.fonts + 1] = t
    t:SetSpacing(1)
    t:SetPoint(anchor, x, y); t:SetWidth(width); t:SetJustifyH("LEFT"); t:SetJustifyV("TOP")
    return t
end
function U:NativeBorder(frame, layoutName)
    local layout = F.Call(NineSliceUtil and NineSliceUtil.GetLayout, layoutName)
    if type(layout) ~= "table" or not NineSliceUtil.ApplyLayoutByName then return false end
    -- Check the running client, rather than assuming a modern layout/atlas exists.
    for _, piece in pairs(layout) do
        if type(piece) == "table" and piece.atlas and not F.Call(C_Texture and C_Texture.GetAtlasInfo, piece.atlas) then
            return false
        end
    end
    local border = F.Call(CreateFrame, "Frame", nil, frame, "NineSlicePanelTemplate")
    if not border then return false end
    border:SetAllPoints(frame)
    if not pcall(NineSliceUtil.ApplyLayoutByName, border, layoutName) then border:Hide(); return false end
    frame.nativeBorder, frame.nativeLayout = border, layoutName
    return true
end
function U:Panel(parent, width, height, style)
    local f = F.Frame("Frame", nil, parent, "BackdropTemplate")
    f:SetSize(width, height)
    -- Keep the native rock texture subdued while allowing the world to show through.
    local base = f:CreateTexture(nil, "BACKGROUND", nil, -8)
    base:SetPoint("TOPLEFT", 3, -3); base:SetPoint("BOTTOMRIGHT", -3, 3)
    base:SetColorTexture(.055, .045, .035, .12)
    f.opaqueBase = base
    local guidePanel = style == "header" or style == "outer"
    local native = not guidePanel and self:NativeBorder(f, "InsetFrameTemplate")
    if f.SetBackdrop then
        -- Rock texture and fallback border confirmed in installed Auctionator/Leatrix.
        f:SetBackdrop({bgFile = "Interface\\FrameGeneral\\UI-Background-Rock",
            edgeFile = not native and "Interface\\Tooltips\\UI-Tooltip-Border" or nil,
            tile = true, tileSize = 64, edgeSize = style == "header" and 8 or 12,
            insets = {left = 3, right = 3, top = 3, bottom = 3}})
        if style == "header" then f:SetBackdropColor(.16, .10, .055, .75)
        else f:SetBackdropColor(.22, .19, .16, style == "outer" and .50 or .30) end
        f:SetBackdropBorderColor(.65, .48, .22, 1)
        if guidePanel then
            base:SetColorTexture(.07,.035,.015,1)
            f:SetBackdrop({bgFile="Interface\\FrameGeneral\\UI-Background-Rock",
                edgeFile="Interface\\DialogFrame\\UI-DialogBox-Gold-Border",
                tile=true,tileSize=64,edgeSize=16,insets={left=4,right=4,top=4,bottom=4}})
            f:SetBackdropColor(.2,.1,.04,1)
            f:SetBackdropBorderColor(.75,.63,.4,1)
        end
    end
    return f
end
function U:Button(parent, title, width, anchor, x, y, callback)
    local b = F.Frame("Button", nil, parent, "UIPanelButtonTemplate")
    b:SetSize(width, 22); b:SetPoint(anchor, x, y); b:SetText(title); b:SetScript("OnClick", callback)
    F.Tooltips:Text(b, title, self.buttonHelp[title] or ("Select this guide. Each guide remembers its own progress."))
    return b
end
function U:Create()
    local size = F.db.windowSize
    local width = type(size) == "table" and F.Number(size.width) and math.max(400, math.min(900, size.width)) or 400
    local height = type(size) == "table" and F.Number(size.height) and math.max(520, math.min(1000, size.height)) or 742
    local f = self:Panel(UIParent, width, height, "outer")
    self.frame = f; f:SetClampedToScreen(true); f:SetMovable(true); f:EnableMouse(true)
    f:SetResizable(true)
    if f.SetResizeBounds then f:SetResizeBounds(400, 520, 900, 1000)
    elseif f.SetMinResize then f:SetMinResize(400, 520); if f.SetMaxResize then f:SetMaxResize(900, 1000) end end
    local p = F.db.position
    if type(p) == "table" and F.Number(p.x) and F.Number(p.y) then
        f:SetPoint("CENTER", UIParent, "CENTER", p.x, p.y)
    else f:SetPoint("CENTER", UIParent, "CENTER", 280, 0) end
    local header = self:Panel(f, 380, 27, "header"); header:SetPoint("BOTTOMLEFT",f,"TOPLEFT",0,2)
    self.header = header
    -- Bronze framed title bar, with a large circular portrait overlapping its edge.
    local addonIcon = header:CreateTexture(nil, "ARTWORK")
    addonIcon:SetSize(52,52); addonIcon:SetPoint("TOPLEFT",-10,6); addonIcon:SetTexture(F.icon)
    self.addonIcon=addonIcon
    self.addonTitle = self:Text(header, "GameFontNormal", "TOPLEFT", 48, -12, 140)
    self.addonTitle:SetText("Forever Rested")
    header:EnableMouse(true); header:RegisterForDrag("LeftButton")
    header:SetScript("OnDragStart", function() if not F.Combat() then f:StartMoving() end end)
    header:SetScript("OnDragStop", function()
        f:StopMovingOrSizing()
        local x, y = f:GetCenter(); local ux, uy = UIParent:GetCenter()
        F.db.position = {x = x - ux, y = y - uy}
    end)
    self.headerTitle = self:Text(header, "GameFontNormal", "TOPLEFT", 9, -7, 330)
    self.headerTitle:SetJustifyH("CENTER")
    self.headerTitle:SetWordWrap(false)
    local close = F.Frame("Button", nil, header, "UIPanelCloseButton")
    close:SetSize(26, 26); close:SetPoint("TOPRIGHT", 0, 0)
    close:SetScript("OnClick", function()
        self:Toggle()
    end)
    F.Tooltips:Text(close, "Hide quest window", "Hide the guide window. Use /fg or the minimap icon to show it again.")
    F.Arrow:Create()
    F.Tracker:Create(f)
    self.footerButtons = {
        self:Button(f, "From..", 80, "BOTTOMLEFT", 16, 10, function() F.GuideEngine:ResetFrom() end),
        self:Button(f, "Previous", 108, "BOTTOMLEFT", 102, 10, function() F.GuideEngine:Move(-1) end),
        self:Button(f, "Next", 80, "BOTTOMLEFT", 216, 10, function() F.GuideEngine:Move(1) end),
        self:Button(f, "Skip", 80, "BOTTOMLEFT", 302, 10, function() F.GuideEngine:Move(1, true) end),
        self:Button(f, "Auto", 80, "BOTTOMLEFT", 388, 10, function() F.GuideEngine:ResumeAuto() end),
    }
    local debug = self:Panel(UIParent, 400, 145)
    debug:SetPoint("TOPLEFT", f, "BOTTOMLEFT", 0, -4)
    self.debugFrame = debug; self.debugText = self:Text(debug, "GameFontHighlightSmall", "TOPLEFT", 9, -9, 380)
    self.debugText:SetHeight(130); debug:Hide()
    local grip = CreateFrame("Button", nil, f)
    self.resizeGrip = grip; grip:SetSize(18, 18); grip:SetPoint("BOTTOMRIGHT", -4, 4)
    F.Tooltips:Text(grip, "Resize quest window", "Drag this corner to resize the window. Width, height and position are saved.")
    self:Text(grip, "GameFontNormal", "CENTER", 0, 0, 18):SetText("//")
    grip:SetScript("OnMouseDown", function(_, button)
        if button == "LeftButton" then f:StartSizing("BOTTOMRIGHT") end
    end)
    grip:SetScript("OnMouseUp", function()
        f:StopMovingOrSizing(); self:SaveWindowGeometry()
    end)
    f:SetScript("OnSizeChanged", function(_, w, h) self:Layout(w, h) end)
    self:Layout(width, height)
    if F.db.hidden then f:Hide() end
end
function U:SaveWindowGeometry()
    local width, height = self.frame:GetWidth(), self.frame:GetHeight()
    if F.Number(width) and F.Number(height) then F.db.windowSize = {width = width, height = height} end
    local x, y = self.frame:GetCenter(); local ux, uy = UIParent:GetCenter()
    if F.Number(x) and F.Number(y) and F.Number(ux) and F.Number(uy) then F.db.position = {x = x - ux, y = y - uy} end
end
function U:Layout(width, height)
    if not F.Tracker.frame then return end
    -- Keep normal widths when they fit; compact only as the window narrows.
    -- Reserve the right corner for the resize grip and keep every full label.
    local compact = math.max(0, math.min(1, (550 - width) / 150))
    local buttonWidth, previousWidth = 80 - 28 * compact, 108 - 28 * compact
    local gap, buttonX = 6 - 2 * compact, 16
    for index, button in ipairs(self.footerButtons or {}) do
        local size = index == 2 and previousWidth or buttonWidth
        button:ClearAllPoints(); button:SetPoint("BOTTOMLEFT", self.frame, "BOTTOMLEFT", buttonX, 10)
        button:SetWidth(size)
        buttonX = buttonX + size + gap
    end
    local fontSize = F.db.fontSize or 12
    local headerWidth = width
    local titleHeight = math.max(44, fontSize + 24)
    local nameWidth = F.Call(self.addonTitle.GetStringWidth, self.addonTitle) or fontSize * 8
    self.addonTitle:SetWidth(nameWidth + 2)
    self.headerTitle:SetText(F.Guide.title)
    -- Use the full space after the addon name, reserving only the close button.
    local guideLeft = nameWidth + 60
    local rightSpace = 36
    local guideWidth = F.Call(self.headerTitle.GetStringWidth, self.headerTitle) or 0
    local secondLine = guideWidth > headerWidth - guideLeft - rightSpace
    local titleLeft = math.max(guideLeft,(headerWidth-guideWidth)/2)
    self.header:SetSize(headerWidth, secondLine and titleHeight * 2 or titleHeight)
    self.addonTitle:ClearAllPoints()
    self.addonTitle:SetPoint("TOPLEFT",48,0)
    self.addonTitle:SetHeight(titleHeight)
    self.addonTitle:SetJustifyV("MIDDLE")
    self.headerTitle:ClearAllPoints()
    self.headerTitle:SetPoint("TOPLEFT", secondLine and 12 or titleLeft, secondLine and -titleHeight or 0)
    self.headerTitle:SetSize(secondLine and headerWidth - 24 or math.min(guideWidth+2,headerWidth-titleLeft-rightSpace), titleHeight)
    self.headerTitle:SetJustifyV("MIDDLE")
    local trackerTop = 10
    F.Tracker.frame:ClearAllPoints(); F.Tracker.frame:SetPoint("TOPLEFT", 8, -trackerTop)
    -- End the list just above the bottom buttons.
    F.Tracker.frame:SetSize(width - 16, math.max(100, height - trackerTop - 36))
    F.Tracker.scrollbar:ClearAllPoints()
    F.Tracker.scrollbar:SetPoint("TOPRIGHT", -2, -(fontSize + 36))
    F.Tracker.scrollbar:SetPoint("BOTTOMRIGHT", -2, 16)
    local badgeSize = self:RowIconSize()
    F.Tracker.rowHeight = math.max(38, badgeSize + 8)
    local headers = F.Tracker.headers
    headers.Step:SetText("Step")
    local headingWidth = F.Call(headers.Step.GetStringWidth, headers.Step)
    local stepWidth = math.max((F.db.fontSize or 12) * 3,
        F.Number(headingWidth) and headingWidth + 8 or (F.db.fontSize or 12) * 6.5)
    headers.Status:SetText("Status " .. #F.Guide.steps .. " / " .. #F.Guide.steps)
    local statusHeadingWidth = F.Call(headers.Status.GetStringWidth, headers.Status)
    local statusWidth = math.max((F.db.fontSize or 12) * 4.5,
        F.Number(statusHeadingWidth) and statusHeadingWidth + 8 or (F.db.fontSize or 12) * 9)
    local questX = stepWidth + 24
    local statusX = width - 56 - statusWidth - 10
    headers.Step:ClearAllPoints(); headers.Step:SetPoint("TOPLEFT", 18, -5); headers.Step:SetWidth(stepWidth)
    headers.Step:SetJustifyH("CENTER")
    headers.Quest:ClearAllPoints(); headers.Quest:SetPoint("TOPLEFT", questX + 8, -5); headers.Quest:SetWidth(statusX - questX - 12)
    headers.Status:ClearAllPoints(); headers.Status:SetPoint("TOPLEFT", statusX + 8, -5); headers.Status:SetWidth(statusWidth)
    headers.Status:SetJustifyH("CENTER")
    for _, row in ipairs(F.Tracker.rows) do
        row:SetWidth(width - 56)
        row.stepBadge:ClearAllPoints(); row.stepBadge:SetPoint("LEFT", row, "LEFT", 10 + (stepWidth - badgeSize) / 2, 0)
        row.stepBadge:SetSize(badgeSize, badgeSize)
        row.stepGlow:SetSize(badgeSize * 1.65, badgeSize * 1.65)
        row.text:SetSize(badgeSize, badgeSize)
        row.text:SetSpacing(0)
        row.text:ClearAllPoints(); row.text:SetPoint("CENTER",row.stepBadge,"CENTER",0,0)
        row.body:ClearAllPoints(); row.body:SetPoint("TOPLEFT", questX, -10)
        row.body:SetWidth(statusX - questX - 12)
        row.statusButton:ClearAllPoints(); row.statusButton:SetPoint("TOPLEFT", statusX, 0); row.statusButton:SetPoint("BOTTOMRIGHT", -10, 0)
        row.status:SetSize(badgeSize, badgeSize)
        row.status:ClearAllPoints(); row.status:SetPoint("CENTER",row.statusButton,"CENTER",0,0)
        row.statusSymbol:SetSize(badgeSize, badgeSize)
    end
    F.Tracker:Refresh()
end
function U:SetFontSize(size)
    F.db.fontSize = math.max(11, math.min(20, math.floor(size)))
    for _, text in ipairs(self.fonts) do
        local face, _, flags = F.Call(text.GetFont, text)
        if face then text:SetFont(face, F.db.fontSize, flags or "") end
    end
    self:Layout(self.frame:GetWidth(), self.frame:GetHeight())
    self:Refresh()
    if self.optionsLabel then self.optionsLabel:SetText("Font size: " .. F.db.fontSize) end
end
function U:ToggleOptions()
    if not self.options then
        local panel = self:Panel(UIParent, 300, 236)
        self.options = panel; panel:SetFrameStrata("DIALOG"); panel:SetClampedToScreen(true)
        panel:SetPoint("CENTER", UIParent, "CENTER", 0, 0)
        local optionsIcon = panel:CreateTexture(nil, "ARTWORK")
        optionsIcon:SetSize(22,22); optionsIcon:SetPoint("TOPLEFT",10,-7); optionsIcon:SetTexture(F.minimapIcon)
        self:Text(panel, "GameFontNormal", "TOPLEFT", 38, -12, 244):SetText("Forever Rested Options")
        self.optionsLabel = self:Text(panel, "GameFontHighlight", "TOPLEFT", 12, -46, 270)
        self:Button(panel, "-", 46, "BOTTOMLEFT", 12, 137, function() self:SetFontSize(F.db.fontSize - 1) end)
        self:Button(panel, "+", 46, "BOTTOMLEFT", 64, 137, function() self:SetFontSize(F.db.fontSize + 1) end)
        self:Button(panel, "Default", 94, "BOTTOMLEFT", 116, 137, function() self:SetFontSize(12) end)
        self.arrowSizeLabel = self:Text(panel, "GameFontHighlight", "TOPLEFT", 12, -126, 270)
        local function arrowButton(title, width, x, size, help)
            local button = self:Button(panel, title, width, "BOTTOMLEFT", x, 57, function()
                F.Arrow:SetSize(type(size) == "function" and size() or size)
                self.arrowSizeLabel:SetText("Arrow size: " .. F.db.arrowSize .. " px")
            end)
            F.Tooltips:Text(button, "Arrow size", help)
        end
        arrowButton("-", 46, 12, function() return F.db.arrowSize - 4 end, "Make the navigation arrow smaller. Minimum size: 24 px.")
        arrowButton("+", 46, 64, function() return F.db.arrowSize + 4 end, "Make the navigation arrow larger. Maximum size: 96 px.")
        arrowButton("Default", 94, 116, 48, "Restore the default arrow size of 48 px.")
        self:Button(panel, "Close", 92, "BOTTOMRIGHT", -12, 12, function() panel:Hide() end)
        panel:Hide()
    end
    self.optionsLabel:SetText("Font size: " .. F.db.fontSize)
    self.arrowSizeLabel:SetText("Arrow size: " .. F.db.arrowSize .. " px")
    self.options:SetShown(not self.options:IsShown())
end
function U:Toggle()
    if F.Combat() then F.Print("Window visibility is locked during combat."); return end
    local visible = not self.frame:IsShown()
    self.frame:SetShown(visible); F.db.hidden = not visible; self:Debug()
    if F.StepPins then F.StepPins:Update() end
end
function U:TaskText(task)
    local id, q = F.GuideEngine:Resolve(task)
    local fixture = task.slot and F.Guide.quests[task.slot]
    local state = F.GuideEngine:TaskState(task)
    local done = state == "complete"
    local metadata = F.GuideEngine:Metadata(id)
    local title = q and q.title or metadata and metadata.title or fixture and fixture.title or task.text or "Guide note"
    local prefix = ({pickup="Accept", turnin="Turn in", objective="Objective", trainer="Trainer", travel="Travel", grind="Level", note="Note"})[task.type] or "Objective"
    local color = done and "|cff40ff40" or state == "failed" and "|cffff4444" or "|cffffd100"
    local text = self:StateIcon(state) .. color .. prefix .. ": " .. title .. "|r"
    text = text .. "\n  " .. color .. self.stateLabels[state] .. "|r"
    if metadata and not done and (task.type == "pickup" or task.type == "turnin") then
        local observed = F.QuestData:Get(id)
        local rewardXP = observed and observed.rewardXPObserved
        if rewardXP and rewardXP.playerLevel == F.Call(UnitLevel, "player") then
            text = text .. "\n  Observed XP " .. rewardXP.value .. " (this level/build)"
        elseif metadata.listedXP and metadata.listedXP > 0 then
            text = text .. "\n  Listed XP ~" .. metadata.listedXP .. " (beta estimate)"
        end
        local rewards = {}
        for _, reward in ipairs(metadata.rewards) do
            if reward.name and #rewards < 3 then
                local tint = reward.quality == 3 and "|cff0070dd" or reward.quality == 2 and "|cff1eff00" or "|cffffffff"
                rewards[#rewards+1] = tint .. reward.name .. "|r"
            end
        end
        if #rewards > 0 then text = text .. "\n  Rewards: " .. table.concat(rewards, ", ") end
    end
    if not done and task.type == "objective" and q then
        if task.objective then
            local objective = q.objectives[task.objective]
            text = text .. "\n  " .. (objective and (objective.text or F.QuestLog:Progress(objective)) or "Waiting for objective data")
        else text = text .. "\n  " .. (q.complete and "Ready to turn in" or "Finish all quest objectives") end
    elseif not id and task.slot then text = text .. "\n  Accept a quest to bind this test entry." end
    return text
end
-- Native gossip icons also used by the installed RXPGuides client addon.
function U:ActionIcon(kind, size)
    local icon=({pickup="AvailableQuestIcon",turnin="ActiveQuestIcon",talk="GossipGossipIcon",trainer="GossipGossipIcon"})[kind]
    size = size or F.db.fontSize or 12
    return icon and ("|TInterface\\GossipFrame\\"..icon..":"..size..":"..size.."|t ") or ""
end
function U:ActionTitle(task, iconSize)
    if task.tasks and #task.tasks==1 then task=task.tasks[1] end
    local id,q=F.GuideEngine:Resolve(task)
    local data=F.GuideEngine:Metadata(id)
    local fixture=task.slot and F.Guide.quests[task.slot]
    local title=q and q.title or data and data.title or fixture and fixture.title or task.text or "Guide note"
    if task.type=="pickup" then return self:ActionIcon("pickup",iconSize).."Accept "..title end
    if task.type=="turnin" then return self:ActionIcon("turnin",iconSize).."Turn in "..title end
    if task.type=="objective" and q then
        local pending={}
        for index,o in ipairs(q.objectives) do
            if (not task.objective or task.objective==index) and not o.finished then pending[#pending+1]={o=o,index=index} end
        end
        if #pending==1 then
            local o,index=pending[1].o,pending[1].index
            local mob=task.mob or F.GuideEngine:MappedTarget(q,o,index)
            local name=(o.text or ""):gsub("^%s*%d+%s*/%s*%d+%s*", ""):gsub(":%s*%d+%s*/%s*%d+.*$", ""):gsub("%s+slain$", "")
            if mob then return (o.type=="monster" and "Kill " or "Hunt ")..mob end
            if name~="" then return (o.type=="monster" and "Kill " or o.type=="item" and "Collect " or "Complete ")..name end
        end
        return "Complete "..title
    end
    return self:ActionIcon(task.type,iconSize)..(task.text or title)
end
function U:CriticalIcon(size)
    size = size or F.db.fontSize or 12
    return "|TInterface\\DialogFrame\\UI-Dialog-Icon-Alert:"..size..":"..size..":0:0|t "
end
function U:ActionBody(task)
    local id,q=F.GuideEngine:Resolve(task)
    local data=F.GuideEngine:Metadata(id)
    local lines={}
    if task.type=="pickup" or task.type=="turnin" then
        if task.type=="pickup" and task.recovery then
            local fallback=F.ClassicQuestPolicy and F.ClassicQuestPolicy.records[id]
            for _,itemID in ipairs((data and data.startItemIDs) or (fallback and fallback.startItemIDs) or {}) do
                local name=F.Call(GetItemInfo,itemID) or ("item #"..itemID)
                lines[#lines+1]="Use "..name.." in your bags to start this quest."
            end
        end
        for _,point in ipairs(data and data.locations or {}) do
            if point.role==(task.type=="pickup" and "start" or "end") and point.name then
                lines[#lines+1]=self:ActionIcon("talk").."Talk to |cff40ff40"..point.name.."|r";break
            end
        end
        if task.type=="turnin" and q and not q.complete then lines[#lines+1]="|cffffd100Finish the remaining objectives first.|r" end
    elseif task.type=="objective" then
        if q then
            lines[#lines+1]="|cffffd100"..q.title.."|r"
            for index,o in ipairs(q.objectives) do
                if not task.objective or task.objective==index then
                    lines[#lines+1]=self:StateIcon(o.finished and "complete" or "ongoing")..(o.finished and "|cff40ff40" or "|cffffffff")..(o.text or F.QuestLog:Progress(o)).."|r"
                end
            end
        else lines[#lines+1]="Accept this quest before completing its objectives." end
    end
    return table.concat(lines,"\n")
end
function U:Refresh()
    F.GuideEngine:Current()
    self.headerTitle:SetText(F.Guide.title)
    F.db.view = "steps"
    if self.lastGuide ~= F.Guide then F.GuideEngine.selectedStep = nil end
    if self.lastGuide ~= F.Guide or (self.lastStep ~= F.db.step and not F.GuideEngine.selectedStep) then
        F.Tracker.topOffset = nil
        F.Tracker.offset = math.max(0, F.db.step - 1)
    end
    self.lastStep, self.lastGuide = F.db.step, F.Guide
    self:Layout(self.frame:GetWidth(), self.frame:GetHeight())
    F.SecureTarget:UpdateTasks(F.GuideEngine:Targets())
    self:NavigationTick()
end
function U:NavigationTick()
    F.Navigation:Update(); F.Arrow:Update()
    if F.StepPins then F.StepPins:Update() end
    local n = F.Navigation
    self:Debug()
end
function U:Debug()
    if not F.db.debug or not self.frame:IsShown() then self.debugFrame:Hide(); return end
    self.debugFrame:Show()
    local step, id, q = F.GuideEngine:Focus(); local n = F.Navigation
    local function pos(x, y) return F.Number(x) and F.Number(y) and string.format("%.2f, %.2f", x * 100, y * 100) or "unavailable" end
    local o = q and q.objectives[step.objective or 1]
    local _, version, _, interface = F.Call(GetBuildInfo)
    self.debugText:SetText("DEBUG | client " .. tostring(version) .. " / interface " .. tostring(interface)
        .. "\nStep " .. F.db.step .. " (" .. step.type .. ") | questID " .. tostring(id)
        .. "\nPlayer map " .. tostring(n.map) .. " | " .. pos(n.px, n.py)
        .. "\nTarget map " .. tostring(n.targetMap) .. " | " .. pos(n.tx, n.ty)
        .. "\nDistance " .. (n.distance and string.format("%.1f yd", n.distance) or "unavailable") .. " | " .. tostring(n.source)
        .. "\nObjective " .. F.QuestLog:Progress(o) .. " | finished=" .. tostring(o and o.finished)
        .. "\nAccepted=" .. tostring(q ~= nil) .. " complete=" .. tostring(q and q.complete) .. " turnedIn=" .. tostring(F.QuestLog:TurnedIn(id))
        .. "\nTarget=" .. tostring(F.SecureTarget.current) .. (F.SecureTarget.pending and " (update queued for combat end)" or ""))
end
