local _, F = ...
local T = {offset = 0}
F.Tracker = T
function T:SetSearch(text)
    local query = (text or ""):lower():match("^%s*(.-)%s*$")
    query = query ~= "" and query or nil
    if query == self.searchQuery then return end
    if not self.searchQuery then self.beforeSearchOffset = self.offset end
    self.searchQuery = query
    self.topOffset = nil
    self.offset = query and 0 or (self.beforeSearchOffset or 0)
    self:Refresh()
end
function T:MatchesSearch(step, index, state, statusLabel)
    if not self.searchQuery then return true end
    -- Match exact quest IDs as well as the original step number.
    if self.searchQuery:match("^%d+$") then
        local number = tonumber(self.searchQuery)
        if index == number or F.GuideEngine:Resolve(step) == number then return true end
        for _, task in ipairs(step.tasks or {}) do
            if F.GuideEngine:Resolve(task) == number then return true end
        end
        for _, task in ipairs(step.alongside or {}) do
            if F.GuideEngine:Resolve(task) == number then return true end
        end
        return false
    end
    local parts = {tostring(index)}
    local function add(value)
        if type(value) == "string" then parts[#parts + 1] = value end
    end
    state = state or F.GuideEngine:StepState(index)
    add(statusLabel)
    local statusTerms = {
        complete = "done complete completed finished",
        skipped = "skipped skip",
        failed = "failed failure",
        ongoing = "in progress ongoing active",
        ready = "in progress ready ready to turn in",
        waiting = "not started waiting",
        notready = "in progress objectives pending",
    }
    add(statusTerms[state])
    if state ~= "complete" and state ~= "skipped" then add("to do todo remaining unfinished pending") end
    if index == F.db.step then add("current") end
    if step.optional then add("optional") end
    local priorityTerms = {
        Critical = "key critical key/critical required",
        Gear = "gear equipment reward",
        Money = "money gold reward",
        Optional = "optional",
    }
    for _, marker in ipairs(F.UI:StepMarkers(step, index)) do add(priorityTerms[marker.kind]) end
    local function taskText(task)
        if task.questID or task.slot then add("quest quests") end
        if task.optional then add("optional") end
        add(task.text); add(task.note); add(task.npc); add(task.mob)
        add(F.UI:ActionContact(task)); add(F.UI:ActionTitle(task)); add(F.UI:ActionBody(task))
        local id, quest = F.GuideEngine:Resolve(task)
        if id then add(tostring(id)) end
        local data = F.GuideEngine:Metadata(id)
        add(quest and quest.title); add(data and data.title)
        for _, point in ipairs(data and data.locations or {}) do add(point.name) end
    end
    taskText(step)
    for _, task in ipairs(step.tasks or {}) do taskText(task) end
    for _, task in ipairs(step.alongside or {}) do taskText(task) end
    if step.classAdvice then add(F.GuideDraft:Advice()) end
    local haystack = table.concat(parts, " "):gsub("|c%x%x%x%x%x%x%x%x", ""):gsub("|r", ""):gsub("|H.-|h", ""):gsub("|h", ""):gsub("|T.-|t", ""):lower()
    for word in self.searchQuery:gmatch("%S+") do
        if not haystack:find(word, 1, true) then return false end
    end
    return true
end
T.statusIcons = {Done = "Done", Current = "Current", Next = "Next", ["Not started"] = "NotStarted",
    ["In progress"] = "InProgress", Skipped = "Skipped", Failed = "Failed"}
T.statusSymbols = {Current = ">", Next = "▶", ["Not started"] = "",
    ["In progress"] = "", Skipped = "▶▶", Failed = "!"}
T.statusColors = {Current={.08,.38,.8},Next={.52,.12,.75},
    ["Not started"]={.35,.35,.33},Done={.08,.6,.22},
    ["In progress"]={.85,.54,.04},Skipped={.85,.3,.06},Failed={.75,.07,.08}}
function T:ScrollTo(offset)
    local target = math.max(0, math.min(self.maxOffset or 0, math.floor(offset + .5)))
    if target == self.offset and not self.topOffset then return end
    self.topOffset = nil
    self.offset = target
    self:Render()
end
function T:ShowCurrentAtTop()
    if self.searchQuery and F.UI.searchBox then F.UI.searchBox:SetText("") end
    self:SetSearch("")
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
    if self.scrollUp then
        self.scrollUp:SetScript("OnClick", function() self:ScrollTo(self.offset - 1) end)
        F.Tooltips:Text(self.scrollUp, "Scroll up", "Show earlier guide steps.")
    end
    if self.scrollDown then
        self.scrollDown:SetScript("OnClick", function() self:ScrollTo(self.offset + 1) end)
        F.Tooltips:Text(self.scrollDown, "Scroll down", "Show later guide steps.")
    end
    F.Tooltips:Text(scrollbar, "Scroll guide", "Drag to browse guide steps, or use the mouse wheel.")
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
        GameTooltip:AddLine(counts.skipped .. " skipped", 1, 1, 1)
        GameTooltip:AddLine(counts.remaining .. " remaining", 1, 1, 1)
        GameTooltip:AddLine(counts.done .. " done", 1, 1, 1)
        local critical = self.criticalCounts or {done=0, skipped=0, remaining=0, total=0}
        GameTooltip:AddLine(" ")
        GameTooltip:AddLine("Critical quests: " .. critical.total, 1, .82, 0)
        GameTooltip:AddLine(critical.skipped .. " skipped", 1, 1, 1)
        GameTooltip:AddLine(critical.remaining .. " remaining", 1, 1, 1)
        GameTooltip:AddLine(critical.done .. " done", 1, 1, 1)
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
        row:SetHyperlinksEnabled(true)
        row:SetScript("OnHyperlinkEnter", function(owner, link)
            local kind = link and link:match("^foreverrestedicon:(%a+)$")
            local meanings = {
                Critical={"Key / Critical", "Required for guide progression or a quest chain. Catch-up keeps this step; Skip can bypass it manually."},
                Gear={"Equipment reward", "This quest offers uncommon or better equipment. Check its level, class requirements and stats before choosing a reward."},
                Money={"Money reward", "This quest offers a money reward."},
                Optional={"Optional", "You can skip this step. Travel advice can be followed using any route you prefer."},
                OptionalTurnin={"Optional turn-in", "Turn in this quest if you choose to do it. You can skip this step."},
                OptionalObjective={"Optional objectives", "Complete this quest if you choose to do it. You can skip this step."},
                OptionalTravel={"Optional travel", "Use any route you prefer. Arriving near the next quest action skips this travel advice."},
                Objective={"Quest objectives", "Complete the gathering, combat or other objectives for this quest."},
                Catchup={"Catch-up quest", "An unfinished essential quest or prerequisite. Complete this before continuing the regional route."},
                pickup={"Accept quest", "Accept this quest from its quest giver."},
                turnin={"Turn in quest", "Return to the quest giver to turn in this quest after completing its objectives."},
                talk={"Talk", "Speak to this NPC."},
                trainer={"Trainer", "Visit this trainer to learn available skills."},
            }
            local help = meanings[kind]
            if not help or not GameTooltip then return end
            F.Tooltips:Cancel()
            F.Tooltips.shownOwner = owner
            GameTooltip:SetOwner(owner, "ANCHOR_RIGHT")
            GameTooltip:SetText(help[1], 236/255, 187/255, 49/255)
            GameTooltip:AddLine(help[2], 1, 1, 1, true)
            GameTooltip:Show()
        end)
        row:SetScript("OnHyperlinkLeave", function(owner) F.Tooltips:Cancel(owner) end)
        row:SetScript("OnHyperlinkClick", function(owner)
            if owner.stepIndex then F.GuideEngine:SelectStep(owner.stepIndex) end
        end)
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
                local step=F.Guide.steps[r.stepIndex]
                self.expandedStepID=self.expandedStepID~=step.id and step.id or nil
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
                local action = step.tasks and #step.tasks == 1 and step.tasks[1] or step
                local id,quest=F.GuideEngine:Resolve(action)
                local metadata=id and F.GuideEngine:Metadata(id)
                GameTooltip:SetOwner(r,"ANCHOR_RIGHT")
                GameTooltip:ClearLines()
                GameTooltip:SetText(quest and quest.title or metadata and metadata.title or step.text or "Guide step",1,.82,0)
                local function labelStyle()
                    local count=F.Call(GameTooltip.NumLines,GameTooltip)
                    local name=F.Call(GameTooltip.GetName,GameTooltip)
                    local left=name and count and _G[name.."TextLeft"..count]
                    if left then
                        local font,size=left:GetFont()
                        if font then left:SetFont(font,size,"OUTLINE") end
                    end
                end
                local function field(key,value)
                    GameTooltip:AddDoubleLine(key..":",tostring(value or "Not specified"),1,.82,0,1,1,1)
                    labelStyle()
                end
                field("Step",r.stepIndex)
                field("Location",F.UI:StepLocation(step):gsub("^Location: ",""))
                field("Status",r.statusLabel or F.GuideEngine:StepState(r.stepIndex))
                if step.recovery then
                    local reason=step.criticalReason or F.GuideEngine.catchUpReasons and F.GuideEngine.catchUpReasons[r.stepIndex]
                    GameTooltip:AddLine("Catch-up:",1,.82,0);labelStyle()
                    GameTooltip:AddLine(reason or "Unfinished quest needed for this route.",1,1,1,true)
                end
                if self.expandedStepID==step.id then
                GameTooltip:AddLine("Description:",1,.82,0);labelStyle()
                local description=F.Travel:Note(step) or step.text or metadata and metadata.title or ""
                GameTooltip:AddLine(description,1,1,1,true)
                end
                F.Tooltips:QuestHint('Click to view this step and its details. Use From to restart here.')
                GameTooltip:Show(); return
            end
            if not r.quest then
                GameTooltip:SetOwner(r, "ANCHOR_RIGHT"); GameTooltip:SetText("Quest tracker", 1, .82, 0)
                GameTooltip:AddLine(r.helpText or "Scroll to browse your quests.", 1, 1, 1, true)
                GameTooltip:Show(); return
            end
            F.Tooltips:QuestHeader(r,r.quest.title)
            for _, o in ipairs(r.quest.objectives) do
                F.Tooltips:QuestObjective(o.text or F.QuestLog:Progress(o),o.finished)
            end
            GameTooltip:Show()
        end, true)
        self.rows[i] = row
    end
end
function T:Refresh()
    local entries = {}
    local criticalQuests = {}
    local completed, skipped = 0, 0
    local iconSize = math.floor(F.UI:RowIconSize() * .7 + .5)
    local nextIndex=F.GuideEngine:NextRelevantIndex()
    local viewedStep = F.GuideEngine.selectedStep or F.db.step
    for index, step in ipairs(F.Guide.steps) do
        local state = F.GuideEngine:StepState(index)
        local done = state == "complete"
        if done then completed = completed + 1 end
        if state == "skipped" then skipped = skipped + 1 end
        -- Count unique quests, rather than their accept/objective/turn-in rows.
        for _, task in ipairs(step.tasks or {step}) do
            local id = F.GuideEngine:Resolve(task)
            local record = id and F.QuestPolicy:Record(id) or {}
            if id and (task.critical or step.criticalReason or record.critical
                or F.QuestPolicy.requiredQuests and F.QuestPolicy.requiredQuests[id])
                and F.QuestPolicy:Eligible(id, task) then
                local quest = criticalQuests[id] or {allSkipped=true}
                if state ~= "skipped" then quest.allSkipped = false end
                if task.type == "turnin" and state == "skipped" then quest.turninSkipped = true end
                criticalQuests[id] = quest
            end
        end
        local color = index == viewedStep and "|cffffec80" or "|cffbfb59a"
        local label=done and "Done" or state=="skipped" and "Skipped" or state=="failed" and "Failed" or index==F.db.step and "Current" or index==nextIndex and "Next" or state=="ongoing" and "In progress" or "Not started"
        local heading = color..index.."|r"
        local text = F.UI:ActionTitle(step,iconSize)
        local markers=''
        for _,marker in ipairs(F.UI:StepMarkers(step,index)) do
            if marker.kind~='Optional' then markers=markers..F.UI:PriorityIcon(marker.kind,iconSize) end
        end
        if markers~='' then text=text..' '..markers end
        if index ~= viewedStep then text = color .. text .. "|r" end
        if index==F.db.step or index==viewedStep then
            local primary=step.tasks and #step.tasks==1 and step.tasks[1] or step
            local contact=F.UI:ActionContact(primary)
            if contact~='' then text=contact..'\n  '..text end
            for _,task in ipairs(F.GuideEngine:Tasks(step)) do
                if step.tasks and #step.tasks>1 then
                    local contact=F.UI:ActionContact(task)
                    if contact~='' then text=text..'\n  '..contact end
                    text=text.."\n  "..F.UI:ActionTitle(task,iconSize)..F.UI:TaskMarkerIcons(task,iconSize)
                end
                local body=F.UI:ActionBody(task)
                if body~="" then text=text.."\n  "..body:gsub('\n','\n  ') end
            end
            local note=F.Travel:Note(step)
            local action=step.tasks and #step.tasks==1 and step.tasks[1] or step
            local questAction=action.type=='pickup' or action.type=='objective' or action.type=='turnin'
            if note and not questAction and self.expandedStepID==step.id then text=text.."\n|cffffff80"..note.."|r" end
            if step.classAdvice then text=text.."\n|cffffff80"..F.GuideDraft:Advice().."|r" end
        end
        if self:MatchesSearch(step, index, state, label) then
            text=F.UI:UniqueText(text)
            entries[#entries + 1] = {stepIndex = index, heading = heading, text = text, statusLabel = label}
        end
    end
    self.headers.Step:SetText("Step")
    self.headers.Quest:SetText(self.searchQuery and
        ("Quests - " .. #entries .. " / " .. #F.Guide.steps .. " matched") or "Quests")
    self.progressCounts = {done=completed, skipped=skipped, remaining=#F.Guide.steps-completed-skipped}
    -- Completed class unlocks no longer need recovery rows, but still belong
    -- in the character's critical progress for this guide.
    local policy, seenUnlocks = F.QuestPolicy, {}
    local function completedChain(id, visited)
        if visited[id] then return end
        visited[id] = true
        local quest = criticalQuests[id] or {}
        quest.unlockCompleted = true
        criticalQuests[id] = quest
        for _, prior in ipairs(policy:Record(id).prerequisites or {}) do completedChain(prior, visited) end
    end
    local function countUnlock(unlock)
        if type(unlock) ~= "table" or not policy:UnlockApplies(unlock) then return end
        for _, id in ipairs(unlock.terminals or {}) do
            if policy:Satisfied(id) then completedChain(id, {}); return end
        end
    end
    for _, unlock in ipairs(policy.unlocks) do
        seenUnlocks[unlock.key] = true
        local override = policy.foreverUnlocks[unlock.key]
        countUnlock(override == nil and unlock or override)
    end
    for key, unlock in pairs(policy.foreverUnlocks) do
        if not seenUnlocks[key] then countUnlock(unlock) end
    end
    local critical = {done=0, skipped=0, remaining=0, total=0}
    for id, quest in pairs(criticalQuests) do
        critical.total = critical.total + 1
        if quest.unlockCompleted or F.QuestPolicy:Satisfied(id) then critical.done = critical.done + 1
        elseif quest.allSkipped or quest.turninSkipped then critical.skipped = critical.skipped + 1
        else critical.remaining = critical.remaining + 1 end
    end
    self.criticalCounts = critical
    self.headers.Status:SetText("Status " .. (completed + skipped) .. " / " .. #F.Guide.steps)
    -- Assign stripes before slicing, keeping each step's shade stable while scrolling.
    local questRow = 0
    for _, entry in ipairs(entries) do
        if not entry.zone then
            questRow = questRow + 1
            entry.alternate = questRow % 2 == 0
        end
    end
    local used,available=self.contentTop or (F.db.fontSize or 12)+18,math.max(100,(self.frame:GetHeight() or 328)-8)
    -- Measure the full list so the final scroll position fills the last page.
    local probe = self.rows[1].body
    for _, entry in ipairs(entries) do
        probe:SetHeight(0); probe:SetText(entry.text)
        local measured = F.Call(probe.GetStringHeight, probe)
        local _, lines = entry.text:gsub("\n", "")
        entry.height = math.min(math.max(self.rowHeight or 52,
            F.Number(measured) and measured + 20 or (lines + 1) * ((F.db.fontSize or 12) + 2) + 20), available - used)
    end
    -- Quest, search and layout refreshes rebuild the list. Scrolling only
    -- repaints the row pool, without rescanning quests or measuring the list.
    self.entries = entries
    self:Render()
end
function T:Render()
    if not self.entries then self:Refresh(); return end
    local entries = self.entries
    local viewedStep = F.GuideEngine.selectedStep or F.db.step
    local used,available=self.contentTop or (F.db.fontSize or 12)+18,math.max(100,(self.frame:GetHeight() or 328)-8)
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
        local face, _, flags = F.Call(row.text.GetFont, row.text)
        local number = entry and entry.stepIndex
        local numberOffset=number and number>=10 and number<=19 and -.5 or 0
        row.text:ClearAllPoints();row.text:SetPoint("CENTER",row.stepBadge,"CENTER",numberOffset,0)
        local size = (F.db.fontSize or 12) * (number and number >= 100 and .85 or 1)
        if face then row.text:SetFont(face, size, flags or "") end
        row.text:SetWordWrap(false)
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
        row.text:SetShadowColor(0,0,0,0)
        row.text:SetShadowOffset(0,0)
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
