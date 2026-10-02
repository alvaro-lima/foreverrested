local _, F = ...
local T = {offset = 0}
F.Tracker = T
T.statusIcons = {Done = "Done", Current = "Current", Next = "Next", ["Not started"] = "NotStarted",
    ["In progress"] = "InProgress", Skipped = "Skipped", Failed = "Failed"}
T.statusSymbols = {Current = ">", Next = "▶", ["Not started"] = "",
    ["In progress"] = "", Skipped = "▶▶", Failed = "!"}
T.statusColors = {Current={.08,.38,.8},Next={.52,.12,.75},
    ["Not started"]={.35,.35,.33},Done={.08,.6,.22},
    ["In progress"]={.85,.54,.04},Skipped={.85,.3,.06},Failed={.75,.07,.08}}
function T:ScrollTo(offset)
    self.topOffset = nil
    self.offset = math.max(0, math.min(self.maxOffset or 0, math.floor(offset + .5)))
    self:Refresh()
end
function T:ShowCurrentAtTop()
    self.topOffset = math.max(0, F.db.step - 1)
    self.offset = self.topOffset
    self:Refresh()
end
function T:Create(parent)
    self.frame = CreateFrame("Frame", nil, parent)
    self.frame:SetSize(376,328)
    self.frame:SetPoint("TOPLEFT", 12, -350)
    self.visibleRows = 6
    self.frame:EnableMouseWheel(true)
    self.frame:SetScript("OnMouseWheel", function(_, delta)
        self:ScrollTo(self.offset - delta)
    end)
    local scrollbar = CreateFrame("Slider", "ForeverRestedGuideScrollBar", self.frame, "UIPanelScrollBarTemplate")
    self.scrollbar = scrollbar
    scrollbar:SetWidth(16)
    scrollbar:SetScript("OnValueChanged", function(_, value)
        if not self.syncingScroll then self:ScrollTo(value) end
    end)
    -- Replace the template's ScrollFrame handler before any value changes.
    self.syncingScroll = true
    scrollbar:SetMinMaxValues(0, 0); scrollbar:SetValueStep(1); scrollbar:SetValue(0)
    self.syncingScroll = false
    scrollbar:EnableMouseWheel(true)
    scrollbar:SetScript("OnMouseWheel", function(_, delta) self:ScrollTo(self.offset - delta) end)
    self.scrollUp = scrollbar.ScrollUpButton or _G[scrollbar:GetName() .. "ScrollUpButton"]
    self.scrollDown = scrollbar.ScrollDownButton or _G[scrollbar:GetName() .. "ScrollDownButton"]
    if self.scrollUp then self.scrollUp:SetScript("OnClick", function() self:ScrollTo(self.offset - 1) end) end
    if self.scrollDown then self.scrollDown:SetScript("OnClick", function() self:ScrollTo(self.offset + 1) end) end
    local track = scrollbar:CreateTexture(nil, "BACKGROUND")
    track:SetAllPoints(); track:SetColorTexture(0, 0, 0, .4)
    scrollbar:Hide()
    self.rows = {}
    self.headers = {}
    for _, name in ipairs({"Step", "Quest", "Status"}) do
        self.headers[name] = F.UI:Text(self.frame, "GameFontNormalSmall", "TOPLEFT", 18, -5, 80)
        self.headers[name]:SetText(name)
    end
    self.statusHeadingHover = CreateFrame("Frame", nil, self.frame)
    self.statusHeadingHover:SetAllPoints(self.headers.Status)
    self.statusHeadingHover:EnableMouse(true)
    F.Tooltips:Attach(self.statusHeadingHover, function(owner)
        if not GameTooltip then return end
        local counts = self.progressCounts or {done=0, skipped=0, remaining=0}
        GameTooltip:SetOwner(owner, "ANCHOR_RIGHT")
        GameTooltip:SetText("Guide progress", 1, .82, 0)
        GameTooltip:AddLine(counts.done .. " done", 1, 1, 1)
        GameTooltip:AddLine(counts.skipped .. " skipped", 1, 1, 1)
        GameTooltip:AddLine(counts.remaining .. " remaining", 1, 1, 1)
        GameTooltip:Show()
    end, true)
    -- Reuse a small row pool; the current step expands to show live objectives.
    for i = 1, 26 do
        local row = CreateFrame("Button", nil, self.frame)
        row:SetPoint("TOPLEFT", 8, -8 - (i - 1) * 52); row:SetSize(356, 51)
        row.background = row:CreateTexture(nil, "BACKGROUND")
        row.background:SetAllPoints()
        row.stepBadge = row:CreateTexture(nil, "ARTWORK")
        row.stepBadge:SetTexture("Interface\\AddOns\\ForeverRested\\Media\\StepBadge.tga")
        row.stepGlow = row:CreateTexture(nil, "ARTWORK", nil, -1)
        row.stepGlow:SetTexture("Interface\\AddOns\\ForeverRested\\Media\\StepGlow.tga")
        row.stepGlow:SetPoint("CENTER", row.stepBadge, "CENTER")
        row.stepGlow:SetBlendMode("ADD")
        row.text = F.UI:Text(row, "GameFontNormalSmall", "TOPLEFT", 10, -10, 130)
        row.text:ClearAllPoints(); row.text:SetPoint("CENTER", row.stepBadge, "CENTER", 0, 0)
        row.text:SetJustifyH("CENTER"); row.text:SetJustifyV("MIDDLE")
        row.body = F.UI:Text(row, "GameFontNormalSmall", "TOPLEFT", 150, -10, 198)
        row.statusButton = CreateFrame("Button", nil, row)
        row.status = row.statusButton:CreateTexture(nil, "ARTWORK")
        row.status:SetPoint("CENTER")
        row.statusFill=row.statusButton:CreateTexture(nil,"OVERLAY",nil,-1)
        row.statusFill:SetAllPoints(row.status)
        row.statusFill:SetTexture("Interface\\AddOns\\ForeverRested\\Media\\StatusColorFill.tga")
        row.statusArt=row.statusButton:CreateTexture(nil,"OVERLAY")
        row.statusArt:SetAllPoints(row.status)
        row.statusSymbol = F.UI:Text(row.statusButton, "GameFontHighlightSmall", "CENTER", 0, 0, 24)
        row.statusSymbol:ClearAllPoints(); row.statusSymbol:SetPoint("CENTER", row.status, "CENTER")
        row.statusSymbol:SetJustifyH("CENTER"); row.statusSymbol:SetJustifyV("MIDDLE")
        row.statusSymbol:SetTextColor(1, 1, .9)
        row.statusSymbol:SetShadowColor(0, 0, 0, 1); row.statusSymbol:SetShadowOffset(1, -1)
        row.statusButton:SetScript("OnClick", function() if row.stepIndex then F.GuideEngine:SelectStep(row.stepIndex) end end)
        F.Tooltips:Attach(row.statusButton, function(owner)
            if not GameTooltip or not row.statusLabel then return end
            GameTooltip:SetOwner(owner, "ANCHOR_RIGHT")
            GameTooltip:SetText(row.statusLabel, 1, .82, 0)
            local meanings = {Done = "This step is complete.", Current = "This is the step you are viewing.", Next = "This is the next relevant step.", Skipped = "You skipped this step.", ["Not started"] = "This step is waiting to begin.", Failed = "This step's quest has failed.", ["In progress"] = "This step's objectives are underway, or ready to turn in."}
            GameTooltip:AddLine(meanings[row.statusLabel], 1, 1, 1, true)
            GameTooltip:Show()
        end, true)
        row:SetScript("OnClick", function(r)
            if r.stepIndex then
                F.GuideEngine:SelectStep(r.stepIndex); return
            end
            if r.zone then self.collapsed[r.zone] = not self.collapsed[r.zone]; self:Refresh() end
        end)
        F.Tooltips:Attach(row, function(r)
            if not GameTooltip then return end
            if r.zone then
                GameTooltip:SetOwner(r, "ANCHOR_RIGHT"); GameTooltip:SetText(r.zone, 1, .82, 0)
                GameTooltip:AddLine("Click to collapse or expand this zone's quests.", 1, 1, 1, true)
                GameTooltip:Show(); return
            end
            if r.stepIndex then
                local step = F.Guide.steps[r.stepIndex]
                GameTooltip:SetOwner(r, "ANCHOR_RIGHT"); GameTooltip:SetText("Step " .. r.stepIndex, 1, .82, 0)
                GameTooltip:AddLine(step.text, 1, 1, 1, true)
                local reason=step.criticalReason or F.GuideEngine.catchUpReasons and F.GuideEngine.catchUpReasons[r.stepIndex]
                if reason or step.critical then
                    GameTooltip:AddLine("Critical: "..(reason or "Required quest"),1,.65,.1,true)
                    GameTooltip:AddLine("Catch-up keeps this step. Use Skip to bypass it manually.",1,1,1,true)
                end
                if step.note then GameTooltip:AddLine(step.note,1,1,.5,true) end
                if step.classAdvice then GameTooltip:AddLine(F.GuideDraft:Advice(),1,1,.5,true) end
                if step.type ~= "note" then
                    for _, task in ipairs(F.GuideEngine:Tasks(step)) do
                        GameTooltip:AddLine(F.UI:TaskText(task), 1, 1, 1, true)
                    end
                end
                local alongside = false
                for _, task in ipairs(step.alongside or {}) do
                    if F.GuideEngine:Applies(task) and F.GuideEngine:TaskState(task) ~= "complete" then
                        if not alongside then
                            GameTooltip:AddLine(" ")
                            GameTooltip:AddLine("Alongside this step", 1, .82, 0)
                            alongside = true
                        end
                        GameTooltip:AddLine(F.UI:TaskText(task), 1, 1, 1, true)
                        local body = F.UI:ActionBody(task)
                        if body ~= "" then GameTooltip:AddLine(body, 1, 1, 1, true) end
                    end
                end
                GameTooltip:Show(); return
            end
            if not r.quest then
                GameTooltip:SetOwner(r, "ANCHOR_RIGHT"); GameTooltip:SetText("Quest tracker", 1, .82, 0)
                GameTooltip:AddLine(r.helpText or "Scroll to browse your quests.", 1, 1, 1, true)
                GameTooltip:Show(); return
            end
            GameTooltip:SetOwner(r, "ANCHOR_RIGHT"); GameTooltip:SetText(r.quest.title, 1, .82, 0)
            for _, o in ipairs(r.quest.objectives) do
                GameTooltip:AddLine(o.text or F.QuestLog:Progress(o), o.finished and .2 or 1, o.finished and 1 or .82, o.finished and .2 or 0, true)
            end
            GameTooltip:Show()
        end)
        self.rows[i] = row
    end
end
function T:Refresh()
    local entries = {}
    local completed, skipped = 0, 0
    local iconSize = math.floor(F.UI:RowIconSize() * .7 + .5)
    local nextIndex=F.GuideEngine:NextRelevantIndex()
    local viewedStep = F.GuideEngine.selectedStep or F.db.step
    for index, step in ipairs(F.Guide.steps) do
        local state = F.GuideEngine:StepState(index)
        local done = state == "complete"
        if done then completed = completed + 1 end
        if state == "skipped" then skipped = skipped + 1 end
        local color = index == viewedStep and "|cffffec80" or "|cffbfb59a"
        local label=done and "Done" or state=="skipped" and "Skipped" or state=="failed" and "Failed" or index==F.db.step and "Current" or index==nextIndex and "Next" or (state=="ongoing" or state=="ready") and "In progress" or "Not started"
        local heading = color..index.."|r"
        local text = F.UI:ActionTitle(step,iconSize)
        local reason=step.criticalReason or F.GuideEngine.catchUpReasons and F.GuideEngine.catchUpReasons[index]
        local critical=reason or step.critical
        for _,task in ipairs(F.GuideEngine:Tasks(step)) do
            if F.QuestPolicy:Critical(task) then critical=true end
        end
        if critical then text=F.UI:CriticalIcon(iconSize)..text end
        if index ~= viewedStep then text = color .. text .. "|r" end
        if index==F.db.step or index==viewedStep then
            for _,task in ipairs(F.GuideEngine:Tasks(step)) do
                if step.tasks and #step.tasks>1 then text=text.."\n  "..F.UI:ActionTitle(task,iconSize) end
                local body=F.UI:ActionBody(task)
                if body~="" then text=text.."\n  "..body end
            end
            if step.note then text=text.."\n|cffffff80"..step.note.."|r" end
            if step.classAdvice then text=text.."\n|cffffff80"..F.GuideDraft:Advice().."|r" end
            local alongside=0
            for _,task in ipairs(step.alongside or {}) do
                if F.GuideEngine:Applies(task) and F.GuideEngine:TaskState(task)~="complete" then
                    alongside=alongside+1
                    if alongside == 1 then text=text.."\n\n|cffffd100Alongside this step:|r" end
                    text=text.."\n  "..(F.QuestPolicy:Critical(task) and F.UI:CriticalIcon(iconSize) or "")..F.UI:ActionTitle(task,iconSize)
                    local body=F.UI:ActionBody(task)
                    if body~="" then text=text.."\n    "..body end
                end
            end
        end
        entries[#entries + 1] = {stepIndex = index, heading = heading, text = text, statusLabel = label}
    end
    self.headers.Step:SetText("Step")
    self.progressCounts = {done=completed, skipped=skipped, remaining=#F.Guide.steps-completed-skipped}
    self.headers.Status:SetText("Status " .. (completed + skipped) .. " / " .. #F.Guide.steps)
    -- Assign stripes before slicing, keeping each step's shade stable while scrolling.
    local questRow = 0
    for _, entry in ipairs(entries) do
        if not entry.zone then
            questRow = questRow + 1
            entry.alternate = questRow % 2 == 0
        end
    end
    local used,available=(F.db.fontSize or 12)+18,math.max(100,(self.frame:GetHeight() or 328)-8)
    -- Measure the full list so the final scroll position fills the last page.
    local probe = self.rows[1].body
    for _, entry in ipairs(entries) do
        probe:SetHeight(0); probe:SetText(entry.text)
        local measured = F.Call(probe.GetStringHeight, probe)
        local _, lines = entry.text:gsub("\n", "")
        entry.height = math.min(math.max(self.rowHeight or 52,
            F.Number(measured) and measured + 20 or (lines + 1) * ((F.db.fontSize or 12) + 2) + 20), available - used)
    end
    local tailHeight, tailCount, firstLastPage = 0, 0, #entries + 1
    for index = #entries, 1, -1 do
        if tailHeight + entries[index].height > available - used or tailCount >= #self.rows then break end
        tailHeight = tailHeight + entries[index].height
        tailCount = tailCount + 1; firstLastPage = index
    end
    self.maxOffset = math.max(0, firstLastPage - 1)
    -- Auto may place a late step at the top even when fewer rows follow it.
    if self.topOffset then
        self.maxOffset = math.max(self.maxOffset, math.min(self.topOffset, math.max(0, #entries - 1)))
    end
    self.offset = math.max(0, math.min(self.offset, self.maxOffset))
    self.visibleRows=0
    for i, row in ipairs(self.rows) do
        local entry = entries[self.offset + i]
        row.text:SetText(entry and entry.heading or "")
        row.body:SetText(entry and entry.text or "")
        row.status:SetTexture(entry and "Interface\\AddOns\\ForeverRested\\Media\\StepBadge.tga" or nil)
        local tint=entry and self.statusColors[entry.statusLabel]
        row.statusFill:SetShown(tint~=nil)
        if tint then row.statusFill:SetVertexColor(tint[1],tint[2],tint[3],1) end
        row.statusArt:SetTexture(entry and ("Interface\\AddOns\\ForeverRested\\Media\\StatusGlyph"..self.statusIcons[entry.statusLabel]..".tga") or nil)
        row.statusLabel = entry and entry.statusLabel
        row.statusSymbol:SetText("")
        local height = entry and entry.height or 0
        if not entry or used+height>available then entry=nil;used=available end
        row:SetShown(entry~=nil)
        if entry then
            row:ClearAllPoints();row:SetPoint("TOPLEFT",8,-used)
            row:SetHeight(height-3);row.body:SetHeight(height-20)
            used=used+height;self.visibleRows=self.visibleRows+1
        end
        row.zone, row.quest = entry and entry.zone, entry and entry.quest
        row.stepIndex = entry and entry.stepIndex
        row.helpText = entry and entry.text
        local selected = entry~=nil and entry.stepIndex==viewedStep
        row.stepGlow:SetShown(selected)
        row.text:SetShadowColor(selected and 1 or 0, selected and .68 or 0, 0, selected and .85 or 1)
        row.text:SetShadowOffset(selected and 0 or 1, selected and 0 or -1)
        row.background:SetShown(entry~=nil)
        if selected then
            row.background:SetColorTexture(.65, .46, .12, .28)
        elseif entry and entry.alternate then
            row.background:SetColorTexture(.48, .40, .27, .22)
        else
            row.background:SetColorTexture(.02, .02, .02, .32)
        end
    end
    self.syncingScroll = true
    self.scrollbar:SetMinMaxValues(0, self.maxOffset)
    self.scrollbar:SetValue(self.offset)
    self.scrollbar:SetShown(self.maxOffset > 0)
    if self.scrollUp then self.scrollUp:SetEnabled(self.offset > 0) end
    if self.scrollDown then self.scrollDown:SetEnabled(self.offset < self.maxOffset) end
    self.syncingScroll = false
end
