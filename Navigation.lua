local _, F = ...
local N = {}
F.Navigation = N
local function valid(map, x, y)
    return F.Number(map) and map > 0 and F.Number(x) and F.Number(y)
        and x >= 0 and x <= 1 and y >= 0 and y <= 1 and (x ~= 0 or y ~= 0)
end
function N:Waypoint()
    self.source, self.label, self.waypointTask = nil, nil, nil
    for _, step in ipairs(F.GuideEngine:Tasks(nil, true)) do
        local id, q = F.GuideEngine:Resolve(step)
        if not F.GuideEngine:Done(step, id, q) then
            if step.travelQuestID then
                -- Aim at the departure harbor before a boat crossing, rather
                -- than trying to draw a bearing across different continents.
                local harbor
                if step.travelFrom == 'Wetlands' and step.travelTo == 'Darkshore' then
                    harbor = {zone='Wetlands',x=0.0832,y=0.5857,name='Menethil Harbor (Karl Boran area)'}
                elseif step.travelFrom == 'Darkshore' and
                    (step.travelTo == 'Wetlands' or step.travelTo == 'Teldrassil' or step.travelTo == 'Darnassus') then
                    harbor = {zone='Darkshore',x=0.3677,y=0.4428,name='Auberdine harbor (Laird area)'}
                end
                if harbor then
                    local map = self:ResolveAreaMap(harbor)
                    if valid(map,harbor.x,harbor.y) then
                        self.source,self.label,self.waypointTask='Travel area (approx.)',harbor.name,step
                        return map,harbor.x,harbor.y
                    end
                end
                if step.travelFinal then
                    local map,x,y=F.Call(C_QuestLog and C_QuestLog.GetNextWaypoint,step.travelQuestID)
                    if valid(map,x,y) then
                        self.source,self.waypointTask='Client waypoint',step
                        return map,x,y
                    end
                    local data=F.GuideEngine:Metadata(step.travelQuestID)
                    local point=data and self:ReferencePoint(data,step.travelAction=='turnin' and 'end' or 'requirement')
                    map=point and self:ResolveAreaMap(point)
                    if point and valid(map,point.x,point.y) then
                        self.source,self.label,self.waypointTask='Public area (approx.)',point.name,step
                        return map,point.x,point.y
                    end
                end
            end
            if id and not F.QuestLog:TurnedIn(id) then
                local map, x, y = F.Call(C_QuestLog and C_QuestLog.GetNextWaypoint, id)
                if valid(map, x, y) then self.source, self.waypointTask = "Client waypoint", step; return map, x, y end
                if step.type == "objective" and q then
                    local record = F.GuideEngine:TargetRecord(q)
                    local location = record and record.location
                    if location then
                        map = self:ResolveAreaMap(location)
                        if valid(map, location.x, location.y) then
                            self.source, self.label = "Hunting area (approx.)", location.label
                            self.waypointTask = step
                            return map, location.x, location.y
                        end
                    end
                end
                local metadata = F.GuideEngine:Metadata(id)
                if metadata and (step.type == "pickup" or q) then
                    local role = step.type == "pickup" and "start" or step.type == "turnin" and "end" or "requirement"
                    local point = self:ReferencePoint(metadata, role)
                    if point then
                        map = self:ResolveAreaMap(point)
                        if valid(map, point.x, point.y) then
                            self.source, self.label = "Public area (approx.)", point.name
                            self.waypointTask = step
                            return map, point.x, point.y
                        end
                    end
                end
            end
            local map = step.zone and self:ResolveAreaMap(step) or step.mapID
            if valid(map, step.x, step.y) then
                self.source, self.waypointTask = "Guide coordinate (approx.)", step; return map, step.x, step.y
            end
        end
    end
end
function N:ReferencePoint(metadata, role)
    local candidates = {}
    for _, point in ipairs(metadata.locations) do
        if (point.role == role or role == "requirement" and point.role == "sourcerequirement")
            and F.Number(point.x) and F.Number(point.y) then
            candidates[#candidates + 1] = point
        end
    end
    local map = F.Call(C_Map and C_Map.GetBestMapForUnit, "player")
    local info = F.Call(C_Map and C_Map.GetMapInfo, map)
    local px, py = F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition, map, "player"))
    if info and F.Number(px) and F.Number(py) then
        table.sort(candidates, function(a, b)
            local ad = a.zone == info.name and (a.x-px)^2 + (a.y-py)^2 or math.huge
            local bd = b.zone == info.name and (b.x-px)^2 + (b.y-py)^2 or math.huge
            return ad < bd
        end)
    end
    return candidates[1]
end
function N:ResolveAreaMap(location)
    -- Validate the data's map against this client; don't apply zone percentages
    -- to a continent or an unrelated map with a similar numeric identifier.
    local known = F.AllianceZoneMaps or {}
    local requested = location.mapID or known[location.zone]
    local info = requested and F.Call(C_Map and C_Map.GetMapInfo, requested)
    if info and info.name == location.zone then return requested end
    local map = F.Call(C_Map and C_Map.GetBestMapForUnit, "player")
    for _ = 1, 5 do
        info = F.Call(C_Map and C_Map.GetMapInfo, map)
        if not info then break end
        if info.name == location.zone then return map end
        if not info.parentMapID or info.parentMapID == map then break end
        map = info.parentMapID
    end
end
function N:Update()
    self:UpdateToolTarget()
    self.distance, self.angle, self.bearing, self.north, self.west, self.reason = nil, nil, nil, nil, nil, "No valid waypoint"
    self.targetMap, self.tx, self.ty = self:Waypoint()
    self.map = F.Call(C_Map and C_Map.GetBestMapForUnit, "player")
    self.px, self.py = F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition, self.map, "player"))
    if not self.targetMap then return end
    if not valid(self.map, self.px, self.py) or not CreateVector2D then
        self.reason = "Player position unavailable"; return
    end
    local instance, player = F.Call(C_Map and C_Map.GetWorldPosFromMapPos, self.map, CreateVector2D(self.px, self.py))
    local targetInstance, target = F.Call(C_Map and C_Map.GetWorldPosFromMapPos, self.targetMap, CreateVector2D(self.tx, self.ty))
    local px, py = F.XY(player)
    local tx, ty = F.XY(target)
    if not instance or instance ~= targetInstance or not F.Number(px) or not F.Number(py)
        or not F.Number(tx) or not F.Number(ty) then self.reason = "Destination in another space / map API unavailable"; return end
    local north, west = tx - px, ty - py
    self.north, self.west = north, west
    self.distance = math.sqrt(north * north + west * west)
    local facing = F.Call(GetPlayerFacing)
    if not F.Number(facing) then self.reason = "Player facing unavailable"; return end
    if not math.atan2 then self.reason = "Bearing API unavailable"; return end
    self.bearing = math.atan2(west, north)
    self.angle = self.bearing - facing
    self.reason = nil
end
function N:UpdateToolTarget()
    self.followBearing,self.followDistance,self.followAngle,self.followGUID=nil,nil,nil,nil
    local guid=F.Call(UnitGUID,"target")
    if not guid then return end
    if F.Call(UnitCanAttack,"player","target")~=true or F.Call(UnitIsDead,"target")==true
        or F.Call(UnitIsDeadOrGhost,"target")==true then
        F.SecureTarget.toolTargetGUID=nil; return
    end
    -- UnitPosition can be absent/restricted for creatures. Never estimate a
    -- moving unit from a static hunting-area coordinate or read hidden positions.
    local tx,ty,_,instance=F.Call(UnitPosition,"target")
    local px,py,_,playerInstance=F.Call(UnitPosition,"player")
    local facing=F.Call(GetPlayerFacing)
    if not F.Number(tx) or not F.Number(ty) or not F.Number(px) or not F.Number(py)
        or not F.Number(instance) or instance~=playerInstance or not F.Number(facing) or not math.atan2 then return end
    local north,west=tx-px,ty-py
    self.followBearing=math.atan2(west,north)
    self.followDistance=math.sqrt(north*north+west*west)
    self.followAngle,self.followGUID=self.followBearing-facing,guid
end
