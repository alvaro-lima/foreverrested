local addon, F = ...
F.name = addon
F.icon = "Interface\\AddOns\\" .. addon .. "\\Media\\GuideIcon-title-64"
F.minimapIcon = "Interface\\AddOns\\" .. addon .. "\\Media\\GuideIcon-face"
ForeverRested = F
function F.Call(fn, ...)
    if type(fn) ~= "function" then return end
    local function pack(...) return {n = select("#", ...), ...} end
    local values = pack(pcall(fn, ...))
    if not values[1] then return end
    for i = 2, values.n do
        if issecretvalue and issecretvalue(values[i]) then values[i] = nil end
    end
    return unpack(values, 2, values.n)
end
function F.XY(v)
    if not v then return end
    if v.GetXY then return F.Call(v.GetXY, v) end
    return v.x, v.y
end
function F.Number(n)
    return type(n) == "number" and n == n and n > -math.huge and n < math.huge
end
function F.Combat() return F.Call(InCombatLockdown) == true end
function F.Print(text)
    if DEFAULT_CHAT_FRAME then DEFAULT_CHAT_FRAME:AddMessage("|cffffd100Forever Rested:|r " .. text) end
end
-- Templates are tested once when creating frames. Missing optional templates
-- fall back to ordinary frames; secure buttons never fall back to insecure ones.
function F.Frame(kind, name, parent, template)
    local frame = template and F.Call(CreateFrame, kind, name, parent, template)
    if frame then return frame end
    return CreateFrame(kind, name, parent)
end
function F.Refresh()
    if not F.db then return end
    F.QuestLog:Refresh()
    local selectedUnlockView
    if F.GuideEngine.unlockRefreshPending and F.Guide and F.db.guideID then
        F.GuideEngine.unlockRefreshPending = nil
        selectedUnlockView = F.GuideEngine.selectedStep and F.Guide.steps[F.GuideEngine.selectedStep]
        F.GuideLibrary:SaveCurrent()
        F.GuideLibrary:ApplyState(F.Guide, F.db.guides[F.db.guideID])
    end
    F.GuideEngine:CatchUpOnLoad()
    if selectedUnlockView then
        for index, step in ipairs(F.Guide.steps) do
            if step.id == selectedUnlockView.id then F.GuideEngine.selectedStep = index; break end
        end
    end
    F.GuideEngine:AdvanceSafe()
    if F.UI.frame then F.UI:Refresh() end
end
