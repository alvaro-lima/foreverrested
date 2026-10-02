local _, F = ...
F.Arrow = {}
local fullTurn = 2 * math.pi
local lineEnds = {{0, -16, 0, 17}, {0, 17, -9, 6}, {0, 17, 9, 6}}
local function wrap(angle)
    return (angle + math.pi) % fullTurn - math.pi
end
function F.Arrow:Create()
    local f = CreateFrame("Frame", nil, UIParent)
    f:SetSize(80, 76); f:SetPoint("CENTER", UIParent, "CENTER", 0, 180)
    local p = F.db.arrowPosition
    if type(p) == "table" and F.Number(p.x) and F.Number(p.y) then
        f:ClearAllPoints(); f:SetPoint("CENTER", UIParent, "CENTER", p.x, p.y)
    end
    f:SetMovable(not F.db.positionsLocked); f:SetClampedToScreen(true); f:EnableMouse(true)
    F.Tooltips:Text(f, "Navigation arrow", "Points toward the current destination. The number below shows distance in yards. Drag with the left mouse button to move the arrow.")
    f:RegisterForDrag("LeftButton")
    f:SetScript("OnDragStart", function() if not F.db.positionsLocked then f:StartMoving() end end)
    f:SetScript("OnDragStop", function()
        f:StopMovingOrSizing()
        local x, y = f:GetCenter(); local ux, uy = UIParent:GetCenter()
        if F.Number(x) and F.Number(y) and F.Number(ux) and F.Number(uy) then
            F.db.arrowPosition = {x = x - ux, y = y - uy}
            f:ClearAllPoints(); f:SetPoint("CENTER", UIParent, "CENTER", x - ux, y - uy)
        end
    end)
    local compass = CreateFrame("Frame", nil, f)
    self.compass = compass
    compass:SetSize(48, 48); compass:SetPoint("TOP", 0, 0)
    self.yards = F.UI:Text(f, "GameFontNormal", "TOP", 0, -52, 80)
    self.yards:SetJustifyH("CENTER")
    local icon = compass:CreateTexture(nil, "ARTWORK")
    icon:SetAllPoints()
    local custom = "Interface\\AddOns\\" .. F.name .. "\\Media\\BronzeArrow.tga"
    local loaded = F.Call(icon.SetTexture, icon, custom) == true
    if loaded then self.artSource = custom end
    -- Prefer the client's native player-arrow atlas, including its beveled art.
    -- Confirm atlas availability before selecting it; never assume Retail assets.
    for _, atlas in ipairs({"UI-HUD-Minimap-Arrow-Player", "UI-WorldMapArrow"}) do
        if loaded then break end
        if F.Call(C_Texture and C_Texture.GetAtlasInfo, atlas) and icon.SetAtlas then
            loaded = pcall(icon.SetAtlas, icon, atlas, false)
            if loaded then self.artSource = atlas; break end
        end
    end
    if not loaded then
        -- This Blizzard texture is referenced in the installed RXPGuides
        -- functions.lua:232. No RestedXP artwork or code is bundled here.
        local native = "Interface\\MINIMAP\\MinimapArrow"
        loaded = F.Call(icon.SetTexture, icon, native) == true
        if loaded then self.artSource = native end
    end
    if loaded then
        self.texture = icon
    elseif compass.CreateLine then
        icon:Hide()
        self.lines = {}
        for i = 1, 3 do
            local line = compass:CreateLine(nil, "ARTWORK")
            line:SetThickness(3); line:SetColorTexture(1, .82, 0, 1)
            self.lines[i] = line
        end
    end
    self.frame = f
    self:SetSize(F.db.arrowSize or 48)
    -- Only facing/rotation runs per rendered frame. Quest/map work stays at 5 Hz.
    f:SetScript("OnUpdate", function(_, elapsed) self:Animate(elapsed) end)
end
function F.Arrow:SetSize(size)
    size = F.Number(size) and math.max(24, math.min(96, math.floor(size))) or 48
    F.db.arrowSize = size
    if not self.frame then return end
    self.compass:SetSize(size, size)
    self.frame:SetSize(math.max(80, size + 16), size + 28)
    self.yards:ClearAllPoints(); self.yards:SetPoint("TOP", 0, -size - 4)
    self.yards:SetWidth(math.max(80, size + 16))
    if self.lines then
        for _, line in ipairs(self.lines) do line:SetThickness(3 * size / 48) end
        self:Draw(self.displayAngle or 0)
    end
end
function F.Arrow:Update()
    local n, f = F.Navigation, self.frame
    if not f then return end
    local angle,distance=n.followAngle or n.angle,n.followDistance or n.distance
    if angle == nil or not F.Number(distance) or (not self.texture and not self.lines) then
        self.displayAngle, self.lastYards = nil, nil
        f:Hide(); return
    end
    if self.targetMap ~= n.targetMap or self.tx ~= n.tx or self.ty ~= n.ty or self.followGUID~=n.followGUID then
        self.displayAngle = nil
        self.targetMap, self.tx, self.ty = n.targetMap, n.tx, n.ty
        self.followGUID=n.followGUID
    end
    if self.displayAngle == nil then self.displayAngle = wrap(angle); self:Draw(self.displayAngle) end
    f:Show()
    local yards = math.floor(distance + .5)
    if yards ~= self.lastYards then
        self.yards:SetText(string.format("%d yd", yards)); self.lastYards = yards
    end
end
function F.Arrow:Animate(elapsed)
    local n = F.Navigation
    local bearing,distance=n.followBearing or n.bearing,n.followDistance or n.distance
    if not F.Number(bearing) or not F.Number(distance) then
        self.displayAngle = nil; self.frame:Hide(); return
    end
    local facing = F.Call(GetPlayerFacing)
    if not F.Number(facing) then
        n.angle, n.reason = nil, "Player facing unavailable"
        self.displayAngle = nil; self.frame:Hide(); return
    end
    n.angle, n.reason = wrap(bearing - facing), nil
    if F.StepPins then F.StepPins:RotateMini(facing) end
    local previous = self.displayAngle
    -- Shortest-arc, frame-rate-independent smoothing avoids a full spin at north.
    local weight = 1 - math.exp(-math.max(0, elapsed or 0) / .04)
    self.displayAngle = previous and wrap(previous + wrap(n.angle - previous) * weight) or n.angle
    if previous == nil or math.abs(wrap(self.displayAngle - previous)) > .00001 then
        self:Draw(self.displayAngle)
    end
end
function F.Arrow:Draw(angle)
    if self.texture and self.texture.SetRotation then self.texture:SetRotation(angle) end
    if self.lines then
        local cosine, sine = math.cos(angle), math.sin(angle)
        local scale = (F.db.arrowSize or 48) / 48
        local function point(x, y)
            return (x * cosine - y * sine) * scale, (x * sine + y * cosine) * scale
        end
        for i, p in ipairs(lineEnds) do
            local ax, ay = point(p[1], p[2]); local bx, by = point(p[3], p[4])
            self.lines[i]:SetStartPoint("CENTER", ax, ay); self.lines[i]:SetEndPoint("CENTER", bx, by)
        end
    end
end
