local _, F = ...
local T = {roads={}}
F.Travel = T
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
function T:Tick()
    local step=F.Guide and F.db and F.Guide.steps[F.db.step]
    local dock=step and step.travelQuestID and self:DepartureDock(step)
    if not dock or F.GuideEngine:Done(step) then self.motion=nil; return end
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
    "Follow the road to Menethil Harbor. Board the boat bound for Auberdine; the Forever quest describes a Southshore stop. Stay aboard until Auberdine, then register its flight point.",
    "Return to Auberdine harbor and board the boat bound for Menethil Harbor. Check the destination with the dock NPC; stay aboard through intermediate stops.")
road("Darkshore","Ashenvale","Follow the main road south from Auberdine into Ashenvale, then continue to Astranaar. Avoid hostile camps and register Astranaar's flight point.",
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
function T:EnsureSteps(guide, runtime)
    local authored=runtime and guide.steps or guide.authoredSteps or guide.steps
    local result={}
    local function point(data,role)
        for _,location in ipairs(data.locations or {}) do if location.role==role then return location end end
    end
    for _,step in ipairs(authored) do
        if not step.travelQuestID then
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
                    end
                end
            end
            result[#result+1]=step
        end
    end
    guide.steps=result
    if guide.authoredSteps and not runtime then guide.authoredSteps=result end
end
