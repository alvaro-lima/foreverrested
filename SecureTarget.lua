local _, F = ...
local S = {buttons = {}, capacity = 8, markerOrder = {8, 7, 6, 5, 4, 3, 2, 1}}
F.SecureTarget = S
local markerNames = {"Star", "Circle", "Diamond", "Triangle", "Moon", "Square", "Cross", "Skull"}
local function sanitize(mob)
    if type(mob) ~= "string" or #mob == 0 or #mob > 120 or mob:find("[\r\n/;]") then return end
    return mob
end
function S:Create()
    local panel = CreateFrame("Frame",nil,UIParent)
    panel:SetSize(160,80)
    local box = CreateFrame("Frame",nil,panel)
    box:SetPoint("TOPLEFT",0,-24); box:SetPoint("BOTTOMRIGHT",0,0)
    self.box = box
    local fill=box:CreateTexture(nil,"BACKGROUND")
    fill:SetPoint("TOPLEFT",7,-7); fill:SetPoint("BOTTOMRIGHT",-7,7)
    fill:SetColorTexture(.025,.02,.015,.6)
    local path="Interface\\AddOns\\"..F.name.."\\Media\\TargetsBorder"
    local function piece(l,r,t,b)
        local texture=box:CreateTexture(nil,"BORDER")
        texture:SetTexture(path);texture:SetTexCoord(l,r,t,b)
        return texture
    end
    local c=.1
    local edge=14 -- Approximately one extra pixel of visible bronze edge.
    for _,corner in ipairs({{"TOPLEFT",0,c,0,c},{"TOPRIGHT",1-c,1,0,c},
        {"BOTTOMLEFT",0,c,1-c,1},{"BOTTOMRIGHT",1-c,1,1-c,1}}) do
        local texture=piece(corner[2],corner[3],corner[4],corner[5])
        texture:SetSize(edge,edge);texture:SetPoint(corner[1],box,corner[1],0,0)
    end
    local top=piece(c,1-c,0,c)
    top:SetHeight(edge);top:SetPoint("TOPLEFT",edge,0);top:SetPoint("TOPRIGHT",-edge,0)
    local bottom=piece(c,1-c,1-c,1)
    bottom:SetHeight(edge);bottom:SetPoint("BOTTOMLEFT",edge,0);bottom:SetPoint("BOTTOMRIGHT",-edge,0)
    local left=piece(0,c,c,1-c)
    left:SetWidth(edge);left:SetPoint("TOPLEFT",0,-edge);left:SetPoint("BOTTOMLEFT",0,edge)
    local right=piece(1-c,1,c,1-c)
    right:SetWidth(edge);right:SetPoint("TOPRIGHT",0,-edge);right:SetPoint("BOTTOMRIGHT",0,edge)
    self.frame = panel
    local title = panel:CreateFontString(nil,"OVERLAY","GameFontNormal")
    title:SetPoint("TOP",panel,"TOP",0,-8)
    title:SetText("Targets"); title:SetTextColor(1,.82,0)
    title:SetShadowColor(0,0,0,1); title:SetShadowOffset(1,-1)
    self.title = title
    panel:SetMovable(true); panel:SetClampedToScreen(true); panel:EnableMouse(true)
    local p = F.db.targetPosition
    if type(p) == "table" and F.Number(p.x) and F.Number(p.y) then
        panel:SetPoint("CENTER", UIParent, "CENTER", p.x, p.y)
    else panel:SetPoint("CENTER", UIParent, "CENTER", 520, 160) end
    local function dragStart()
        if F.Combat() then return end
        self.dragging = true; panel:StartMoving()
    end
    local function dragStop()
        if not self.dragging then return end
        if F.Combat() then self.stopPending = true; return end
        self:StopDragging()
    end
    panel:RegisterForDrag("LeftButton", "RightButton")
    panel:SetScript("OnDragStart", dragStart); panel:SetScript("OnDragStop", dragStop)
    self.markerCommand = self:MarkerCommand()
    local source = TargetFrame and TargetFrame.raidTargetIcon
    local markerTexture = source and F.Call(source.GetTexture, source)
        or "Interface\\TargetingFrame\\UI-RaidTargetingIcons"
    -- Allocate a fixed secure pool before combat. Protected targets stay frozen
    -- together until combat ends, including their visibility and layout.
    for i = 1, self.capacity do
        local b = F.Call(CreateFrame, "Button", "ForeverRestedTargetButton" .. i, panel,
            "SecureActionButtonTemplate")
        if not b then F.Print("Secure target template unavailable; Target disabled."); break end
        b:SetSize(32, 32); b:SetPoint("TOPLEFT",10+((i - 1) % 4)*36,-34-math.floor((i - 1)/4)*36)
        b.marker = self.markerOrder[i]
        b.markerName = _G["RAID_TARGET_" .. b.marker] or markerNames[b.marker]
        b:RegisterForClicks("LeftButtonUp"); b:RegisterForDrag("RightButton")
        b:SetAttribute("useOnKeyDown", false); b:SetAttribute("type", "macro"); b:SetAttribute("macrotext", "")
        local icon = b:CreateTexture(nil, "ARTWORK")
        b.markerIcon = icon
        icon:SetAllPoints(); icon:SetTexture(markerTexture)
        if type(SetRaidTargetIconTexture) == "function" then
            SetRaidTargetIconTexture(icon, b.marker)
        else
            -- Blizzard's native 4x4 sheet: each marker occupies a 64px cell.
            local cell = b.marker - 1
            local left, top = (cell % 4) / 4, math.floor(cell / 4) / 4
            icon:SetTexCoord(left, left + .25, top, top + .25)
        end
        b:SetScript("PostClick",function(button,click)
            if click=="LeftButton" and button.mob and F.Call(UnitName,"target")==button.mob
                and F.Call(UnitIsDeadOrGhost,"target")~=true and F.Call(UnitCanAttack,"player","target")==true then
                self.toolTargetGUID=F.Call(UnitGUID,"target")
                if F.UI.frame then F.UI:NavigationTick() end
            end
        end)
        b:SetScript("OnDragStart", dragStart); b:SetScript("OnDragStop", dragStop)
        F.Tooltips:Attach(b, function(button)
            if not GameTooltip then return end
            GameTooltip:SetOwner(button, "ANCHOR_RIGHT")
            GameTooltip:SetText(button.mob or "No kill target", 1, .82, 0)
            GameTooltip:AddLine("Marker: " .. button.markerName, 1, .82, 0)
            if button.progress then GameTooltip:AddLine(button.progress, 1, 1, 1, true) end
            GameTooltip:AddLine("Dead and friendly targets are rejected. Busy mobs cannot be filtered automatically.",1,1,1,true)
            GameTooltip:AddLine(self.markerCommand and "Left-click to target and mark. Right-drag to move panel."
                or "Left-click to target. Marking unavailable on this client.", 1, .82, 0, true)
            if self.markerCommand then GameTooltip:AddLine("Marking follows your party / raid permissions.", 1, 1, 1, true) end
            if F.Combat() then GameTooltip:AddLine("Targets remain fixed until combat ends.", 1, .82, 0, true) end
            GameTooltip:Show()
        end)
        b:Hide(); self.buttons[i] = b
    end
    self.button = self.buttons[1]
end
function S:MarkerCommand()
    if type(SetRaidTarget) ~= "function" then return end
    -- Read the installed client's localized native slash alias. No custom slash
    -- handlers or insecure calls to SetRaidTarget are installed by this addon.
    local alias = SLASH_TARGET_MARKER1 or SLASH_RAIDTARGET1
    if type(alias) == "string" and alias:match("^/%S+$") then return alias end
    if SlashCmdList and (SlashCmdList.TARGET_MARKER or SlashCmdList.RAIDTARGET) then return "/tm" end
end
function S:Macro(mob, marker)
    if not mob then return "" end
    -- Clear the previous target first: a failed name lookup must never mark an
    -- unrelated unit. Native conditions reject missing, friendly or dead units.
    -- The ! prefix makes repeated clicks retain the marker rather than toggle it.
    local macro = "/cleartarget\n/targetexact " .. mob .. "\n/cleartarget [@target,dead][@target,noharm]"
    if self.markerCommand then macro = macro .. "\n" .. self.markerCommand .. " [@target,exists,harm,nodead] !" .. marker end
    return macro
end
function S:StopDragging()
    if not self.dragging or F.Combat() then return end
    local f = self.frame
    f:StopMovingOrSizing()
    local x, y = f:GetCenter(); local ux, uy = UIParent:GetCenter()
    if F.Number(x) and F.Number(y) and F.Number(ux) and F.Number(uy) then
        F.db.targetPosition = {x = x - ux, y = y - uy}
        f:ClearAllPoints(); f:SetPoint("CENTER", UIParent, "CENTER", x - ux, y - uy)
    end
    self.dragging, self.stopPending = nil, nil
end
function S:Update(mob)
    self:UpdateTasks(mob and {{mob = mob}} or {})
end
function S:UpdateTasks(targets)
    local clean, used = {}, {}
    for _, target in ipairs(targets or {}) do
        local mob = sanitize(target.mob)
        if mob and not used[mob] then
            used[mob] = true; clean[#clean + 1] = {mob = mob, text = target.text}
        end
    end
    self.desiredTargets = clean; self.desired = clean[1] and clean[1].mob
    if F.Combat() then self.pending = true; return end
    self.pending = nil
    if not self.frame then return end
    if self.stopPending then self:StopDragging() end
    for i, b in ipairs(self.buttons) do
        local target = clean[i]
        local mob = target and target.mob
        if b.mob ~= mob then b:SetAttribute("macrotext", self:Macro(mob, b.marker)) end
        b.mob, b.progress = mob, target and target.text
        b:SetShown(mob ~= nil)
    end
    self.current = clean[1] and clean[1].mob
    local visible=math.min(#clean,#self.buttons)
    local width=math.max(72,20+math.min(visible,4)*36-4)
    self.frame:SetSize(width,44+math.max(32,math.ceil(visible/4)*36-4))
    for i=1,visible do
        local row=math.floor((i-1)/4)
        local count=math.min(4,visible-row*4)
        local left=(width-(count*36-4))/2
        local b=self.buttons[i]
        b:ClearAllPoints(); b:SetPoint("TOPLEFT",left+((i-1)%4)*36,-34-row*36)
    end
    self.frame:SetShown(visible > 0)
    self:UpdateSelection()
end
function S:UpdateSelection()
    if self.toolTargetGUID and F.Call(UnitGUID,"target")~=self.toolTargetGUID then self.toolTargetGUID=nil end
end
