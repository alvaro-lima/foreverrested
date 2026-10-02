local _, F = ...
local M = {}
F.Minimap = M
function M:Create()
    if self.menu then return end
    local menu = F.UI:Panel(UIParent, 306, 266)
    menu.opaqueBase:SetColorTexture(.055,.045,.035,1)
    if menu.SetBackdropColor then menu:SetBackdropColor(.22,.19,.16,1) end
    self.menu = menu; menu:SetFrameStrata("DIALOG"); menu:SetClampedToScreen(true)
    menu:SetPoint("TOPLEFT", F.UI.frame, "TOPRIGHT", 8, 0)
    local menuIcon = menu:CreateTexture(nil, "ARTWORK")
    menuIcon:SetSize(22,22); menuIcon:SetPoint("TOPLEFT",10,-7); menuIcon:SetTexture(F.minimapIcon)
    F.UI:Text(menu, "GameFontNormal", "TOPLEFT", 38, -12, 249):SetText("Available Guides")
    self.bracketIndex = 1
    self.bracketLabel = F.UI:Text(menu, "GameFontNormal", "TOPLEFT", 82, -43, 146)
    local previous = F.UI:Button(menu, "<", 52, "TOPLEFT", 12, -34, function()
        self.bracketIndex = math.max(1, self.bracketIndex - 1); self:RefreshGuides()
    end)
    F.Tooltips:Text(previous, "Previous level bracket", "Browse guides for the previous ten levels.")
    local following = F.UI:Button(menu, ">", 52, "TOPLEFT", 242, -34, function()
        self.bracketIndex = math.min(#F.GuideLibrary.brackets, self.bracketIndex + 1); self:RefreshGuides()
    end)
    F.Tooltips:Text(following, "Next level bracket", "Browse guides for the next ten levels.")
    self.guideButtons = {}
    for index, id in ipairs(F.GuideLibrary.order) do
        local guideID = id
        local b = F.UI:Button(menu, F.GuideLibrary.guides[id].title, 282, "TOPLEFT", 12, -70 - (index - 1) * 27, function()
            F.GuideLibrary:Select(guideID); menu:Hide()
            if not F.Combat() then F.UI.frame:Show(); F.db.hidden = false end
        end)
        self.guideButtons[id] = b
    end
    self.guideNotice = F.UI:Text(menu, "GameFontHighlightSmall", "TOPLEFT", 12, -139, 282)
    self:RefreshGuides()
    F.UI:Button(menu, "Show / Hide", 92, "BOTTOMLEFT", 12, 40, function() F.UI:Toggle(); menu:Hide() end)
    self.lockButton = F.UI:Button(menu, "Lock", 84, "BOTTOMLEFT", 110, 40, function() F.UI:TogglePositionLock() end)
    self:RefreshLockButton()
    F.UI:Button(menu, "Close", 92, "BOTTOMLEFT", 200, 40, function() menu:Hide() end)
    F.UI:Button(menu, "Options", 92, "BOTTOMLEFT", 12, 12, function() F.UI:ToggleOptions(); menu:Hide() end)
    F.UI:Button(menu, "Refresh", 84, "BOTTOMLEFT", 110, 12, function() F.Refresh(); menu:Hide(); F.Print("Live quest data refreshed. /fg data exports this build's observations.") end)
    F.UI:Button(menu, "Data", 92, "BOTTOMLEFT", 200, 12, function() F.QuestData:ShowExport(); menu:Hide() end)
    menu:Hide()
    if not Minimap then return end
    local b = CreateFrame("Button", "ForeverRestedMinimapButton", Minimap)
    self.button = b; b:SetSize(31, 31); b:SetFrameStrata("MEDIUM"); b:SetFrameLevel(8)
    b:RegisterForClicks("LeftButtonUp", "RightButtonUp"); b:RegisterForDrag("LeftButton")
    -- Match Leatrix Plus's Classic LibDBIcon launcher geometry. The border is
    -- separate from the artwork, so its weight survives small UI sizes.
    local border = b:CreateTexture(nil, "OVERLAY")
    border:SetSize(53,53); border:SetPoint("TOPLEFT")
    border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
    local background = b:CreateTexture(nil, "BACKGROUND")
    background:SetSize(20,20); background:SetPoint("TOPLEFT",7,-5)
    background:SetTexture("Interface\\Minimap\\UI-Minimap-Background")
    local icon = b:CreateTexture(nil, "ARTWORK")
    icon:SetSize(20,20); icon:SetPoint("CENTER",b,"CENTER",1,-1); icon:SetTexture(F.minimapIcon)
    -- Dedicated simple artwork fills the native rim without a painted border.
    icon:SetTexCoord(0,1,0,1)
    b.icon, b.border = icon, border
    b:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight", "ADD")
    local function position()
        local angle = math.rad(F.db.minimapAngle or 225)
        local radius = (Minimap:GetWidth() or 140) / 2 + 8
        b:ClearAllPoints(); b:SetPoint("CENTER", Minimap, "CENTER", math.cos(angle) * radius, math.sin(angle) * radius)
    end
    position()
    b:SetScript("OnClick", function(_, button)
        if button == "RightButton" then self:ToggleMenu() else F.UI:Toggle() end
    end)
    F.Tooltips:Attach(b, function()
        if not GameTooltip then return end
        GameTooltip:SetOwner(b, "ANCHOR_LEFT"); GameTooltip:SetText("Forever Rested", 1, .82, 0)
        GameTooltip:AddLine("Left-click: show / hide guide window", 1, 1, 1)
        GameTooltip:AddLine("Right-click: guides and options menu", 1, 1, 1)
        GameTooltip:AddLine("Drag: move around the minimap", 1, 1, 1); GameTooltip:Show()
    end, true)
    b:SetScript("OnDragStart", function() b.dragging = true end)
    b:SetScript("OnDragStop", function() b.dragging = false end)
    b:SetScript("OnUpdate", function()
        if not b.dragging or not GetCursorPosition or not math.atan2 then return end
        local x, y = F.Call(GetCursorPosition)
        local cx, cy = Minimap:GetCenter(); local scale = Minimap:GetEffectiveScale()
        if F.Number(x) and F.Number(y) and F.Number(cx) and F.Number(cy) and F.Number(scale) and scale > 0 then
            F.db.minimapAngle = math.deg(math.atan2(y / scale - cy, x / scale - cx)); position()
        end
    end)
end
function M:RefreshLockButton()
    if not self.lockButton then return end
    local label = F.db.positionsLocked and "Unlock" or "Lock"
    self.lockButton:SetText(label)
    F.Tooltips:Text(self.lockButton, label, F.UI.buttonHelp[label], true)
end
function M:RefreshGuides()
    local bracket = F.GuideLibrary.brackets[self.bracketIndex]
    self.bracketLabel:SetText("Levels " .. bracket.min .. "-" .. bracket.max)
    for _, button in pairs(self.guideButtons) do button:Hide() end
    local ids = F.GuideLibrary:GuidesForBracket(self.bracketIndex)
    for index, id in ipairs(ids) do
        local button = self.guideButtons[id]
        button:ClearAllPoints(); button:SetPoint("TOPLEFT", self.menu, "TOPLEFT", 12, -70 - (index - 1) * 27)
        button:SetText((id == F.db.guideID and "* " or "") .. F.GuideLibrary.guides[id].title)
        button:Show()
    end
    self.menu:SetHeight(266 + math.max(0, #ids - 2) * 27)
    self.guideNotice:ClearAllPoints()
    self.guideNotice:SetPoint("TOPLEFT", self.menu, "TOPLEFT", 12, -139 - math.max(0, #ids - 2) * 27)
    self.guideNotice:SetText(#ids > 0 and "Alliance 1-30 guides. Class quests adapt to your character; Zephras has an optional 10-14 extension."
        or "No route available yet for this level bracket.")
end
function M:ToggleMenu()
    if not self.menu then self:Create() end
    if not self.menu:IsShown() then
        local level = F.Call(UnitLevel, "player") or 1
        self.bracketIndex = F.GuideLibrary:BracketIndex(level)
        if F.Guide and level == F.Guide.maxLevel then
            self.bracketIndex = F.GuideLibrary:BracketIndex(F.Guide.minLevel)
        end
    end
    self:RefreshGuides()
    if self.button then
        self.menu:ClearAllPoints(); self.menu:SetPoint("TOPRIGHT", self.button, "BOTTOMLEFT", 0, -3)
    end
    self.menu:SetShown(not self.menu:IsShown())
end
