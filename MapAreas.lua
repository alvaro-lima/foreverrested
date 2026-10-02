local _, F = ...
local A = {}
F.MapAreas = A
function A:Spec()
    local n=F.Navigation
    local task=n.waypointTask
    if not task or task.type~="objective" then return end
    local id,q=F.GuideEngine:Resolve(task)
    if not q or F.GuideEngine:Done(task,id,q) then return end
    local hunting=false
    for index,o in ipairs(q.objectives or {}) do
        if not o.finished and (not task.objective or task.objective==index) then
            if o.type=="monster" or o.type=="item" and
                (task.mob or F.GuideEngine:MappedTarget(q,o,index)) then hunting=true end
        end
    end
    if not hunting then return end
    return id
end
function A:Hide()
    if self.blob then self.blob:Hide() end
    self.questID,self.mapID=nil,nil
end
function A:Update(pin)
    if pin.huntingArea then pin.huntingArea:Hide() end
    local id=self:Spec()
    local map=WorldMapFrame
    local canvas=map and F.Call(map.GetCanvas,map)
    if not id or not canvas or self.unavailable then self:Hide();return end
    if not self.blob then
        local blob=F.Call(CreateFrame,"QuestPOIFrame",nil,canvas)
        if not blob or type(blob.DrawBlob)~="function" then self.unavailable=true;return end
        self.blob=blob
        blob:EnableMouse(false)
        blob:SetFillTexture("Interface\\WorldMap\\UI-QuestBlob-Inside")
        blob:SetBorderTexture("Interface\\WorldMap\\UI-QuestBlob-Outside")
        blob:SetFillAlpha(90);blob:SetBorderAlpha(160);blob:SetBorderScalar(1)
    end
    local blob=self.blob
    blob:SetParent(canvas);blob:ClearAllPoints();blob:SetAllPoints(canvas)
    local level=F.Call(pin.GetFrameLevel,pin)
    if F.Number(level) then blob:SetFrameLevel(math.max(0,level-1)) end
    local mapID=F.Call(map.GetMapID,map)
    if self.questID~=id or self.mapID~=mapID then
        blob:SetMapID(mapID);blob:DrawNone();blob:DrawBlob(id,true)
        self.questID,self.mapID=id,mapID
    end
    blob:Show()
end
