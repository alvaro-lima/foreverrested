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
    ['Teldrassil']="Rut'theran Village", ['Darnassus']="Rut'theran Village", ['Moonglade']='Moonglade',
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
                        -- The world taxi map lists visible nodes that this
                        -- character cannot use; it supplies positions only.
                        if node.isUndiscovered==true then
                            local stop=flightName(node.name)
                            if type(stop)=='string' and stop~='' then known[stop]=nil end
                        end
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
        local currentStop,reachable
        reachable={}
        for index=1,F.Call(NumTaxiNodes) or 0 do
            local state=F.Call(TaxiNodeGetType,index)
            local stop=flightName(F.Call(TaxiNodeName,index))
            if state=='CURRENT' then currentStop=stop end
            if state=='REACHABLE' and stop then reachable[stop]=true end
        end
        if currentStop then
            F.db.observedFlightConnections=F.db.observedFlightConnections or {}
            F.db.observedFlightConnections[currentStop]=reachable
        end
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
function T:RememberHearth()
    local name=F.Call(GetBindLocation)
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
    local zone=F.Call(GetRealZoneText) or info and info.name
    if type(name)=='string' and type(zone)=='string' and zone~='' then
        F.db.hearthLocation={name=name,zone=zone}
    end
end
function T:ReadyHearth(zone)
    local name=F.Call(GetBindLocation)
    if type(name)~='string' or name=='' then return end
    local saved=F.db and F.db.hearthLocation
    local matched=name==zone or saved and saved.name==name and saved.zone==zone
    -- Only explicit town/zone matches are used for an existing character.
    for area,stop in pairs(self.flightStops) do if area==zone and name==stop then matched=true end end
    local inns={['Stoutlager Inn']='Loch Modan',['Lion\'s Pride Inn']='Elwynn Forest',
        ['Deepwater Tavern']='Wetlands',Goldshire='Elwynn Forest',Kharanos='Dun Morogh',Dolanaar='Teldrassil'}
    if inns[name]==zone then matched=true end
    if not matched then return end
    local count=F.Call(C_Item and C_Item.GetItemCount or GetItemCount,6948,false)
    if not F.Number(count) or count<1 then return end
    local start,duration,enabled=F.Call(C_Container and C_Container.GetItemCooldown or GetItemCooldown,6948)
    if type(start)=='table' then start,duration,enabled=start.startTime,start.duration,start.isEnabled end
    local now=F.Call(GetTime)
    if not F.Number(start) or not F.Number(duration) or not F.Number(now)
        or enabled==nil or enabled==false or enabled==0 or start+duration>now then return end
    return name
end
local kalimdor={Moonglade=true,Darkshore=true,Ashenvale=true,['Stonetalon Mountains']=true,Teldrassil=true,Darnassus=true}
function T:Continent(zone)
    if kalimdor[zone] or zone=='Moonglade' or zone=='Felwood' or zone=='Winterspring' then return 'kalimdor' end
    if self.roads[zone] and not kalimdor[zone] then return 'eastern' end
end
-- Approximate Wetlands road approach shown on the zone map at Dun Algaz.
-- Compare points on this same map; this is a detour check, not a path solver.
function T:WalkingExit(step)
    if (step.entryTravel or step.travelMode=='hearth') and self:ReadyHearth(step.entryGoal or step.travelTo) then return end
    if not (step.travelQuestID or step.entryTravel) or F.Call(UnitOnTaxi,'player')==true then return end
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
    if step.travelMode=='druid-flight' or step.travelMode=='teleport-moonglade'
        or step.travelMode=='boat' or step.travelMode=='portal-ruttheran'
        or step.travelMode=='portal-darnassus' or step.travelFrom=='Darnassus' then return end
    if (step.entryTravel or step.travelMode=='hearth') and self:ReadyHearth(step.entryGoal or step.travelTo) then return end
    if self:WalkingExit(step) then return end
    local from,to=self.flightStops[step.travelFrom],self.flightStops[step.travelTo]
    if (from=='Moonglade' or from=="Rut'theran Village") and to=='Auberdine' then
        local connections=F.db and F.db.observedFlightConnections
        if not (connections and connections[from] and connections[from][to]) then return end
    end
    -- Known nodes on different continents still require the boat connection.
    if from and to and from~=to and kalimdor[step.travelFrom]==kalimdor[step.travelTo]
        and self:KnowsFlightPath(to) then return from,to end
end
function T:AutoFlightStep()
    if self.relocationPending or not F.db or not F.Guide or F.Combat() or F.Call(IsShiftKeyDown)==true
        or F.Call(UnitOnTaxi,'player')==true then return end
    local step=F.Guide.steps[F.db.step]
    if not step or not (step.travelQuestID or step.entryTravel) or F.db.skipped[F.db.step]
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
    if step.travelMode=='teleport-moonglade' or step.travelMode=='druid-flight'
        or step.travelMode=='portal-ruttheran' or step.travelMode=='portal-darnassus'
        or step.travelMode=='boat' then return step.note end
    if step.entryTravel or step.travelMode=='hearth' then
        local hearth=self:ReadyHearth(step.travelMode=='hearth' and step.travelTo or step.entryGoal or step.travelTo)
        if hearth then return 'Hearth to '..hearth..'.' end
        if step.travelMode=='hearth' and self.hearthCast and self.hearthCast.stepID==step.id
            and step.hearthBinding then return 'Hearth to '..step.hearthBinding..'.' end
        if step.travelMode=='hearth' then
            local goal=step.entryGoal or step.travelTo
            local legs=self:Route(step.travelFrom,goal)
            return legs[1] and legs[1].text or 'Continue to '..goal..'.'
        end
    end
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
    if not (step.travelQuestID or step.entryTravel) then return step.note end
    if not from then
        if step.travelFrom and step.travelTo and (step.note or ''):lower():find('fly to',1,true) then
            local legs=self:Route(step.travelFrom,step.travelTo)
            return legs[1] and legs[1].text or step.note
        end
        return step.note
    end
    if self:KnowsFlightPath(from) then return 'Fly to '..to..'.' end
    return 'At '..from..', learn its flight path, then fly to '..to..'.'
end
-- Reviewed arrival areas that pass close to a flight master. Other arrivals
-- require client flight coordinates and a nearby quest destination.
local flightAreas={
    Darkshore={x=.327,y=.437}, Ashenvale={x=.346,y=.488}, Wetlands={x=.095,y=.596},
}
function T:EnsureLocalFlightPath()
    if not F.Guide or not F.Guide.faction or not F.db or F.Combat()
        or F.GuideEngine.manualHold or F.Call(UnitOnTaxi,'player')==true then return end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
    local zone=F.Call(GetRealZoneText) or info and info.name
    -- Darnassus shares Rut'theran's taxi name, but its master is beyond the portal.
    if not zone or zone=='Darnassus' then return end
    local stop=self.flightStops[zone]
    if not stop or self:KnowsFlightPath(stop) then return end
    local step=F.Guide.steps[F.db.step]
    if not step or step.flightPathTravel then return end
    local id='flightpath:local:'..F.Guide.id..':'..zone
    if F.db.manualSkippedSteps and F.db.manualSkippedSteps[id] then return end
    for index,existing in ipairs(F.Guide.steps) do
        if existing.id==id then
            if not F.GuideEngine:Done(existing)
                and not (F.db.manualSkippedSteps and F.db.manualSkippedSteps[id]) then
                F.db.skipped[index]=nil
                if index<F.db.step then F.db.step=index end
            end
            return
        end
    end
    local subzone=F.Call(GetSubZoneText)
    local area=flightAreas[zone]
    local px,py=area and F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,
        F.Navigation:ResolveAreaMap({zone=zone}),'player'))
    local inTown=subzone==stop or area and F.Number(px) and F.Number(py)
        and (px-area.x)^2+(py-area.y)^2<=.07^2
    if not inTown then return end
    local location=F.db.flightPathLocations and F.db.flightPathLocations[stop]
    local point=location and F.Number(location.mapID) and F.Number(location.x)
        and F.Number(location.y) and {mapID=location.mapID,x=location.x,y=location.y}
    local skipped={}
    for index,action in ipairs(F.Guide.steps) do if F.db.skipped[index] then skipped[action.id]=true end end
    table.insert(F.Guide.steps,F.db.step,{id=id,type='travel',optional=true,
        flightPathTravel=true,flightPathStop=stop,confirmOnNext=true,
        resumeStepID=step.id,text='Learn the flight path at '..stop,
        note='Speak to the flight master at '..stop..' to learn this flight path. The step completes when the game confirms it.',
        mapID=point and point.mapID,x=point and point.x,y=point and point.y})
    F.db.skipped={}
    for index,action in ipairs(F.Guide.steps) do F.db.skipped[index]=skipped[action.id] or nil end
    return true
end
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
-- Player-observed Forever beta boarding position, 2026-10-04 (54.9, 97.1).
local ruttheran={zone='Teldrassil',x=.549,y=.971,name="Rut'theran boat boarding area"}
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
function T:TransportArrived(step)
    if step.travelMode~='boat' and step.travelMode~='druid-flight'
        and step.travelMode~='portal-ruttheran' and step.travelMode~='portal-darnassus' then return false end
    if F.Call(UnitOnTaxi,'player')==true then return false end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
    if not info or info.name~=step.travelTo then return false end
    if step.travelMode=='druid-flight' then return true end
    if step.travelMode=='portal-darnassus' then return true end
    if step.travelMode=='portal-ruttheran' then
        local village=self.docks.Teldrassil.Darkshore
        local villageMap=F.Navigation:ResolveAreaMap(village)
        local x,y=F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,villageMap,'player'))
        return F.Number(x) and F.Number(y) and (x~=0 or y~=0)
            and (x-village.x)^2+(y-village.y)^2<=.10^2
    end
    local dock=self.docks[step.travelTo] and self.docks[step.travelTo][step.travelFrom]
    if not dock then return false end
    local arrivalMap=F.Navigation:ResolveAreaMap(dock)
    local x,y=F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,arrivalMap,'player'))
    return F.Number(x) and F.Number(y) and (x~=0 or y~=0)
        and (x-dock.x)^2+(y-dock.y)^2<=.05^2
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
                step.travelMode=leg.mode
                step.hearthBinding=leg.hearthBinding
                step.travelLeg,step.travelZones,step.travelFinal=number,zones,number==#legs
                step.text='Travel to '..leg.zone
                step.note=leg.text..' Destination: '..(final.travelDestination.name or final.travelDestination.zone)..'. This travel step advances on arrival.'
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
function T:SkipTravelNearNext()
    if not F.Guide or not F.db or F.Call(UnitOnTaxi,'player')==true then return end
    local first=F.db.step
    if not F.Guide.steps[first] or F.Guide.steps[first].type~='travel'
        or F.Guide.steps[first].flightPathTravel then return end
    local nextIndex=first
    while F.Guide.steps[nextIndex] and F.Guide.steps[nextIndex].type=='travel' do nextIndex=nextIndex+1 end
    local nextStep=F.Guide.steps[nextIndex]
    if not nextStep then return end
    for _,task in ipairs(F.GuideEngine:Tasks(nextStep)) do
        local id=F.GuideEngine:Resolve(task)
        local map,x,y
        if id then map,x,y=F.Navigation:ClientWaypoint(task,id) end
        if not map then map,x,y=F.StepPins:TaskLocation(task) end
        local px,py=F.XY(map and F.Call(C_Map and C_Map.GetPlayerMapPosition,map,'player'))
        if F.Number(x) and F.Number(y) and F.Number(px) and F.Number(py)
            and (px~=0 or py~=0) and (px-x)^2+(py-y)^2<=.03^2 then
            for index=first,nextIndex-1 do F.db.skipped[index]=true end
            F.GuideEngine.manualHold=nil
            F.GuideEngine.selectedStep=nil
            F.db.step=nextIndex
            F.UI:Refresh()
            return true
        end
    end
end
function T:Tick()
    self:RefreshEntryPlan()
    if self.entryPending and self:EnsureEntry() and F.UI.frame then F.UI:Refresh() end
    local onTaxi=F.Call(UnitOnTaxi,'player')==true
    local boarded=onTaxi and self.onTaxi~=true
    self.onTaxi=onTaxi
    if self:SkipTravelNearNext() then return end
    self:ReplanAfterRelocation()
    local step=F.Guide and F.db and F.Guide.steps[F.db.step]
    -- Confirm only the active flight leg on boarding, never subsequent legs
    -- merely because the player is still aboard the same flight.
    if boarded and step and (step.travelQuestID or step.entryTravel) and self:FlightLeg(step) then
        local quest=F.QuestLog.byID[step.travelQuestID]
        if step.travelAction~='turnin' or quest and quest.complete then
            F.db.confirmedSteps=F.db.confirmedSteps or {}
            F.db.confirmedSteps[step.id]=true
        end
    end
    if step and (step.travelQuestID or step.entryTravel) and F.GuideEngine:Done(step) then
        self.motion=nil
        -- From may hold an already reached travel checkpoint. Arrival resumes
        -- travel automatically; quest and trainer restart points remain held.
        F.GuideEngine.manualHold=nil
        local previous=F.db.step
        local previousGuide=F.Guide
        F.GuideEngine:AdvanceSafe()
        if F.db.step~=previous or F.Guide~=previousGuide then F.UI:Refresh() end
        return
    end
    local dock=step and (step.travelQuestID or step.entryTravel) and self:DepartureDock(step)
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
        if step.entryTravel then
            self.boatBoardedStepID=step.id
            self.motion=nil
            F.Navigation:Update()
            return
        end
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
    "Return to Auberdine harbor and board the boat bound for Menethil Harbor. Stay aboard through intermediate stops.")
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
road("Teldrassil","Darkshore","Go to the marked Rut'theran dock and take the boat to Auberdine.","Take the Rut'theran Village boat from Auberdine, then use the portal to Darnassus.")
road("Darnassus","Teldrassil","Leave Darnassus through its eastern gate into Teldrassil.","Follow Teldrassil's western road into Darnassus.")
road("Darnassus","Darkshore","Use the Darnassus portal to Rut'theran Village, then board the boat to Auberdine at the marked dock.","Board the Rut'theran Village boat in Auberdine, then use the portal into Darnassus.")
-- Rut'theran is in the Teldrassil map, but it is a separate transport hub
-- from the island quests reached through Darnassus's eastern gate.
local function villagePortal(from)
    if from=='Darnassus' then
        return {from=from,zone='Teldrassil',mode='portal-ruttheran',
            text="Use the Darnassus portal to Rut'theran Village."}
    end
    return {from='Teldrassil',zone='Darnassus',mode='portal-darnassus',
        text="At Rut'theran Village, use the portal into Darnassus."}
end
local function villageBoat(from)
    if from=='Teldrassil' then
        return {from=from,zone='Darkshore',mode='boat',
            text="At the marked Rut'theran dock, board the boat to Auberdine."}
    end
    return {from='Darkshore',zone='Teldrassil',mode='boat',
        text="At the marked Auberdine dock, board the boat to Rut'theran Village."}
end
-- Forever beta: corrected player observation, 2026-10-04.
-- Silva Fil'naveth flies druids to Rut'theran; Auberdine then requires the boat.
-- This class route does not require the ordinary Auberdine node to be learned.
-- The flight destination must still be checked with the Moonglade flight master.
function T:ReadyMoongladeTeleport()
    local _,class=F.Call(UnitClass,'player')
    if class~='DRUID' then return false end
    local learned=F.Call(IsSpellKnown,18960)==true or F.Call(IsPlayerSpell,18960)==true
        or F.Call(C_SpellBook and C_SpellBook.IsSpellKnown,18960)==true
    if not learned then return end
    local start,duration,enabled=F.Call(GetSpellCooldown,18960)
    local cooldown=F.Call(C_Spell and C_Spell.GetSpellCooldown,18960)
    if type(cooldown)=='table' then start,duration,enabled=cooldown.startTime,cooldown.duration,cooldown.isEnabled end
    local now=F.Call(GetTime)
    if enabled==0 or enabled==false or (F.Number(start) and F.Number(duration) and F.Number(now)
        and duration>1.5 and start+duration>now) then return end
    return true
end
function T:DruidShortcut(from,to)
    local _,class=F.Call(UnitClass,'player')
    local faction=F.Call(UnitFactionGroup,'player') or F.Guide and F.Guide.faction
    if class~='DRUID' or faction~='Alliance' or to~='Darkshore'
        or (from~='Ashenvale' and from~='Moonglade') then return end
    if from=='Moonglade' then
        return {
            {from=from,zone='Teldrassil',mode='druid-flight',text="Speak to Silva Fil'naveth in Nighthaven and take the druid flight toward Darnassus, landing at Rut'theran Village. This is separate from Moonglade's ordinary flight master."},
            {from='Teldrassil',zone=to,mode='boat',text="At the marked Rut'theran dock, board the boat to Auberdine."},
        }
    end
    if not self:ReadyMoongladeTeleport() then return end
    return {
        {from=from,zone='Moonglade',mode='teleport-moonglade',text='Cast Teleport: Moonglade. Then take the druid flight toward Darnassus and the Rut\'theran boat to Auberdine. This class shortcut avoids the run north from Astranaar. Travel time has not been measured.'},
        self:DruidShortcut('Moonglade',to)[1],
        self:DruidShortcut('Moonglade',to)[2],
    }
end
function T:CloserDruidDeparture(flightFrom)
    local ordinary=F.db and F.db.flightPathLocations and F.db.flightPathLocations[flightFrom]
    if not ordinary or not CreateVector2D then return false end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local x,y=F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,map,'player'))
    local dm,dx,dy=F.Navigation:TravelWaypoint({travelMode='druid-flight'})
    local function world(m,px,py)
        if not m or not F.Number(px) or not F.Number(py) then return end
        local instance,pos=F.Call(C_Map and C_Map.GetWorldPosFromMapPos,m,CreateVector2D(px,py))
        local wx,wy=F.XY(pos)
        if instance~=nil and F.Number(wx) and F.Number(wy) then return instance,wx,wy end
    end
    local pi,px,py=world(map,x,y)
    local di,sx,sy=world(dm,dx,dy)
    local oi,ox,oy=world(ordinary.mapID,ordinary.x,ordinary.y)
    if pi==nil or pi~=di or pi~=oi then return false end
    return (sx-px)^2+(sy-py)^2 < (ox-px)^2+(oy-py)^2
end
function T:Route(from,to)
    if from==to then return {} end
    local hearth=self:ReadyHearth(to)
    if hearth then return {{from=from,zone=to,mode='hearth',hearthBinding=hearth,text='Hearth to '..hearth..'.'}} end
    if to=='Moonglade' and self:ReadyMoongladeTeleport() then
        return {{from=from,zone=to,mode='teleport-moonglade',text='Cast Teleport: Moonglade, then continue to your quest destination.'}}
    end
    -- A nearby hearth is useful only with an evidenced binding and ready item.
    -- These reviewed approaches to Westfall avoid an intercontinental detour.
    if to=='Westfall' then
        for _,zone in ipairs({'Stormwind City','Elwynn Forest'}) do
            local binding=self:ReadyHearth(zone)
            if binding and from~=zone then
                local legs={{from=from,zone=zone,mode='hearth',hearthBinding=binding,text='Hearth to '..binding..'.'}}
                for _,leg in ipairs(self:Route(zone,to)) do legs[#legs+1]=leg end
                return legs
            end
        end
    end
    if from=='Moonglade' and to=='Darnassus' then
        local druid=self:DruidShortcut(from,'Darkshore')
        if druid then return {druid[1],villagePortal('Teldrassil')} end
    end
    if from=='Teldrassil' and to=='Darnassus' then
        local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
        local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
        local x,y=F.XY(F.Call(C_Map and C_Map.GetPlayerMapPosition,map,'player'))
        local village=self.docks.Teldrassil.Darkshore
        if info and info.name=='Teldrassil' and F.Number(x) and F.Number(y)
            and (x-village.x)^2+(y-village.y)^2<=.10^2 then
            return {villagePortal('Teldrassil')}
        end
    end
    local flightFrom,flightTo=self:FlightLeg({travelFrom=from,travelTo=to})
    local function directFlight()
        local leg={from=from,zone=to,mode='flight',
            text='Speak to the flight master at '..flightFrom..' and fly to '..flightTo..'.'}
        if to=='Darnassus' then
            leg.zone='Teldrassil'
            return {leg,villagePortal('Teldrassil')}
        end
        return {leg}
    end
    local shortcut=self:DruidShortcut(from,to)
    if shortcut and from=='Moonglade' and self:CloserDruidDeparture(flightFrom) then return shortcut end
    -- Both endpoints must be observed before a regular flight supersedes the
    -- class detour. Destination-only cache entries are insufficient evidence.
    if flightFrom and self:KnowsFlightPath(flightFrom) then
        return directFlight()
    end
    if shortcut then return shortcut end
    if flightFrom then
        return directFlight()
    end
    local _,class=F.Call(UnitClass,'player')
    if class=='DRUID' and to=='Moonglade' then
        return {{zone=to,text="Use Teleport: Moonglade if learned. Otherwise visit your druid trainer for the travel spell before beginning this class detour."}}
    end
    if class=='DRUID' and from=='Moonglade' then
        local legs=self:DruidShortcut(from,'Darkshore')
        if legs then
            for _,leg in ipairs(self:Route('Darkshore',to)) do legs[#legs+1]=leg end
            return legs
        end
    end
    local queue,seen={{zone=from,legs={}}},{[from]=true}
    local index=1
    while queue[index] do
        local current=queue[index]; index=index+1
        if current.zone==to then
            local expanded={}
            for _,leg in ipairs(current.legs) do
                if leg.from=='Darnassus' and leg.zone=='Darkshore' then
                    expanded[#expanded+1]=villagePortal('Darnassus')
                    expanded[#expanded+1]=villageBoat('Teldrassil')
                elseif leg.from=='Darkshore' and leg.zone=='Darnassus' then
                    expanded[#expanded+1]=villageBoat('Darkshore')
                    expanded[#expanded+1]=villagePortal('Teldrassil')
                else expanded[#expanded+1]=leg end
            end
            return expanded
        end
        local destinations={}
        for zone in pairs(self.roads[current.zone] or {}) do destinations[#destinations+1]=zone end
        table.sort(destinations)
        for _,zone in ipairs(destinations) do
            if not seen[zone] then
                seen[zone]=true
                local legs={}; for _,leg in ipairs(current.legs) do legs[#legs+1]=leg end
                local dock=self.docks[current.zone] and self.docks[current.zone][zone]
                legs[#legs+1]={from=current.zone,zone=zone,text=self.roads[current.zone][zone],mode=dock and 'boat' or nil}
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
function T:ObserveObjectiveStage()
    local step=F.Guide and F.db and F.Guide.steps[F.db.step]
    local task=step and step.tasks and #step.tasks==1 and step.tasks[1] or step
    local id=task and task.type=='objective' and F.GuideEngine:Resolve(task)
    local point=id and F.GuideEngine:ObjectiveLocation(id)
    if not point or not point.zone or F.GuideEngine.manualHold then
        self.objectiveStage=nil
        return
    end
    local key=tostring(F.Guide.id)..':'..tostring(task.id)..':'..tostring(id)..':'
        ..point.zone..':'..tostring(point.itemID or point.resultItemID or '')
    if key~=self.objectiveStage then
        self.objectiveStage=key
        self.entryPending=true
    end
end
function T:EnsureEntry()
    if not self.entryPending or not F.Guide or not F.Guide.faction or not F.db then return end
    if F.Call(UnitOnTaxi,'player')==true then return end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
    local from=F.Call(GetRealZoneText) or info and info.name
    if type(from)~='string' or from=='' then return end
    local guide,index=F.Guide,F.db.step
    local target,task,point
    for position=index,#guide.steps do
        local step=guide.steps[position]
        if not F.db.skipped[position] and F.GuideEngine:Applies(step) and not F.GuideEngine:Done(step,F.GuideEngine:Resolve(step)) then
            if step.entryTravel then self.entryPending=nil;return end
            if step.travelTo then
                if step.travelFrom==from then self.entryPending=nil;return end
                target,point=step,step.travelFinal and step.travelDestination or {zone=step.travelTo}
                break
            end
            if step.zone and F.Number(step.x) and F.Number(step.y) then
                target,point=step,step;break
            end
            for _,action in ipairs(step.tasks or {step}) do
                local id=F.GuideEngine:Resolve(action)
                if id and F.GuideEngine:Applies(action) and not F.GuideEngine:Done(action,id,F.QuestLog.byID[id]) then
                    local data=F.GuideEngine:Metadata(id) or {}
                    local role=action.type=='pickup' and 'start' or action.type=='turnin' and 'end' or 'requirement'
                    point=F.GuideEngine:ActionLocation(action)
                    if action.type=='objective' then
                        local record=F.GuideEngine:TargetRecord(F.QuestLog.byID[id] or {id=id,title=data.title})
                        point=F.GuideEngine:ObjectiveLocation(id) or F.GuideEngine:TargetLocation(F.QuestLog.byID[id] or {id=id,title=data.title}) or point
                    end
                    local clientMap,x,y=F.Navigation:ClientWaypoint(action,id)
                    local clientInfo=clientMap and F.Call(C_Map and C_Map.GetMapInfo,clientMap)
                    if clientInfo and not (action.type=='objective' and point and point.zone and point.zone~=clientInfo.name) then
                        point={zone=clientInfo.name,mapID=clientMap,x=x,y=y,name=data.title}
                    end
                    target,task=step,action;break
                end
            end
            if target then break end
        end
    end
    self.entryPending=nil
    local zone=point and point.zone
    if not target or not zone or zone==from then return end
    local legs=self:Route(from,zone)
    local zones={};for _,leg in ipairs(legs) do zones[#zones+1]=leg.zone end
    local skipped,reasons={},{}
    for position,step in ipairs(guide.steps) do
        if F.db.skipped[position] then skipped[step.id]=true end
        reasons[step.id]=F.GuideEngine.catchUpReasons and F.GuideEngine.catchUpReasons[position]
    end
    for number,leg in ipairs(legs) do
        local step={id='entry-travel:'..guide.id..':'..target.id..':'..from..':'..zone..':'..number,type='travel',optional=true,
            entryTravel=true,entryGoal=zone,resumeStepID=guide.steps[index].id,
            text='Travel to '..leg.zone,note=leg.text,travelMode=leg.mode,hearthBinding=leg.hearthBinding,
            confirmOnNext=true,travelFrom=leg.from or from,travelTo=leg.zone,
            travelLeg=number,travelZones=zones,travelFinal=number==#legs,
            travelDestination=point or {zone=zone},travelQuestID=task and task.questID or target.travelQuestID,
            travelAction=task and task.type or target.travelAction}
        table.insert(guide.steps,index+number-1,step)
    end
    F.db.skipped={};F.GuideEngine.catchUpReasons={}
    for position,step in ipairs(guide.steps) do
        F.db.skipped[position]=skipped[step.id] or F.db.manualSkippedSteps[step.id] or nil
        F.GuideEngine.catchUpReasons[position]=reasons[step.id]
    end
    return #legs>0
end
-- Ordinary quest returns need the same location-aware planning as guide entry.
-- Run once per active action so skipping a suggested trip does not recreate it.
function T:EnsureTurninTravel()
    if not F.Guide or not F.db or F.Combat() or F.GuideEngine.manualHold
        or F.Call(UnitOnTaxi,'player')==true then return end
    local step=F.Guide.steps[F.db.step]
    if not step or step.entryTravel or step.travelQuestID then return end
    local task=step.tasks and #step.tasks==1 and step.tasks[1] or step
    if task.type~='turnin' and task.type~='pickup' then self.lastTurninStep=nil;return end
    local id,q=F.GuideEngine:Resolve(task)
    if not id or task.type=='turnin' and (not q or not q.complete) or F.GuideEngine:Done(task,id,q) then return end
    if self.lastTurninStep==step then return end
    -- Wait for a valid location before recording the check (login can lack it).
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
    local zone=F.Call(GetRealZoneText) or info and info.name
    if type(zone)~='string' or zone=='' then return end
    self.lastTurninStep=step
    self.entryPending=true
    return self:EnsureEntry()
end
function T:EntryTitle(step)
    if step.travelMode=='teleport-moonglade' then return 'Teleport to Moonglade.' end
    if step.travelMode=='druid-flight' then return "Fly to Rut'theran Village." end
    if step.travelMode=='portal-ruttheran' then return "Portal to Rut'theran Village." end
    if step.travelMode=='portal-darnassus' then return 'Portal to Darnassus.' end
    if step.travelMode=='boat' then return 'Take the boat to '..(self.flightStops[step.travelTo] or step.travelTo)..'.' end
    local hearth=self:ReadyHearth(step.travelMode=='hearth' and step.travelTo or step.entryGoal)
    if hearth then return 'Hearth to '..hearth..'.' end
    if step.travelMode=='hearth' and self.hearthCast and self.hearthCast.stepID==step.id
        and step.hearthBinding then return 'Hearth to '..step.hearthBinding..'.' end
    local _,to=self:FlightLeg(step)
    if to then return 'Fly to '..to..'.' end
    return 'Travel to '..step.travelTo..'.'
end
function T:HearthCast(event,unit,spellID)
    if unit~='player' or spellID~=8690 then return end
    if event=='UNIT_SPELLCAST_FAILED' or event=='UNIT_SPELLCAST_INTERRUPTED' then
        self.hearthCast=nil
        return
    end
    if event~='UNIT_SPELLCAST_START' then return end
    local step=F.Guide and F.db and F.Guide.steps[F.db.step]
    if not step or step.travelMode~='hearth' then return end
    local zone=F.Call(GetRealZoneText)
    self.hearthCast={stepID=step.id,from=zone,started=F.Call(GetTime)}
end
function T:RefreshEntryPlan()
    local step=F.Guide and F.db and F.Guide.steps[F.db.step]
    if not step or not step.entryTravel or F.Call(UnitOnTaxi,'player')==true
        or F.Call(UnitCastingInfo,'player') or F.Call(UnitChannelInfo,'player') then return end
    local map=F.Call(C_Map and C_Map.GetBestMapForUnit,'player')
    local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
    local zone=F.Call(GetRealZoneText) or info and info.name
    if not zone then return end
    local cast=self.hearthCast
    if cast then
        if cast.stepID==step.id and cast.from==zone
            and (not F.Number(cast.started) or not F.Number(F.Call(GetTime))
                or F.Call(GetTime)-cast.started<30) then return end
        self.hearthCast=nil
    end
    local legs=self:Route(zone,step.entryGoal)
    local method=legs[1] and legs[1].mode or 'ground'
    if method==(step.travelMode or 'ground') and (not legs[1] or legs[1].zone==step.travelTo) then return end
    if F.GuideEngine:Done(step) then return end
    local guide,index=F.Guide,F.db.step
    local skipped,reasons={},{}
    for position,action in ipairs(guide.steps) do
        if F.db.skipped[position] then skipped[action.id]=true end
        reasons[action.id]=F.GuideEngine.catchUpReasons and F.GuideEngine.catchUpReasons[position]
    end
    while guide.steps[index] and guide.steps[index].entryTravel do table.remove(guide.steps,index) end
    F.db.skipped={};F.GuideEngine.catchUpReasons={}
    for position,action in ipairs(guide.steps) do
        F.db.skipped[position]=skipped[action.id] or nil
        F.GuideEngine.catchUpReasons[position]=reasons[action.id]
    end
    self.entryPending=true
    if self:EnsureEntry() and F.UI.frame then F.UI:Refresh() end
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
                local record=F.GuideEngine:TargetRecord(F.QuestLog.byID[id] or {id=id,title=data.title})
                objective=F.GuideEngine:ObjectiveLocation(id) or F.GuideEngine:TargetLocation(F.QuestLog.byID[id] or {id=id,title=data.title}) or objective
                local from=task.type=='objective' and start or objective or start
                local destination=task.type=='objective' and objective or point(data,'end')
                if from and destination and from.zone and destination.zone and from.zone~=destination.zone then
                    local legs=self:Route(from.zone,destination.zone)
                    local zones={};for _,leg in ipairs(legs) do zones[#zones+1]=leg.zone end
                    for index,leg in ipairs(legs) do
                        result[#result+1]={id='travel:'..step.id..':'..index,type='travel',
                            text='Travel to '..leg.zone..' - '..(data.title or 'key quest'),
                            note=leg.text..' Destination: '..(destination.name or destination.zone)..'. This travel step advances on arrival.',
                            critical=true,criticalReason=step.criticalReason or task.criticalReason or 'Travel for a key quest',
                            confirmOnNext=true,travelQuestID=id,travelAction=task.type,
                            travelZones=zones,travelLeg=index,travelFinal=index==#legs,
                            travelFrom=leg.from,travelTo=leg.zone,travelMode=leg.mode,hearthBinding=leg.hearthBinding,
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
    for _,step in ipairs(result) do
        if step.type=='travel' then
            step.optional=true
            step.critical,step.criticalReason=nil,nil
            if step.text then step.text=step.text:gsub('^Optional:%s*','') end
        end
    end
    guide.steps=result
    if guide.authoredSteps and not runtime then guide.authoredSteps=result end
end
