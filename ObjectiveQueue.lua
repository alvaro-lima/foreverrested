local _, F = ...
local Q = {}
F.ObjectiveQueue = Q

function Q:Build()
    local skipped, steps = {}, {}
    local guides={F.Guide}
    local sections={}
    for _,guide in ipairs(guides) do
    local saved=guide==F.Guide and F.db or F.db.guides[guide.id] or {}
    for index, step in ipairs(guide.steps) do
        for _, task in ipairs(F.GuideEngine:Tasks(step)) do
            local id = F.GuideEngine:Resolve(task)
            if id and task.type=='objective' then
                steps[id]=steps[id] or {}
                local key=task.objective or 0
                if not steps[id][key] then
                    steps[id][key]=index
                    sections[id]=sections[id] or {}
                    sections[id][key]=guide==F.Guide and false or guide.title
                end
            end
            -- Automatic catch-up skips and optional travel do not skip a quest.
            if id and task.type ~= 'travel' and
                (saved.manualSkippedSteps and saved.manualSkippedSteps[step.id]) then skipped[id] = true end
        end
    end
    end
    local entries = {}
    for _, quest in ipairs(F.QuestLog.list) do
        if not skipped[quest.id] and not quest.failed and not quest.complete
            and not F.QuestLog:TurnedIn(quest.id) then
            for index, objective in ipairs(quest.objectives) do
                local stepIndex=steps[quest.id] and (steps[quest.id][index] or steps[quest.id][0])
                if stepIndex and not objective.finished then
                    entries[#entries + 1] = {questID=quest.id, questTitle=quest.title,
                        objectiveIndex=index, stepIndex=stepIndex,
                        section=sections[quest.id] and (sections[quest.id][index] or sections[quest.id][0]) or F.Guide.title,
                        zone=self:ObjectiveZone(quest,objective,index),
                        text=objective.text or F.QuestLog:Progress(objective)}
                end
            end
        end
    end
    return entries
end

function Q:ObjectiveZone(quest,objective,index)
    local record=F.GuideEngine:TargetRecord(quest)
    for _,source in ipairs(record and record.objectives or {}) do
        if source.index==index and source.location and source.location.zone then return source.location.zone end
    end
    local data=F.GuideEngine:Metadata(quest.id) or {}
    local zones={}
    for _,point in ipairs(data.locations or {}) do
        if point.role=='requirement' or point.role=='sourcerequirement' then
            if point.item and (objective.text or ''):find(point.item,1,true) then return point.zone end
            if point.zone then zones[point.zone]=true end
        end
    end
    local zone,count=nil,0
    for name in pairs(zones) do zone=name;count=count+1 end
    if count==1 then return zone end
    if count>1 then return 'Multiple areas' end
    if record and record.location and record.location.zone then return record.location.zone end
    -- A quest-wide waypoint is unambiguous only for a single remaining objective.
    local remaining=0
    for _,pending in ipairs(quest.objectives or {}) do
        if not pending.finished then remaining=remaining+1 end
    end
    if remaining==1 then
        local map=F.Navigation:ClientWaypoint({type='objective',id='objective-zone:'..quest.id},quest.id)
        local info=map and F.Call(C_Map and C_Map.GetMapInfo,map)
        if info and info.name then return info.name end
    end
    return 'Location unknown'
end

function Q:Create()
    if self.frame then return end
    local frame = F.UI:Panel(F.UI.frame, 300, 520, 'outer')
    self.frame = frame
    self.button=F.UI.footerButtons[6]
    F.Tooltips:Text(self.button,'Objectives','Show or hide your unfinished quest objectives.',true)
    frame:SetPoint('TOPLEFT', F.UI.frame, 'TOPRIGHT', 8, 0)
    frame:SetPoint('BOTTOMLEFT', F.UI.frame, 'BOTTOMRIGHT', 8, 0)
    frame:SetScript('OnSizeChanged',function() if self.entries then self:Refresh() end end)
    local scroll = CreateFrame('ScrollFrame', nil, frame)
    self.scroll = scroll
    scroll:SetPoint('TOPLEFT', 14, -14)
    scroll:SetPoint('BOTTOMRIGHT', -14, 14)
    local content = CreateFrame('Frame', nil, scroll)
    content:SetWidth(272)
    self.content = content
    scroll:SetScrollChild(content)
    self.rows={}
    local bar=CreateFrame('Slider',nil,frame)
    self.scrollbar=bar
    bar:SetPoint('TOPRIGHT',-9,-14);bar:SetPoint('BOTTOMRIGHT',-9,14);bar:SetWidth(14)
    bar:SetOrientation('VERTICAL');bar:SetValueStep(1);bar:SetMinMaxValues(0,0)
    local rail=bar:CreateTexture(nil,'BACKGROUND');rail:SetAllPoints();rail:SetColorTexture(.18,.13,.06,.9)
    local thumb=bar:CreateTexture(nil,'ARTWORK');thumb:SetTexture('Interface\\Buttons\\UI-ScrollBar-Knob');thumb:SetSize(14,28)
    bar:SetThumbTexture(thumb)
    bar:SetScript('OnValueChanged',function(_,value) self:SetOffset(value,true) end)
    scroll:SetScript('OnSizeChanged',function() if self.entries then self:Refresh() end end)
    scroll:EnableMouseWheel(true)
    scroll:SetScript('OnMouseWheel', function(_, delta)
        self:SetOffset((self.offset or 0)-delta*36)
    end)
    self.otherScroll=CreateFrame('ScrollFrame',nil,frame)
    self.otherContent=CreateFrame('Frame',nil,self.otherScroll)
    self.otherContent:SetWidth(250);self.otherScroll:SetScrollChild(self.otherContent)
    self.otherScrollbar=CreateFrame('Slider',nil,frame)
    self.otherScrollbar:SetWidth(14);self.otherScrollbar:SetOrientation('VERTICAL');self.otherScrollbar:SetValueStep(1)
    local otherThumb=self.otherScrollbar:CreateTexture(nil,'ARTWORK')
    otherThumb:SetTexture('Interface\\Buttons\\UI-ScrollBar-Knob');otherThumb:SetSize(14,28)
    self.otherScrollbar:SetThumbTexture(otherThumb)
    self.otherScrollbar:SetScript('OnValueChanged',function(_,value) self:SetOffset(value,true,'other') end)
    self.otherScroll:EnableMouseWheel(true)
    self.otherScroll:SetScript('OnMouseWheel',function(_,delta) self:SetOffset((self.otherOffset or 0)-delta*36,false,'other') end)
end

function Q:SetOffset(value,fromBar,area)
    if area=='other' then
        self.otherOffset=math.max(0,math.min(self.otherMaxOffset or 0,value or 0))
        self.otherScroll:SetVerticalScroll(self.otherOffset)
        if not fromBar then self.otherScrollbar:SetValue(self.otherOffset) end
        return
    end
    self.offset=math.max(0,math.min(self.maxOffset or 0,value or 0))
    self.scroll:SetVerticalScroll(self.offset)
    if not fromBar then self.scrollbar:SetValue(self.offset) end
end

function Q:DisplayRows(entries)
    local active=F.Guide.steps[F.db.step]
    local currentIDs={}
    for _,task in ipairs(F.GuideEngine:Tasks(active)) do
        local id=task.travelAction=='objective' and task.travelQuestID
            or task.type=='objective' and F.GuideEngine:Resolve(task)
        if id then currentIDs[id]=task.objective or 0 end
    end
    local first
    for _,entry in ipairs(entries) do
        if entry.stepIndex>=F.db.step and (not first or entry.stepIndex<first) then first=entry.stepIndex end
    end
    local explicit=false
    for _,entry in ipairs(entries) do
        local objective=currentIDs[entry.questID]
        if objective~=nil and (objective==0 or objective==entry.objectiveIndex) then explicit=true end
    end
    local nearby,remote={},{}
    local count,seen=0,{}
    local ordered={};for _,entry in ipairs(entries) do ordered[#ordered+1]=entry end
    table.sort(ordered,function(a,b)
        if a.stepIndex~=b.stepIndex then return a.stepIndex<b.stepIndex end
        if a.questID~=b.questID then return a.questID<b.questID end
        return a.objectiveIndex<b.objectiveIndex
    end)
    for _,entry in ipairs(ordered) do
        local objective=currentIDs[entry.questID]
        local current=explicit and objective~=nil and (objective==0 or objective==entry.objectiveIndex)
            or not explicit and entry.stepIndex==first
        if current then nearby[#nearby+1]=entry
        else
            remote[#remote+1]=entry
            if not seen[entry.questID] then seen[entry.questID]=true;count=count+1 end
        end
    end
    local result={}
    local function quests(list)
        local groups,order={},{}
        for _,entry in ipairs(list) do
            if not groups[entry.questID] then groups[entry.questID]={};order[#order+1]=entry.questID end
            groups[entry.questID][#groups[entry.questID]+1]=entry
        end
        for _,id in ipairs(order) do
            local group=groups[id];local steps,labels={},{}
            for _,entry in ipairs(group) do steps[entry.stepIndex]=true end
            for number in pairs(steps) do labels[#labels+1]=number end
            table.sort(labels)
            for i,number in ipairs(labels) do labels[i]=tostring(number) end
            local zones,zoneLabels={},{}
            for _,entry in ipairs(group) do
                if not zones[entry.zone] then zones[entry.zone]=true;zoneLabels[#zoneLabels+1]=entry.zone end
            end
            local lines={'|cffffd100['..table.concat(labels,', ')..'] '..group[1].questTitle..'|r |cff999999'..table.concat(zoneLabels,', ')..'|r'}
            for _,entry in ipairs(group) do lines[#lines+1]='|cffbfb59a  • '..entry.text..'|r' end
            result[#result+1]={text=table.concat(lines,'\n'),entries=group}
        end
    end
    result[#result+1]={text='|cffffd100Current objectives|r',header=true,toggle='current',expanded=not self.currentZoneCollapsed}
    if not self.currentZoneCollapsed then
        quests(nearby)
        if #nearby==0 then result[#result+1]={text='|cffbfb59aNo current objectives.|r'} end
    end
    if count>0 then
        result[#result+1]={text='|cffffd100Upcoming objectives ('..count..' quests)|r',header=true,toggle='other',expanded=self.otherAreasExpanded}
        if self.otherAreasExpanded then
            quests(remote)
        end
    end
    return result
end

function Q:Refresh()
    if self.refreshing then return end
    self.refreshing=true
    self:Create()
    self.entries = self:Build()
    local hasObjectives=#self.entries>0
    self.button:SetEnabled(hasObjectives)
    -- Disabled native buttons need explicit motion scripts to show help.
    if self.button.SetMotionScriptsWhileDisabled then self.button:SetMotionScriptsWhileDisabled(true) end
    F.Tooltips:Text(self.button,'Objectives',hasObjectives and
        'Show or hide your unfinished quest objectives.' or 'No objectives to track.',true)
    self.frame:SetShown(not F.db.objectivesHidden and #self.entries>0)
    local display=self:DisplayRows(self.entries)
    local width=250
    self.content:SetWidth(width)
    self.scroll:SetPoint('BOTTOMRIGHT',-32,14)
    local heights,lines={current=0,other=0},{}
    local area,headers='current',{}
    for index,item in ipairs(display) do
        local row=self.rows[index]
        if not row then
            row=CreateFrame('Button',nil,self.content)
            row:EnableMouseWheel(true)
            row:SetScript('OnMouseWheel',function(button,delta)
                local offset=button.area=='other' and self.otherOffset or self.offset
                self:SetOffset((offset or 0)-delta*36,false,button.area)
            end)
            row.label=F.UI:Text(row,'GameFontNormal','TOPLEFT',0,0,width)
            row.sectionBar=F.Frame('Frame',nil,row,'BackdropTemplate');row.sectionBar:SetAllPoints()
            row.sectionBar:SetFrameLevel(row:GetFrameLevel())
            row.sectionBar:SetBackdrop({edgeFile='Interface\\Tooltips\\UI-Tooltip-Border',edgeSize=8,
                insets={left=3,right=3,top=3,bottom=3}})
            row.sectionBar:SetBackdropBorderColor(.46,.36,.20,.9)
            local background=row.sectionBar:CreateTexture(nil,'BACKGROUND')
            background:SetPoint('TOPLEFT',3,-3);background:SetPoint('BOTTOMRIGHT',-3,3)
            background:SetTexture('Interface\\QuestFrame\\UI-QuestLogTitleHighlight')
            background:SetVertexColor(.34,.25,.13,.7)
            row.label:SetDrawLayer('OVERLAY')
            row.sign=F.UI:Text(row,'GameFontNormal','TOPRIGHT',-9,-6,16)
            row:SetScript('OnClick',function(button)
                if button.item.toggle=='current' then self.currentZoneCollapsed=not self.currentZoneCollapsed;self:Refresh()
                elseif button.item.toggle=='other' then self.otherAreasExpanded=not self.otherAreasExpanded;self:Refresh() end
            end)
            F.Tooltips:Attach(row,function(button)
                if not GameTooltip then return end
                GameTooltip:SetOwner(button,'ANCHOR_RIGHT')
                local data=button.item
                F.Tooltips:QuestHeader(button,data.toggle=='current' and 'Current objectives' or data.toggle and 'Upcoming objectives' or data.entries and data.entries[1].questTitle or 'Objective area',data.entries and data.entries[1].stepIndex)
                if data.toggle then GameTooltip:AddLine('Click to expand or collapse this section. Objectives follow this guide\'s step order.',1,1,1,true)
                else
                    local sections={}
                    for _,entry in ipairs(data.entries or {}) do
                        if entry.section and not sections[entry.section] then
                            sections[entry.section]=true;GameTooltip:AddLine(entry.section,.72,.68,.58,true)
                        end
                    end
                    if data.entries then
                        GameTooltip:AddLine('Location: '..data.entries[1].zone,.72,.68,.58,true)
                        GameTooltip:AddLine(' ')
                        for _,entry in ipairs(data.entries) do F.Tooltips:QuestObjective(entry.text,false) end
                    end
                end
                GameTooltip:Show()
            end,true)
            self.rows[index]=row
        end
        if item.header then area=item.toggle=='other' and 'other' or 'current';headers[area]=row end
        row.area=area;row.item=item;row:ClearAllPoints()
        row:SetParent(item.header and self.frame or area=='other' and self.otherContent or self.content)
        row.sectionBar:SetFrameLevel(row:GetFrameLevel())
        if not item.header then row:SetPoint('TOPLEFT',6,-heights[area]) end
        row:SetWidth(item.header and 272 or width)
        row.sectionBar:SetShown(item.header==true);row.sign:SetShown(item.header==true)
        row.sign:SetText(item.expanded and '−' or '+')
        row.label:ClearAllPoints();row.label:SetPoint('TOPLEFT',item.header and 9 or 0,item.header and -6 or 0)
        row.label:SetWidth(item.header and 235 or width)
        local text=item.header and item.text:gsub('|cffffd100','|cffd5c48a') or item.text
        row.label:SetText(text);row.label:SetHeight(0)
        local measured=F.Call(row.label.GetStringHeight,row.label)
        local _,breaks=item.text:gsub('\n','')
        local rowHeight=F.Number(measured) and measured>0 and measured or (breaks+1)*((F.db.fontSize or 12)+4)
        if item.header then rowHeight=26 end
        row:SetHeight(rowHeight);row:Show()
        if not item.header then heights[area]=heights[area]+rowHeight+10 end
        lines[#lines+1]=item.text
    end
    for index=#display+1,#self.rows do self.rows[index]:Hide() end
    self.renderedText=table.concat(lines,'\n')
    local available=math.max(0,self.frame:GetHeight()-28-32-(headers.other and 38 or 0))
    local currentOpen=not self.currentZoneCollapsed
    local otherOpen=headers.other and self.otherAreasExpanded
    local currentHeight=currentOpen and math.min(heights.current,otherOpen and math.floor(available*.5) or available) or 0
    local otherHeight=otherOpen and math.min(heights.other,available-currentHeight) or 0
    if currentOpen then currentHeight=math.min(heights.current,available-otherHeight) end
    headers.current:SetPoint('TOPLEFT',14,-14)
    if headers.other then headers.other:SetPoint('TOPLEFT',14,-52-currentHeight) end
    self.scroll:ClearAllPoints();self.scroll:SetPoint('TOPLEFT',self.frame,'TOPLEFT',14,-46)
    self.scroll:SetSize(width,math.max(1,currentHeight));self.scroll:SetShown(currentOpen)
    self.otherScroll:ClearAllPoints();self.otherScroll:SetPoint('TOPLEFT',self.frame,'TOPLEFT',14,-84-currentHeight)
    self.otherScroll:SetSize(width,math.max(1,otherHeight));self.otherScroll:SetShown(otherOpen==true)
    self.scrollbar:ClearAllPoints();self.scrollbar:SetPoint('TOPLEFT',self.scroll,'TOPRIGHT',8,0)
    self.scrollbar:SetPoint('BOTTOMLEFT',self.scroll,'BOTTOMRIGHT',8,0)
    self.otherScrollbar:ClearAllPoints();self.otherScrollbar:SetPoint('TOPLEFT',self.otherScroll,'TOPRIGHT',8,0)
    self.otherScrollbar:SetPoint('BOTTOMLEFT',self.otherScroll,'BOTTOMRIGHT',8,0)
    self.content:SetHeight(math.max(1,heights.current));self.otherContent:SetHeight(math.max(1,heights.other))
    self.maxOffset = math.max(0, heights.current - currentHeight)
    self.otherMaxOffset=math.max(0,heights.other-otherHeight)
    self.scrollbar:SetMinMaxValues(0,self.maxOffset)
    self.scrollbar:SetShown(currentOpen and self.maxOffset>0)
    self.otherScrollbar:SetMinMaxValues(0,self.otherMaxOffset)
    self.otherScrollbar:SetShown(otherOpen==true and self.otherMaxOffset>0)
    self:SetOffset(self.offset or 0)
    self:SetOffset(self.otherOffset or 0,false,'other')
    self.refreshing=nil
end
