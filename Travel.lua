local _, F = ...
local T = {roads={}}
F.Travel = T
-- Alliance flight stops; starter zones without a flight master are omitted.
T.flightStops={
    ['Ironforge']='Ironforge', ['Stormwind City']='Stormwind',
    ['Loch Modan']='Thelsamar', ['Wetlands']='Menethil Harbor',
    ['Darkshore']='Auberdine', ['Ashenvale']='Astranaar',
    ['Redridge Mountains']='Lakeshire', ['Westfall']='Sentinel Hill',
    ['Duskwood']='Darkshire', ['Stonetalon Mountains']='Stonetalon Peak',
    ['Teldrassil']="Rut'theran Village", ['Darnassus']="Rut'theran Village",
}
local function flightName(name)
    -- Taxi names include the zone ("Thelsamar, Loch Modan").
    return type(name)=='string' and name:match('^%s*(.-)%s*,') or name
end
function T:ObserveFlightPaths(atFlightMaster)
    if not F.db then return end
    F.db.knownFlightPaths=F.db.knownFlightPaths or {}
    F.db.flightPathLocations=F.db.flightPathLocations or {}
    local known=F.db.knownFlightPaths
    local function remember(name)
        local stop=flightName(name)
        if type(stop)=='string' and stop~='' then known[stop]=true end
    end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    if C_TaxiMap and C_TaxiMap.GetTaxiNodesForMap then
        -- Both continents, plus the current map for client-specific nodes.
        for _,area in ipairs({1414,1415,map or 1414}) do
            local nodes=F.Call(C_TaxiMap.GetTaxiNodesForMap,area)
            if type(nodes)=='table' then
                for _,node in ipairs(nodes) do
                    if node.faction==2 or node.faction==0 then
                        if node.isUndiscovered==false then remember(node.name) end
                        local x,y=F.XY(node.position)
                        if type(node.name)=='string' and node.name~='' and F.Number(x) and F.Number(y)
                            and x>=0 and x<=1 and y>=0 and y<=1 and (x~=0 or y~=0) then
                            F.db.flightPathLocations[flightName(node.name)]={mapID=area,x=x,y=y,name=node.name}
                        end
                    end
                end
            end
        end
    end
    if atFlightMaster then
        local nodes=map and F.Call(C_TaxiMap and C_TaxiMap.GetAllTaxiNodes,map)
        if type(nodes)=='table' then
            for _,node in ipairs(nodes) do
                if node.state==0 or node.state==1 then remember(node.name) end
            end
        end
        local count=F.Call(NumTaxiNodes)
        for index=1,F.Number(count) and count or 0 do
            local state=F.Call(TaxiNodeGetType,index)
            if state=='CURRENT' or state=='REACHABLE' then remember(F.Call(TaxiNodeName,index)) end
        end
    end
end
function T:KnowsFlightPath(stop)
    return F.db and F.db.knownFlightPaths and F.db.knownFlightPaths[stop]==true or false
end
local kalimdor={Darkshore=true,Ashenvale=true,['Stonetalon Mountains']=true,Teldrassil=true,Darnassus=true}
-- Approximate Wetlands road approach shown on the zone map at Dun Algaz.
-- Compare points on this same map; this is a detour check, not a path solver.
function T:WalkingExit(step)
    if not step.travelQuestID or F.Call(UnitOnTaxi,'player')==true then return end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
    if not info or info.name~=step.travelFrom then return end
    local x,y=F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,map,'player'))
    if not F.Number(x) or not F.Number(y) or (x==0 and y==0) then return end
    if step.travelFrom=='Wetlands' and step.travelTo=='Loch Modan' then
        local exitX,exitY=.535,.70
        local roadDistance=(x-exitX)^2+(y-exitY)^2
        local harborDistance=(x-.095)^2+(y-.596)^2
        if roadDistance<harborDistance then
            return {mapID=map,x=exitX,y=exitY,name='Dun Algaz road to Loch Modan'}
        end
    end
    -- For every guide, prefer a nearby destination over backtracking to a
    -- flight master when a reviewed, direct walking connection exists.
    local road=self.roads[step.travelFrom] and self.roads[step.travelFrom][step.travelTo]
    if not road or road:lower():find('boat',1,true) or road:lower():find('tram',1,true)
        or road:lower():find('portal',1,true) or not step.travelFinal then return end
    local destination=step.travelDestination
    local departure=F.db and F.db.flightPathLocations and F.db.flightPathLocations[self.flightStops[step.travelFrom]]
    if not destination or destination.zone~=step.travelTo or not departure or not CreateVector2D then return end
    local targetMap=F.Navigation:ResolveAreaMap(destination)
    local function world(pointMap,px,py)
        if not pointMap or not F.Number(px) or not F.Number(py) or px<0 or px>1 or py<0 or py>1
            or (px==0 and py==0) then return end
        local instance,pos=F.Call(C_Map and C_Map.GetWorldPosFromMapPos,pointMap,CreateVector2D(px,py))
        local wx,wy=F.XY(pos)
        if instance~=nil and F.Number(wx) and F.Number(wy) then return instance,wx,wy end
    end
    local pi,px,py=world(map,x,y)
    local di,dx,dy=world(targetMap,destination.x,destination.y)
    local fi,fx,fy=world(departure.mapID,departure.x,departure.y)
    -- Straight-line distance is only a conservative detour signal. It does
    -- not claim to estimate road length, flight time, or obstacle avoidance.
    if pi~=nil and pi==di and pi==fi and
        (dx-px)^2+(dy-py)^2 < .65^2*((fx-px)^2+(fy-py)^2) then
        return {mapID=targetMap,x=destination.x,y=destination.y,
            name=destination.name or destination.zone,roadNote=road}
    end
end
function T:FlightLeg(step)
    if self:WalkingExit(step) then return end
    local from,to=self.flightStops[step.travelFrom],self.flightStops[step.travelTo]
    -- Known nodes on different continents still require the boat connection.
    if from and to and from~=to and kalimdor[step.travelFrom]==kalimdor[step.travelTo]
        and self:KnowsFlightPath(to) then return from,to end
end
function T:AutoFlightStep()
    if self.relocationPending or not F.db or not F.Guide or F.Combat() or F.Call(IsShiftKeyDown)==true
        or F.Call(UnitOnTaxi,'player')==true then return end
    local step=F.Guide.steps[F.db.step]
    if not step or not step.travelQuestID or F.db.skipped[F.db.step]
        or F.GuideEngine:Done(step) then return end
    local from,to=self:FlightLeg(step)
    if not from then return end
    if step.travelAction=='turnin' then
        local quest=F.QuestLog.byID[step.travelQuestID]
        if not (quest and quest.complete) then return end
    end
    return step,from,to
end
function T:OpenFlightGossip()
    local step=self:AutoFlightStep()
    if not step or not C_GossipInfo then return end
    local choice
    for _,option in ipairs(F.Call(C_GossipInfo.GetOptions) or {}) do
        if option.type=='taxi' or option.icon==132057 then
            if choice then return end
            if option.status==nil or option.status==0 then choice=option.gossipOptionID end
        end
    end
    if choice then F.Call(C_GossipInfo.SelectOption,choice);return true end
end
function T:AutoFly()
    local step,from,to=self:AutoFlightStep()
    if not step or type(TakeTaxiNode)~='function' then return end
    -- Match the open flight master's current node, not just the player's zone.
    -- Never guess a destination slot or choose between duplicate names.
    local count=F.Call(NumTaxiNodes)
    local current,destination
    for index=1,F.Number(count) and count or 0 do
        local state=F.Call(TaxiNodeGetType,index)
        local name=flightName(F.Call(TaxiNodeName,index))
        if state=='CURRENT' then current=name end
        if state=='REACHABLE' and name==to then
            if destination then return end
            destination=index
        end
    end
    if not current then
        local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
        for _=1,8 do
            local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
            if not info or info.mapType==2 or not info.parentMapID or info.parentMapID==0 then break end
            map=info.parentMapID
        end
        local nodes=map and F.Call(C_TaxiMap and C_TaxiMap.GetAllTaxiNodes,map)
        for _,node in ipairs(type(nodes)=='table' and nodes or {}) do
            local name=flightName(node.name)
            if node.state==0 then current=name end
            if node.state==1 and name==to and F.Number(node.slotIndex) and node.slotIndex>0 then
                if destination then return end
                destination=node.slotIndex
            end
        end
    end
    if current~=from or not destination then return end
    F.Call(TakeTaxiNode,destination)
    return true
end
function T:FlightMapOpened()
    self.flightAttempts=10
    if self:AutoFly() then self.flightAttempts=nil end
end
function T:FlightMapTick()
    if not self.flightAttempts then return end
    self.flightAttempts=self.flightAttempts-1
    if self:AutoFly() or self.flightAttempts<=0 then self.flightAttempts=nil end
end
function T:Note(step)
    local walking=self:WalkingExit(step)
    if walking and walking.roadNote then
        return walking.roadNote..' Continue to '..walking.name..'. Walking avoids backtracking to the flight master. Next confirms arrival.'
    elseif walking then
        return 'Continue through Dun Algaz into Loch Modan. You are closer to the road than the Menethil flight master. '..
            (step.travelFinal and ('Then continue to '..
                (step.travelDestination and (step.travelDestination.name or step.travelDestination.zone) or step.travelTo)..'. ') or '')..
            'Next confirms arrival.'
    end
    local from,to=self:FlightLeg(step)
    if not step.travelQuestID or not from then return step.note end
    return 'Speak to the flight master at '..from..
        (self:KnowsFlightPath(from) and '' or ', learn its flight path,')..' and fly to '..to..
        '. The destination flight path is known. Check the offered destination before departing. '..
        (step.travelFinal and ('After landing, continue to '..
            (step.travelDestination and (step.travelDestination.name or step.travelDestination.zone) or step.travelTo)..'. ') or '')..
        'Next confirms arrival.'
end
-- Reviewed arrival areas that pass close to a flight master. Other arrivals
-- require client flight coordinates and a nearby quest destination.
local flightAreas={
    Darkshore={x=.327,y=.437}, Ashenvale={x=.346,y=.488}, Wetlands={x=.095,y=.596},
}
function T:NearFlightStop(leg,destination,final)
    local arrival=final and destination
    if not arrival or not F.Number(arrival.x) or not F.Number(arrival.y) then
        arrival=self:ArrivalArea({travelFrom=leg.from,travelTo=leg.zone})
    end
    local dock=self:DepartureDock({travelFrom=leg.zone,travelTo=leg.from})
    arrival=arrival or dock
    if not arrival or arrival.zone~=leg.zone then return false end
    local area=flightAreas[leg.zone]
    if area and F.Number(arrival.x) and F.Number(arrival.y) then
        return (arrival.x-area.x)^2+(arrival.y-area.y)^2<=.06^2
    end
    local stop=self.flightStops[leg.zone]
    local flight=F.db and F.db.flightPathLocations and F.db.flightPathLocations[stop]
    local map=arrival and F.Navigation and F.Navigation:ResolveAreaMap(arrival)
    if not flight or not map or not CreateVector2D or not F.Number(arrival.x) or not F.Number(arrival.y) then return false end
    local instance,pos=F.Call(C_Map and C_Map.GetWorldPosFromMapPos,map,CreateVector2D(arrival.x,arrival.y))
    local fi,fp=F.Call(C_Map and C_Map.GetWorldPosFromMapPos,flight.mapID,CreateVector2D(flight.x,flight.y))
    local x,y=F.XY(pos);local fx,fy=F.XY(fp)
    return instance~=nil and instance==fi and F.Number(x) and F.Number(y) and F.Number(fx) and F.Number(fy)
        and (x-fx)^2+(y-fy)^2<=400^2
end
function T:DepartureFlight(step)
    local from=self:FlightLeg(step)
    if not from or F.Call(UnitOnTaxi,'player')==true then return end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=F.Call(C_Map and C_Map.GetMapInfo,map)
    if not info or info.name~=step.travelFrom then return end
    return F.db.flightPathLocations and F.db.flightPathLocations[from]
end
-- Dock positions: Wowhead Classic transportation guide. These remain
-- approximate until verified against the Forever beta's transport changes.
local menethil={zone='Wetlands',x=.047,y=.570,name='Menethil northern boat dock'}
local auberdineSouth={zone='Darkshore',x=.327,y=.437,name='Auberdine southern boat dock'}
local auberdineNorth={zone='Darkshore',x=.332,y=.402,name='Auberdine northern boat dock'}
local ruttheran={zone='Teldrassil',x=.555,y=.930,name="Rut'theran boat dock"}
T.docks={
    Wetlands={Darkshore=menethil},
    Darkshore={Wetlands=auberdineSouth,Teldrassil=auberdineNorth,Darnassus=auberdineNorth},
    Teldrassil={Darkshore=ruttheran},Darnassus={Darkshore=ruttheran},
}
function T:DepartureDock(step)
    if self:FlightLeg(step) then return end
    local destinations=self.docks[step.travelFrom]
    return destinations and destinations[step.travelTo]
end
function T:QuestArea(id)
    -- Astranaar's western road entrance, sourced from Shindrell's location
    -- in the installed quest reference. This guides arrival, not the exact
    -- spot at which the waterskin can be filled.
    if id==94500 then return {zone='Ashenvale',x=.346,y=.488,name='Astranaar arrival area; fill the waterskin in the lake'} end
end
function T:ArrivalArea(step)
    if step.travelFinal and step.travelDestination and F.Number(step.travelDestination.x)
        and F.Number(step.travelDestination.y) then return step.travelDestination end
    if step.travelFrom=='Darkshore' and step.travelTo=='Ashenvale' then
        return {zone='Ashenvale',x=.346,y=.488,name='Astranaar western arrival area'}
    elseif step.travelFrom=='Ashenvale' and step.travelTo=='Darkshore' then
        return {zone='Darkshore',x=.327,y=.437,name='Auberdine southern boat dock'}
    end
end
function T:PositionChanged()
    self.relocationPending=true
    self.motion,self.flightAttempts=nil,nil
    if F.Navigation then F.Navigation.clientPoints={} end
end
function T:ReplanAfterRelocation()
    if not self.relocationPending or not F.db or not F.Guide or F.Combat()
        or F.Call(UnitOnTaxi,'player')==true or F.Call(UnitIsDeadOrGhost,'player')==true then return end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
    local x,y=F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,map,'player'))
    -- Loading screens can deliver the event before position data becomes ready.
    if not info or not info.name or not F.Number(x) or not F.Number(y) or (x==0 and y==0) then return end
    self.relocationPending=nil
    local guide,index=F.Guide,F.db.step
    local current=guide.steps[index]
    if current and current.travelQuestID then
        local last=index
        while true do
            local nextIndex=last+1
            while guide.steps[nextIndex] and guide.steps[nextIndex].flightPathQuestID==current.travelQuestID do
                nextIndex=nextIndex+1
            end
            local nextStep=guide.steps[nextIndex]
            if not nextStep or nextStep.travelQuestID~=current.travelQuestID
                or nextStep.travelAction~=current.travelAction then break end
            last=nextIndex
        end
        local final=guide.steps[last]
        local onRoute=info.name==current.travelFrom
        for _,zone in ipairs(current.travelZones or {}) do if info.name==zone then onRoute=true end end
        -- Ordinary route arrivals use existing completion checks. A teleport
        -- outside that itinerary needs a new connection to its actual goal.
        if not onRoute and final.travelFinal and final.travelDestination and final.travelDestination.zone then
            local legs=self:Route(info.name,final.travelDestination.zone)
            local zones={};for _,leg in ipairs(legs) do zones[#zones+1]=leg.zone end
            local skipped,reasons={},{}
            for position,step in ipairs(guide.steps) do
                if F.db.skipped[position] then skipped[step.id]=true end
                reasons[step.id]=F.GuideEngine.catchUpReasons and F.GuideEngine.catchUpReasons[position]
            end
            local steps={}
            for position=1,index-1 do steps[#steps+1]=guide.steps[position] end
            for number,leg in ipairs(legs) do
                local step={};for key,value in pairs(final) do step[key]=value end
                step.id=number==#legs and final.id or final.id..':reroute:'..info.name..':'..leg.zone
                step.travelFrom,step.travelTo=leg.from or info.name,leg.zone
                step.travelLeg,step.travelZones,step.travelFinal=number,zones,number==#legs
                step.text='Travel to '..leg.zone
                step.note=leg.text..' Destination: '..(final.travelDestination.name or final.travelDestination.zone)..'. Next confirms arrival.'
                steps[#steps+1]=step
            end
            for position=last+1,#guide.steps do steps[#steps+1]=guide.steps[position] end
            guide.steps=steps
            F.db.skipped={};F.GuideEngine.catchUpReasons={}
            for position,step in ipairs(steps) do
                F.db.skipped[position]=skipped[step.id] or nil
                F.GuideEngine.catchUpReasons[position]=reasons[step.id] or step.travelQuestID and step.criticalReason or nil
            end
            F.GuideEngine.selectedStep=nil
            F.db.step=math.min(index,#steps)
        end
    end
    F.Refresh()
    return true
end
function T:Tick()
    self:ReplanAfterRelocation()
    local step=F.Guide and F.db and F.Guide.steps[F.db.step]
    if step and step.travelQuestID and F.GuideEngine:Done(step) then
        self.motion=nil
        -- From may hold an already reached travel checkpoint. Arrival resumes
        -- travel automatically; quest and trainer restart points remain held.
        F.GuideEngine.manualHold=nil
        local previous=F.db.step
        F.GuideEngine:AdvanceSafe()
        if F.db.step~=previous then F.UI:Refresh() end
        return
    end
    local dock=step and step.travelQuestID and self:DepartureDock(step)
    if not dock then self.motion=nil; return end
    if step.travelAction=='turnin' then
        local quest=F.QuestLog.byID[step.travelQuestID]
        if not (quest and quest.complete) then self.motion=nil; return end
    end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=F.Call(C_Map and C_Map.GetMapInfo,map)
    local x,y=F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,map,'player'))
    local speed=F.Call(GetUnitSpeed,'player')
    if not info or info.name~=dock.zone or not F.Number(x) or not F.Number(y)
        or not F.Number(speed) or F.Call(IsSwimming)==true or F.Call(IsFalling)==true
        or F.Call(UnitOnTaxi,'player')==true or F.Call(UnitIsDeadOrGhost,'player')==true then
        self.motion=nil; return
    end
    local instance,position
    if CreateVector2D then
        instance,position=F.Call(C_Map.GetWorldPosFromMapPos,map,CreateVector2D(x,y))
    end
    local wx,wy=F.XY(position)
    if not F.Number(wx) or not F.Number(wy) then self.motion=nil; return end
    local sample=self.motion
    if not sample or sample.id~=step.id or sample.instance~=instance then
        sample={id=step.id,instance=instance,count=0};self.motion=sample
    end
    if (x-dock.x)^2+(y-dock.y)^2<=.02^2 then sample.nearDock=true end
    local distance=sample.x and math.sqrt((wx-sample.x)^2+(wy-sample.y)^2) or 0
    -- Ordinary movement and swimming cannot confirm boarding. Require three
    -- consecutive samples of passive world movement after visiting the dock.
    if sample.nearDock and speed==0 and distance>.5 and distance<30 then
        sample.count=sample.count+1
    else sample.count=0 end
    sample.x,sample.y=wx,wy
    if sample.count>=3 then
        F.db.confirmedSteps=F.db.confirmedSteps or {}
        F.db.confirmedSteps[step.id]=true
        self.motion=nil
        F.Refresh()
    end
end
local function road(a,b,outbound,inbound)
    T.roads[a]=T.roads[a] or {}; T.roads[b]=T.roads[b] or {}
    T.roads[a][b]=outbound; T.roads[b][a]=inbound
end
road("Wetlands","Darkshore",
    "Follow the road to Menethil Harbor. Board the boat bound for Auberdine; the Forever quest describes a Southshore stop. Stay aboard until Auberdine.",
    "Return to Auberdine harbor and board the boat bound for Menethil Harbor. Check the destination with the dock NPC; stay aboard through intermediate stops.")
road("Darkshore","Ashenvale","Follow the main road south from Auberdine into Ashenvale, then continue to Astranaar. Avoid hostile camps.",
    "Follow the road north from Astranaar into Darkshore, then continue to Auberdine harbor. Use an already unlocked flight if available.")
road("Loch Modan","Wetlands","Take the northern road through Dun Algaz into Wetlands. Stay on the road and avoid fighting the tunnel orcs if outmatched.",
    "Take the southern road through Dun Algaz into Loch Modan. Avoid pulling tunnel guards; use a known flight if available.")
road("Dun Morogh","Loch Modan","Follow the eastern road through the mountain pass into Loch Modan.","Follow the western mountain pass from Loch Modan into Dun Morogh.")
road("Ironforge","Dun Morogh","Leave Ironforge by its main gate into Dun Morogh.","Follow the road to Ironforge's main gate and enter the city.")
road("Ironforge","Stormwind City","Use the Deeprun Tram between Ironforge's Tinker Town and Stormwind's Dwarven District.","Use the Deeprun Tram between Stormwind's Dwarven District and Ironforge's Tinker Town.")
road("Stormwind City","Elwynn Forest","Leave Stormwind's main gate and follow the road into Elwynn Forest.","Follow the road through Goldshire to Stormwind's main gate.")
road("Elwynn Forest","Redridge Mountains","Follow the eastern road through Elwynn Forest into Redridge, then take the road to Lakeshire.","Follow the western road from Lakeshire into Elwynn Forest.")
road("Elwynn Forest","Westfall","Follow the western road across the bridge into Westfall. Continue on the road toward Sentinel Hill and Moonbrook.","Follow the northeastern road from Westfall across the bridge into Elwynn Forest.")
road("Elwynn Forest","Duskwood","Take the southern road across the river into Duskwood and continue toward Darkshire.","Take the northern road out of Duskwood across the river into Elwynn Forest.")
road("Duskwood","Redridge Mountains","Follow Duskwood's eastern road into Redridge and continue to Lakeshire.","Follow the southern road from Lakeshire into Duskwood.")
road("Ashenvale","Stonetalon Mountains","Take the southwestern mountain passage from Ashenvale into Stonetalon. Avoid Horde settlements.","Return through the northeastern mountain passage into Ashenvale, avoiding Horde settlements.")
road("Teldrassil","Darkshore","Use the Darnassus portal to Rut'theran Village, then take the Auberdine boat. Check the dock destination before boarding.","Take the Rut'theran Village boat from Auberdine, then use the portal to Darnassus.")
road("Darnassus","Teldrassil","Leave Darnassus through its eastern gate into Teldrassil.","Follow Teldrassil's western road into Darnassus.")
road("Darnassus","Darkshore","Use the Darnassus portal to Rut'theran Village, then board the Auberdine boat. Check its destination with the dock NPC.","Board the Rut'theran Village boat in Auberdine, then use the portal into Darnassus.")
function T:Route(from,to)
    local flightFrom,flightTo=self:FlightLeg({travelFrom=from,travelTo=to})
    if flightFrom then
        return {{from=from,zone=to,text='Speak to the flight master at '..flightFrom..' and fly to '..flightTo..'.'}}
    end
    local _,class=F.Call(UnitClass,'player')
    if class=='DRUID' and to=='Moonglade' then
        return {{zone=to,text="Use Teleport: Moonglade if learned. Otherwise visit your druid trainer for the travel spell before beginning this class detour."}}
    end
    if class=='DRUID' and from=='Moonglade' then
        return {{zone=to,text="Use your hearthstone if it returns you near "..to..", or speak to the Moonglade flight master and choose an available flight toward your quest destination. Check the offered destinations before travelling."}}
    end
    local queue,seen={{zone=from,legs={}}},{[from]=true}
    local index=1
    while queue[index] do
        local current=queue[index]; index=index+1
        if current.zone==to then return current.legs end
        local destinations={}
        for zone in pairs(self.roads[current.zone] or {}) do destinations[#destinations+1]=zone end
        table.sort(destinations)
        for _,zone in ipairs(destinations) do
            if not seen[zone] then
                seen[zone]=true
                local legs={}; for _,leg in ipairs(current.legs) do legs[#legs+1]=leg end
                legs[#legs+1]={from=current.zone,zone=zone,text=self.roads[current.zone][zone]}
                queue[#queue+1]={zone=zone,legs=legs}
            end
        end
    end
    return {{zone=to,text="Travel to "..to.." using an available safe route or an unlocked flight. Check the quest's destination NPC before leaving. This guide has no reviewed transport route for this connection."}}
end
function T:ReferenceLocation(data,role)
    local fallback
    for _,location in ipairs(data.locations or {}) do
        if location.role==role then
            fallback=fallback or location
            -- Shared NPC/object records can include Horde and Alliance copies.
            if F.AllianceZoneMaps and F.AllianceZoneMaps[location.zone] then return location end
        end
    end
    return fallback
end
function T:EnsureSteps(guide, runtime)
    local authored=runtime and guide.steps or guide.authoredSteps or guide.steps
    local result={}
    local function point(data,role)
        return self:ReferenceLocation(data,role)
    end
    for _,step in ipairs(authored) do
        if not step.travelQuestID and not step.flightPathTravel then
            local task=step.tasks and #step.tasks==1 and step.tasks[1] or step
            local id=F.GuideEngine:Resolve(task)
            if id and (step.critical or task.critical or F.QuestPolicy:Key(task))
                and (task.type=='objective' or task.type=='turnin') then
                local data=F.GuideEngine:Metadata(id) or {}
                local start=point(data,'start')
                local objective=point(data,'requirement') or point(data,'sourcerequirement')
                local from=task.type=='objective' and start or objective or start
                local destination=task.type=='objective' and objective or point(data,'end')
                if from and destination and from.zone and destination.zone and from.zone~=destination.zone then
                    local legs=self:Route(from.zone,destination.zone)
                    local zones={};for _,leg in ipairs(legs) do zones[#zones+1]=leg.zone end
                    for index,leg in ipairs(legs) do
                        result[#result+1]={id='travel:'..step.id..':'..index,type='travel',
                            text='Travel to '..leg.zone..' - '..(data.title or 'key quest'),
                            note=leg.text..' Destination: '..(destination.name or destination.zone)..'. Next confirms arrival. Use an unlocked flight or a suitably placed hearthstone if faster.',
                            critical=true,criticalReason=step.criticalReason or task.criticalReason or 'Travel for a key quest',
                            confirmOnNext=true,travelQuestID=id,travelAction=task.type,
                            travelZones=zones,travelLeg=index,travelFinal=index==#legs,
                            travelFrom=leg.from,travelTo=leg.zone,
                            travelDestination=destination,
                            travelX=destination.x,travelY=destination.y,classes=task.classes,minLevel=task.minLevel,
                            requiredRaces=task.requiredRaces,unlockTerminal=step.unlockTerminal or task.unlockTerminal}
                        local stop=self.flightStops[leg.zone]
                        local nextLeg=legs[index+1]
                        local usedNext=nextLeg and self:FlightLeg({travelFrom=nextLeg.from,travelTo=nextLeg.zone})
                        if stop and not self:KnowsFlightPath(stop) and not usedNext
                            and self:NearFlightStop(leg,destination,index==#legs) then
                            result[#result+1]={id='flightpath:'..step.id..':'..index,type='travel',
                                text='Learn the flight path at '..stop,
                                note='Speak to the flight master at '..stop..' and learn the flight path before continuing. Known flight paths complete automatically; use Next if the client cannot report this path.',
                                confirmOnNext=true,flightPathTravel=true,flightPathQuestID=id,
                                flightPathStop=stop,
                                unlockTerminal=step.unlockTerminal or task.unlockTerminal,
                                classes=task.classes,minLevel=task.minLevel,requiredRaces=task.requiredRaces}
                        end
                    end
                end
            end
            result[#result+1]=step
        end
    end
    guide.steps=result
    if guide.authoredSteps and not runtime then guide.authoredSteps=result end
end
