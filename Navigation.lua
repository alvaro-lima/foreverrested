local _, F = ...
local N = {}
F.Navigation = N
local function valid(map, x, y)
    return F.Number(map) and map > 0 and F.Number(x) and F.Number(y)
        and x >= 0 and x <= 1 and y >= 0 and y <= 1 and (x ~= 0 or y ~= 0)
end
-- Remember an observed client waypoint for this specific action. Loading
-- screens can briefly remove the live POI without invalidating its destination.
function N:ClientWaypoint(task,id)
    self.clientPoints=self.clientPoints or {}
    local quest=F.QuestLog.byID[id]
    local key=tostring(F.Guide and F.Guide.id)..':'..tostring(task.id or id)..':'..
        tostring(task.travelAction or task.type)..':'..tostring(quest and quest.complete==true)
    local map,x,y=F.Call(C_QuestLog and C_QuestLog.GetNextWaypoint,id)
    if valid(map,x,y) then self.clientPoints[key]={map,x,y};return map,x,y end
    local cached=self.clientPoints[key]
    if cached then return unpack(cached) end
end
function N:TravelWaypoint(step)
    -- The client has no evidenced portal-entrance coordinate for these legs.
    if step.travelMode=='portal-ruttheran' or step.travelMode=='portal-darnassus' then return end
    -- A spell is the next action; a ground arrow to Moonglade would be misleading.
    if step.travelMode=='teleport-moonglade' then return end
    if step.travelMode=='druid-flight' then
        -- NPC 11800, installed Forever QuestieDB area 493: 44.15, 45.23.
        local point={zone='Moonglade',x=.4415,y=.4523,name="Silva Fil'naveth"}
        local map=self:ResolveAreaMap(point)
        if map then return map,point.x,point.y,'Druid flight master (approx.)',point.name end
        return
    end
    if step.travelMode=='boat' and F.Travel.boatBoardedStepID==step.id then return end
    if step.travelMode~='boat' and (step.entryTravel or step.travelMode=='hearth')
        and F.Travel:ReadyHearth(step.entryGoal or step.travelTo) then return end
    local exit=F.Travel:WalkingExit(step)
    if exit then return exit.mapID,exit.x,exit.y,'Road exit (approx.)',exit.name end
    local flight=F.Travel:DepartureFlight(step)
    if flight and valid(flight.mapID,flight.x,flight.y) then
        return flight.mapID,flight.x,flight.y,'Flight master',flight.name
    end
    local dock=F.Travel:DepartureDock(step)
    if dock then
        local map=self:ResolveAreaMap(dock)
        if valid(map,dock.x,dock.y) then return map,dock.x,dock.y,'Travel area (approx.)',dock.name end
        return -- A missing dock map must not redirect to a different continent.
    end
    if step.travelFinal then
        local map,x,y=self:ClientWaypoint(step,step.travelQuestID)
        if valid(map,x,y) then return map,x,y,'Client waypoint' end
        local data=F.GuideEngine:Metadata(step.travelQuestID)
        local point=data and self:ReferencePoint(data,step.travelAction=='turnin' and 'end' or 'requirement')
        map=point and self:ResolveAreaMap(point)
        if point and valid(map,point.x,point.y) then return map,point.x,point.y,'Public area (approx.)',point.name end
    end
    local point=F.Travel:ArrivalArea(step)
    local map=point and self:ResolveAreaMap(point)
    if point and valid(map,point.x,point.y) then return map,point.x,point.y,'Travel area (approx.)',point.name end
end
function N:Waypoint()
    self.source, self.label, self.waypointTask = nil, nil, nil
    -- From holds a restart point even when live progress already completes it.
    -- Keep that step navigable until the user resumes automation.
    local held=F.GuideEngine.manualHold==true
    for _, step in ipairs(F.GuideEngine:Tasks(nil, true)) do
        local id, q = F.GuideEngine:Resolve(step)
        if held or not F.GuideEngine:Done(step, id, q) then
            if step.type=='travel' or step.travelQuestID or step.entryTravel then
                local map,x,y,source,label=self:TravelWaypoint(step)
                if not map and (step.travelMode=='teleport-moonglade' or step.travelMode=='druid-flight'
                    or step.travelMode=='portal-ruttheran' or step.travelMode=='portal-darnassus'
                    or step.travelMode=='boat' and F.Travel.boatBoardedStepID==step.id) then return end
                if map then
                    self.source,self.label,self.waypointTask=source,label,step
                    return map,x,y
                end
            end
            if id and (held or not F.QuestLog:TurnedIn(id)) then
                local map, x, y
                if step.type == "objective" and q then
                    local location = F.GuideEngine:ObjectiveLocation(id) or F.GuideEngine:TargetLocation(q)
                    if not location then
                        location = F.GuideEngine:ActionLocation(step)
                    end
                    if location then
                        map = self:ResolveAreaMap(location)
                        if valid(map, location.x, location.y) then
                            self.source, self.label = F.QuestObjectiveLocations and F.QuestObjectiveLocations[id] and "Objective area (approx.)" or "Hunting area (approx.)", location.label or location.name
                            self.waypointTask = step
                            return map, location.x, location.y
                        end
                    end
                end
                map, x, y = self:ClientWaypoint(step,id)
                if valid(map, x, y) then self.source, self.waypointTask = "Client waypoint", step; return map, x, y end
                local metadata = F.GuideEngine:Metadata(id)
                if metadata and (held or step.type == "pickup" or q) then
                    local role = step.type == "pickup" and "start" or step.type == "turnin" and "end" or "requirement"
                    local point = F.GuideEngine:ActionLocation(step)
                    if point then
                        map = self:ResolveAreaMap(point)
                        if valid(map, point.x, point.y) then
                            self.source, self.label = "Public area (approx.)", point.name
                            self.waypointTask = step
                            return map, point.x, point.y
                        end
                    end
                end
                local area=step.type=='objective' and F.Travel:QuestArea(id)
                if area then
                    map=self:ResolveAreaMap(area)
                    if valid(map,area.x,area.y) then
                        self.source,self.label,self.waypointTask='Quest area (approx.)',area.name,step
                        return map,area.x,area.y
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
    local preferred={}
    for _, point in ipairs(metadata.locations) do
        if (point.role == role or role == "requirement" and point.role == "sourcerequirement")
            and F.Number(point.x) and F.Number(point.y) then
            candidates[#candidates + 1] = point
            if F.Guide and F.Guide.faction=='Alliance' and F.AllianceZoneMaps and F.AllianceZoneMaps[point.zone] then
                preferred[#preferred+1]=point
            end
        end
    end
    if #preferred>0 then candidates=preferred end
    local map = F.Call(C_Map and C_Map.GetBestMapForUnit, "player")
    local info = F.Call(C_Map and C_Map.GetMapInfo, map)
    local px, py = F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition, map, "player"))
    local instance, player
    if valid(map,px,py) and CreateVector2D then
        instance, player = F.Call(C_Map and C_Map.GetWorldPosFromMapPos,map,CreateVector2D(px,py))
    end
    local wx, wy = F.XY(player)
    local best, bestRank, bestDistance
    for _, point in ipairs(candidates) do
        local targetMap = self:ResolveAreaMap(point)
        if valid(targetMap,point.x,point.y) then
            local rank, distance = 2, math.huge
            if instance and F.Number(wx) and F.Number(wy) and CreateVector2D then
                local targetInstance, target = F.Call(C_Map and C_Map.GetWorldPosFromMapPos,targetMap,CreateVector2D(point.x,point.y))
                local tx, ty = F.XY(target)
                if instance == targetInstance and F.Number(tx) and F.Number(ty) then
                    rank, distance = 0, (tx-wx)^2 + (ty-wy)^2
                end
            end
            if rank > 0 and info and point.zone == info.name and F.Number(px) and F.Number(py) then
                rank, distance = 1, (point.x-px)^2 + (point.y-py)^2
            end
            if not best or rank < bestRank or rank == bestRank and distance < bestDistance then
                best, bestRank, bestDistance = point, rank, distance
            end
        end
    end
    return best
end
function N:ResolveAreaMap(location)
    -- Validate the data's map against this client; don't apply zone percentages
    -- to a continent or an unrelated map with a similar numeric identifier.
    local known = F.AllianceZoneMaps or {}
    local requested = location.mapID or known[location.zone]
    local info = requested and F.Call(C_Map and C_Map.GetMapInfo, requested)
    if info and info.name == location.zone then return requested end
    -- The open zone map can be available while the player map is temporarily
    -- absent (for example during a teleport or taxi transition).
    local viewed=F.Call(WorldMapFrame and WorldMapFrame.GetMapID,WorldMapFrame)
    local viewedInfo=viewed and F.Call(C_Map and C_Map.GetMapInfo,viewed)
    if viewedInfo and viewedInfo.name==location.zone then return viewed end
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
