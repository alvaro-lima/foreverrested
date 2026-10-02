local _, F = ...
local P = {areaWorld = {}, areaMini = {}}
F.StepPins = P
function P:PinsHidden()
    return F.db.hidden or F.db.hideWorldPins
end
P.stateIcons = {ongoing = "InProgress", notready = "InProgress", ready = "InProgress",
    complete = "Done", waiting = "NotStarted", skipped = "Skipped", failed = "Failed"}
function P:CreateMapToggle()
    local map = WorldMapFrame
    if not map then return end
    if self.mapToggle then self:PositionMapToggle();return end
    local parent = map
    local button = CreateFrame("Button",nil,parent)
    self.mapToggle = button
    button:SetSize(31,31)
    self:PositionMapToggle()
    button:SetFrameLevel(parent:GetFrameLevel()+200)
    local border = button:CreateTexture(nil,"OVERLAY")
    border:SetSize(53,53);border:SetPoint("TOPLEFT")
    border:SetTexture("Interface\\Minimap\\MiniMap-TrackingBorder")
    local background = button:CreateTexture(nil,"BACKGROUND")
    background:SetSize(20,20);background:SetPoint("TOPLEFT",7,-5)
    background:SetTexture("Interface\\Minimap\\UI-Minimap-Background")
    local icon = button:CreateTexture(nil,"ARTWORK")
    icon:SetSize(20,20);icon:SetPoint("CENTER",button,"CENTER",1,-1)
    icon:SetTexture(F.minimapIcon);icon:SetTexCoord(0,1,0,1)
    button:SetHighlightTexture("Interface\\Minimap\\UI-Minimap-ZoomButton-Highlight","ADD")
    local function label()
        icon:SetDesaturated(self:PinsHidden() == true)
        icon:SetAlpha(self:PinsHidden() and .5 or 1)
    end
    self.updateToggleAppearance = label
    button:SetScript("OnClick",function()
        F.db.hideWorldPins = not F.db.hideWorldPins
        label();self:Update()
    end)
    F.Tooltips:Attach(button,function(owner)
        GameTooltip:SetOwner(owner,"ANCHOR_LEFT")
        GameTooltip:SetText("Forever Rested map icons",1,.82,0)
        GameTooltip:AddLine(F.db.hideWorldPins and "Click to show map and minimap guide pins." or "Click to hide map and minimap guide pins.",1,1,1,true)
        GameTooltip:Show()
    end,true)
    label()
end
function P:PositionMapToggle()
    local button = self.mapToggle
    if not button then return end
    button:ClearAllPoints()
    if GatherLiteWorldmapButton then
        button:SetPoint("BOTTOMLEFT",GatherLiteWorldmapButton,"TOPLEFT",0,6)
    else
        button:SetPoint("BOTTOMLEFT",WorldMapFrame,"BOTTOMLEFT",20,77)
    end
end
function P:ShouldShow(index,task)
    local state = F.GuideEngine:StepState(index)
    return state ~= "complete" and state ~= "skipped"
        and (not task or F.GuideEngine:TaskState(task) ~= "complete")
end
function P:TaskKey(task)
    if not task then return end
    local id = F.GuideEngine:Resolve(task)
    if id then return id..":"..(task.type or "note")..":"..(task.objective or "all") end
end
function P:DestinationStep()
    local task = F.Navigation.waypointTask
    if task then
        for index, step in ipairs(F.Guide.steps) do
            if step == task then return index, step end
            for _, action in ipairs(step.tasks or {}) do
                if action == task then return index, step end
            end
            for _, action in ipairs(step.alongside or {}) do
                if action == task then return index, step end
            end
        end
    end
    return F.db.step, F.GuideEngine:Current()
end
function P:Create(parent)
    local pin = CreateFrame("Frame", nil, parent)
    pin:SetSize(22,22); pin:SetScale(1); pin:SetFrameStrata("HIGH"); pin:EnableMouse(true)
    local icon = pin:CreateTexture(nil,"ARTWORK")
    icon:SetAllPoints(); icon:SetTexture("Interface\\AddOns\\ForeverRested\\Media\\StepBadge.tga")
    pin.icon = icon
    pin.fill = pin:CreateTexture(nil,"ARTWORK",nil,1)
    pin.fill:SetAllPoints(icon)
    pin.fill:SetTexture("Interface\\AddOns\\ForeverRested\\Media\\StatusColorFill.tga")
    pin.fill:Hide()
    -- Pin labels have their own sizing; the guide's font refresh must not resize them.
    pin.number = pin:CreateFontString(nil,"OVERLAY","GameFontNormal")
    pin.number:SetPoint("CENTER",pin,"CENTER",0,0)
    pin.number:SetSize(22,22)
    pin.number:SetJustifyH("CENTER"); pin.number:SetJustifyV("MIDDLE")
    pin.number:SetSpacing(0)
    pin.number:SetTextColor(1,1,.9); pin.number:SetShadowColor(0,0,0,1); pin.number:SetShadowOffset(1,-1)
    F.Tooltips:Attach(pin,function()
        if not GameTooltip then return end
        local number, step = self:DestinationStep()
        local task = F.Navigation.waypointTask
        if pin.entry then number,step,task = pin.entry.index,F.Guide.steps[pin.entry.index],pin.entry.task end
        GameTooltip:SetOwner(pin,"ANCHOR_RIGHT")
        local tasks = task and {task} or F.GuideEngine:Tasks(step)
        local seen, first = {}, true
        for _, action in ipairs(tasks) do
            local id,q = F.GuideEngine:Resolve(action)
            if not id or not seen[id] then
                if id then seen[id] = true end
                local metadata = F.GuideEngine:Metadata(id)
                local title = q and q.title or metadata and metadata.title or action.text or step.text or "Guide step"
                local level = q and q.level
                local tint = F.Number(level) and level > 0 and F.Call(GetQuestDifficultyColor,level)
                local r,g,b = tint and tint.r or .2,tint and tint.g or 1,tint and tint.b or .2
                if F.Number(level) and level > 0 then title = "["..level.."] "..title end
                if first then GameTooltip:SetText(title,r,g,b); first = false
                else GameTooltip:AddLine(" "); GameTooltip:AddLine(title,r,g,b,true) end
                if q and #q.objectives > 0 then
                    for objectiveIndex, objective in ipairs(q.objectives) do
                        if not action.objective or action.objective == objectiveIndex then
                            local text = objective.text or F.QuestLog:Progress(objective)
                            local shade = objective.finished and .6 or 1
                            GameTooltip:AddLine("- "..text,shade,shade,shade,true)
                        end
                    end
                else
                    local body = F.UI:ActionBody(action)
                    if body ~= "" then GameTooltip:AddLine(body,1,1,1,true)
                    elseif action.type == "pickup" then GameTooltip:AddLine("Accept this quest.",1,1,1,true)
                    elseif action.type == "turnin" then GameTooltip:AddLine("Turn in this quest.",1,1,1,true) end
                end
            end
        end
        if first then GameTooltip:SetText(step.text or "Guide step",1,.82,0) end
        GameTooltip:AddLine(" ")
        GameTooltip:AddLine("Forever Rested - Step "..number,.55,.55,.55)
        if not pin.entry and F.MapAreas:Spec() then GameTooltip:AddLine("Blue areas: objective regions supplied by the game",.4,.75,1,true) end
        if pin.edge then GameTooltip:AddLine("Outside minimap view: direction marker",1,1,1,true) end
        GameTooltip:Show()
    end, true)
    pin:Hide(); return pin
end
function P:Style(pin)
    local number = self:DestinationStep()
    if pin.entry then number = pin.entry.index end
    local state = F.GuideEngine:StepState(number)
    -- An alongside destination has its own quest progress within the numbered step.
    local task = pin.entry and pin.entry.task or F.Navigation.waypointTask
    if state ~= "skipped" and task then
        state = F.GuideEngine:TaskState(task)
    end
    pin.icon:SetTexture("Interface\\AddOns\\ForeverRested\\Media\\Status" .. (self.stateIcons[state] or "NotStarted") .. ".tga")
    if state == "ongoing" or state == "notready" or state == "ready" then
        pin.icon:SetTexture("Interface\\AddOns\\ForeverRested\\Media\\MapStepBadge-thick.tga")
        pin.icon:SetVertexColor(1,1,1)
        pin.icon:Show()
        pin.fill:SetVertexColor(1,.82,.08,1)
        pin.fill:Hide()
        pin.number:SetTextColor(.22,.12,.035)
        pin.number:SetShadowColor(.22,.12,.035,1)
        pin.number:SetShadowOffset(1,0)
    else
        pin.icon:Show()
        pin.icon:SetVertexColor(1,1,1)
        pin.fill:Hide()
        if state == "skipped" or state == "failed" then
            pin.number:SetTextColor(236/255,187/255,49/255)
            pin.number:SetShadowColor(0,0,0,1)
            pin.number:SetShadowOffset(1,-1)
        else
            pin.number:SetTextColor(.22,.12,.035)
            pin.number:SetShadowColor(.22,.12,.035,1)
            pin.number:SetShadowOffset(1,0)
        end
    end
    local label = tostring(number)
    local isMini = pin == self.mini or pin.isMini
    local size = #label >= 3 and 10 or (#label == 2 and 12 or 14)
    if isMini then size = size - 1 end
    local goldNumber = state == "skipped" or state == "failed"
    -- Keep multi-digit labels inside the rim and avoid the inherited serif font.
    pin.number:SetFont("Interface\\AddOns\\ForeverRested\\Media\\SegoeUISemibold.ttf", size, goldNumber and "OUTLINE" or "")
    pin.number:SetText(label)
end
function P:RotateMini(facing)
    if self:PinsHidden() then return end
    self:RotateAreaMini(facing)
    local pin,n = self.mini,F.Navigation
    if not pin or not self.radius or not F.Number(n.north) or not F.Number(n.west) then return end
    local x,y = -n.west,n.north
    if self.rotate and F.Number(facing) then
        local c,s = math.cos(facing),math.sin(facing)
        x,y = x*c+y*s,-x*s+y*c
    end
    x,y = x/self.radius*self.halfWidth,y/self.radius*self.halfHeight
    local length = math.sqrt((x/self.halfWidth)^2+(y/self.halfHeight)^2)
    pin.edge = length > self.limit
    if pin.edge then x,y = x/length*self.limit,y/length*self.limit end
    local scale = pin:GetScale()
    pin:ClearAllPoints(); pin:SetPoint("CENTER",Minimap,"CENTER",x/scale,y/scale)
end
function P:TaskLocation(task)
    local id,q = F.GuideEngine:Resolve(task)
    local location
    if task.type == "objective" and q then
        local record = F.GuideEngine:TargetRecord(q)
        location = record and record.location
    end
    if not location and id then
        local data = F.GuideEngine:Metadata(id)
        if data then
            local role = task.type == "pickup" and "start" or task.type == "turnin" and "end" or "requirement"
            location = F.Navigation:ReferencePoint(data,role)
        end
    end
    location = location or task
    local map = location.zone and F.Navigation:ResolveAreaMap(location) or location.mapID
    if F.Number(map) and F.Number(location.x) and F.Number(location.y)
        and location.x>=0 and location.x<=1 and location.y>=0 and location.y<=1 then
        return map,location.x,location.y
    end
end
function P:RotateAreaMini(facing)
    if self:PinsHidden() then
        for _,pin in pairs(self.areaMini) do pin:Hide() end
        return
    end
    local radius = F.Call(C_Minimap and C_Minimap.GetViewRadius)
    local w,h = Minimap and F.Call(Minimap.GetWidth,Minimap),Minimap and F.Call(Minimap.GetHeight,Minimap)
    if not F.Number(radius) or radius<=0 or not F.Number(w) or not F.Number(h) then return end
    local rotate = F.Call(GetCVarBool,"rotateMinimap")==true
        and F.Call(C_Minimap and C_Minimap.IsRotateMinimapIgnored)~=true
    for _,pin in pairs(self.areaMini) do
        if pin.north and pin.west then
            local x,y = -pin.west,pin.north
            if rotate and F.Number(facing) then
                local c,s = math.cos(facing),math.sin(facing)
                x,y = x*c+y*s,-x*s+y*c
            end
            x,y = x/radius*w/2,y/radius*h/2
            local limit = math.max(0,1-11.8/math.min(w/2,h/2))
            local visible = (x/(w/2))^2+(y/(h/2))^2<=limit^2
            pin:ClearAllPoints();pin:SetPoint("CENTER",Minimap,"CENTER",(x+(pin.entry.offsetX or 0)),y)
            pin:SetShown(visible and F.Call(Minimap.IsShown,Minimap)==true)
        else pin:Hide() end
    end
end
function P:UpdateAreaPins()
    local map = WorldMapFrame
    local viewedMap = not self:PinsHidden() and map and F.Call(map.IsShown,map) and F.Call(map.GetMapID,map)
    local playerMap = F.Call(C_Map and C_Map.GetBestMapForUnit,"player")
    local playerInstance,playerPos
    if CreateVector2D and F.Number(F.Navigation.px) and F.Number(F.Navigation.py) then
        playerInstance,playerPos = F.Call(C_Map and C_Map.GetWorldPosFromMapPos,playerMap,
            CreateVector2D(F.Navigation.px,F.Navigation.py))
    end
    local px,py = F.XY(playerPos)
    local keepWorld,keepMini = {},{}
    -- Bound the preview by guide order, even when nearby quests are far ahead.
    local limit = F.db.mapStepLimit or 10
    local destination = self:DestinationStep()
    local last = math.min(#F.Guide.steps, F.db.step + limit - 1)
    -- A selected destination retains its marker and uses one preview slot.
    if destination < F.db.step or destination > last then last = last - 1 end
    local allowed = {[destination] = true}
    for index = F.db.step, last do allowed[index] = true end
    local seen,positions = {},{}
    local activeKey = self:TaskKey(F.Navigation.waypointTask)
    if activeKey then seen[activeKey] = true end
    if F.Navigation.targetMap and F.Number(F.Navigation.tx) and F.Number(F.Navigation.ty) then
        positions[#positions+1] = {zone=F.Navigation.targetMap,x=F.Navigation.tx,y=F.Navigation.ty}
    end
    for index,step in ipairs(F.Guide.steps) do
        local visible = allowed[index] and self:ShouldShow(index)
        for actionIndex,task in ipairs(F.GuideEngine:Tasks(step,true)) do
            local taskKey = self:TaskKey(task)
            if visible and task~=F.Navigation.waypointTask and not (taskKey and seen[taskKey])
                and F.GuideEngine:TaskState(task)~="complete" then
                local zone,x,y = self:TaskLocation(task)
                if zone and taskKey then seen[taskKey] = true end
                local key = index..":"..actionIndex
                local entry = {index=index,task=task,key=key}
                if zone then
                    local overlap = 0
                    for _,point in ipairs(positions) do
                        if point.zone==zone and (point.x-x)^2+(point.y-y)^2<.000225 then overlap=overlap+1 end
                    end
                    entry.offsetX = overlap * 22
                    positions[#positions+1] = {zone=zone,x=x,y=y}
                end
                if zone and zone==viewedMap and map.AcquirePin then
                    keepWorld[key] = true
                    local pin = self.areaWorld[key]
                    if not pin then
                        F.Call(map.AcquirePin,map,"ForeverRestedMapPinTemplate",x,y,entry)
                        pin = self.areaWorld[key]
                    end
                    if pin then
                        pin.entry, pin.marker.entry = entry,entry
                        pin.marker:ClearAllPoints();pin.marker:SetPoint("CENTER",pin,"CENTER",entry.offsetX,0)
                        pin:SetPosition(x,y);self:Style(pin.marker);pin.marker:Show();pin:Show()
                    end
                end
                if not self:PinsHidden() and zone and zone==playerMap and Minimap and playerInstance and F.Number(px) and F.Number(py) then
                    local instance,pos = F.Call(C_Map and C_Map.GetWorldPosFromMapPos,zone,CreateVector2D(x,y))
                    local tx,ty = F.XY(pos)
                    if instance==playerInstance and F.Number(tx) and F.Number(ty) then
                        keepMini[key] = true
                        local pin = self.areaMini[key]
                        if not pin then pin=self:Create(Minimap);pin:SetSize(20,20);pin.isMini=true;self.areaMini[key]=pin end
                        pin.entry,pin.north,pin.west = entry,tx-px,ty-py
                        self:Style(pin)
                    end
                end
            end
        end
    end
    local release = {}
    for key,pin in pairs(self.areaWorld) do if not keepWorld[key] then release[#release+1]=pin end end
    for _,pin in ipairs(release) do if map and map.RemovePin then map:RemovePin(pin) end end
    for key,pin in pairs(self.areaMini) do
        if not keepMini[key] then pin.north,pin.west=nil,nil;pin:Hide() end
    end
    self:RotateAreaMini(F.Call(GetPlayerFacing))
end
ForeverRestedMapPinMixin = {}
function ForeverRestedMapPinMixin:OnLoad()
    -- AcquirePin invokes OnLoad after assigning the owning map.
    if self.UseFrameLevelType then self:UseFrameLevelType("PIN_FRAME_LEVEL_AREA_POI") end
    if self.SetScalingLimits then self:SetScalingLimits(1,1,1) end
end
function ForeverRestedMapPinMixin:OnAcquired(x,y,entry)
    if type(self.SetPosition)~="function" then P.worldFailed=true;self:Hide();return end
    self:UseFrameLevelType("PIN_FRAME_LEVEL_AREA_POI")
    self:SetScalingLimits(1,1,1)
    self:SetPosition(x,y)
    if not self.marker then self.marker=P:Create(self); self.marker:SetPoint("CENTER",self,"CENTER",0,0) end
    self.marker:ClearAllPoints();self.marker:SetPoint("CENTER",self,"CENTER",entry and (entry.offsetX or 0) or 0,0)
    self.entry,self.marker.entry = entry,entry
    if entry then
        P.areaWorld[entry.key] = self
        P:Style(self.marker); self.marker:Show()
        return
    end
    P.nativeWorld=self; P.world=self.marker
    P:Style(self.marker); self.marker:Show()
    F.MapAreas:Update(self)
end
function ForeverRestedMapPinMixin:OnReleased()
    if self.marker then self.marker:Hide() end
    if P.nativeWorld==self then P.nativeWorld=nil end
    if self.entry and P.areaWorld[self.entry.key]==self then P.areaWorld[self.entry.key]=nil end
    self.entry = nil
end
function P:UpdateWorld()
    local n,map=F.Navigation,WorldMapFrame
    local valid=map and F.Call(map.IsShown,map) and F.Call(map.GetMapID,map)==n.targetMap
        and n.targetMap and F.Number(n.tx) and F.Number(n.ty)
        and self:ShouldShow(self:DestinationStep(),n.waypointTask)
        and not self:PinsHidden()
    if not valid then
        F.MapAreas:Hide()
        if self.nativeWorld and map and map.RemovePin then map:RemovePin(self.nativeWorld) end
        if self.world then self.world:Hide() end
        return
    end
    if not map.AcquirePin or self.worldFailed then return end
    if not self.nativeWorld then
        local ok=pcall(map.AcquirePin,map,"ForeverRestedMapPinTemplate",n.tx,n.ty)
        if not ok or not self.nativeWorld then
            self.worldFailed=true
            F.Print("World map marker disabled after a pin initialization failure; minimap remains available.")
        end
    else
        self.nativeWorld:SetPosition(n.tx,n.ty)
        self.nativeWorld:Show()
        self:Style(self.world);self.world:Show()
        F.MapAreas:Update(self.nativeWorld)
    end
end
function P:Update()
    local n = F.Navigation
    self:CreateMapToggle()
    if self.updateToggleAppearance then self.updateToggleAppearance() end
    self:UpdateWorld()
    self:UpdateAreaPins()
    if self.world then self:Style(self.world) end
    if self:PinsHidden() or not n.targetMap or not F.Number(n.tx) or not F.Number(n.ty)
        or not self:ShouldShow(self:DestinationStep(),n.waypointTask) then
        if self.mini then self.mini:Hide() end
        self.radius = nil; return
    end
    local radius = F.Call(C_Minimap and C_Minimap.GetViewRadius)
    local w,h = Minimap and F.Call(Minimap.GetWidth,Minimap),Minimap and F.Call(Minimap.GetHeight,Minimap)
    if Minimap and F.Call(Minimap.IsShown,Minimap) and F.Number(radius) and radius>0
        and F.Number(w) and w>32 and F.Number(h) and h>32 and F.Number(n.north) and F.Number(n.west) then
        if not self.mini then self.mini=self:Create(Minimap); self.mini:SetSize(20,20) end
        self.radius,self.halfWidth,self.halfHeight = radius,w/2,h/2
        self.limit=1-11.8/math.min(self.halfWidth,self.halfHeight)
        self.rotate = (F.Call(GetCVarBool,"rotateMinimap")==true or F.Call(GetCVar,"rotateMinimap")=="1")
            and F.Call(C_Minimap and C_Minimap.IsRotateMinimapIgnored)~=true
        self:RotateMini(F.Call(GetPlayerFacing))
        self:Style(self.mini); self.mini:Show()
    else
        self.radius=nil
        if self.mini then self.mini:Hide() end
    end
end
