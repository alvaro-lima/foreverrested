local _, F = ...
local T = {delay = 3, owners = {}}
F.Tooltips = T
T.driver = CreateFrame("Frame")
T.driver:Hide()
function T:Cancel(owner)
    if self.pending and (not owner or self.pending.owner == owner) then
        self.pending = nil; self.driver:Hide()
    end
    if self.shownOwner and (not owner or self.shownOwner == owner) then
        if GameTooltip then GameTooltip:Hide() end
        self.shownOwner = nil
    end
end
function T:Attach(frame, render, immediate)
    frame.foreverTooltip = true
    self.owners[#self.owners + 1] = frame
    frame:SetScript("OnEnter", function(owner)
        self:Cancel()
        if immediate then
            self.shownOwner = owner
            render(owner)
            return
        end
        self.pending = {owner = owner, render = render, elapsed = 0}
        self.driver:Show()
    end)
    frame:SetScript("OnLeave", function(owner) self:Cancel(owner) end)
    if frame.HookScript then frame:HookScript("OnHide", function(owner) self:Cancel(owner) end) end
end
function T:Text(frame, title, body, immediate)
    -- Keep immediate behavior when a button's help text is replaced later.
    if immediate ~= nil then frame.foreverTooltipImmediate = immediate end
    self:Attach(frame, function(owner)
        if not GameTooltip then return end
        GameTooltip:SetOwner(owner, "ANCHOR_RIGHT"); GameTooltip:SetText(title, 1, .82, 0)
        if body then GameTooltip:AddLine(body, 1, 1, 1, true) end
        GameTooltip:Show()
    end, frame.foreverTooltipImmediate == true)
end
function T:Tick(dt)
    local pending = self.pending
    if not pending then self.driver:Hide(); return end
    if not pending.owner:IsShown() then self:Cancel(pending.owner); return end
    pending.elapsed = pending.elapsed + dt
    if pending.elapsed < self.delay then return end
    self.pending = nil; self.driver:Hide()
    if not GameTooltip then return end
    self.shownOwner = pending.owner
    pending.render(pending.owner)
end
T.driver:SetScript("OnUpdate", function(_, dt) T:Tick(dt) end)
