local _, F = ...
local D = {}
F.GuideDraft = D
D.classAdvice = {
    WARRIOR = "Compare usable weapon damage first; a weapon upgrade can shorten every fight. At 10 check your warrior trainer's quest.",
    PALADIN = "Compare usable weapon damage and survivability. Train new abilities here; check trainer quests as they become available.",
    HUNTER = "Compare your ranged weapon and keep ammunition supplied. At 10 prioritize your trainer's pet-taming chain.",
    ROGUE = "Compare usable main-hand damage and dagger requirements. At 10 check your rogue trainer's quest.",
    PRIEST = "A usable wand helps reduce downtime. Check level-5 and level-10 trainer quests/spells; compare intellect, spirit and stamina.",
    MAGE = "A usable wand helps between casts. Compare intellect, spirit and stamina; at 10 check your trainer's quests.",
    WARLOCK = "Prioritize your early demon quest when offered. A usable wand helps; at 10 check your trainer for the next demon chain.",
    DRUID = "Compare stats useful for your current form. At 10 prioritize your trainer's form quest before continuing the leveling route.",
    SHAMAN = "Prioritize totem-unlocking quests offered by your trainer. Compare usable weapons and stats for your current attacks.",
}
function D:Advice()
    local _, class = F.Call(UnitClass, "player")
    return self.classAdvice[class] or "Train abilities for your class and compare usable rewards with your current equipment."
end
function D:Task(kind, id, optional)
    local data = F.AllianceQuestData[id]
    assert(data, "Missing quest reference " .. tostring(id))
    return {type = kind, questID = id, optional = optional or nil,
        activeOnly = optional and kind ~= "pickup" or nil,
        classes = #data.classes > 0 and data.classes or nil,
        requiredRaces = data.requiredRaces, minLevel = optional and data.minLevel or nil}
end
function D:Group(guide, key, label, kind, ids, side, note)
    local tasks, alongside = {}, {}
    for _, id in ipairs(ids) do tasks[#tasks + 1] = self:Task(kind, id) end
    for _, id in ipairs(side or {}) do alongside[#alongside + 1] = self:Task(kind, id, true) end
    guide.steps[#guide.steps + 1] = {id = key, type = "group", text = label, tasks = tasks,
        alongside = alongside, note = note}
end
function D:Trainer(guide, key, label, zone, x, y, maxLevel)
    guide.lastTrainer = {zone=zone, x=x, y=y}
    local alongside = {}
    local ids = {}
    for id, data in pairs(F.AllianceQuestData) do
        if #data.classes > 0 and data.side ~= 2 and (data.minLevel or 99) <= maxLevel then
            for _, point in ipairs(data.locations) do
                if point.role == "start" and point.zone == zone and (point.x-x)^2 + (point.y-y)^2 <= .06^2 then
                    ids[#ids + 1] = id; break
                end
            end
        end
    end
    table.sort(ids)
    for _, id in ipairs(ids) do
        alongside[#alongside + 1] = self:Task("pickup", id, true)
        alongside[#alongside + 1] = self:Task("objective", id, true)
        alongside[#alongside + 1] = self:Task("turnin", id, true)
    end
    guide.steps[#guide.steps + 1] = {id = key, type = "trainer", text = label,
        classAdvice = true, confirmOnNext = true, zone = zone, x = x, y = y,
        alongside = alongside, note = "Take only the quests your trainer actually offers. Next confirms this stop; unavailable side quests do not block the route."}
end
function D:Note(guide, key, label, note)
    guide.steps[#guide.steps + 1] = {id = key, type = "note", text = label, note = note, confirmOnNext = true}
end
function D:New(id, title, zone, races, minLevel, maxLevel)
    return {id = id, title = title, minLevel = minLevel or 1, maxLevel = maxLevel or 10, faction = "Alliance", races = races,
        zone = zone, status = "draft", revision = 1, quests = {}, questData = F.AllianceQuestData,
        steps = {}, description = "Approximate beta route: nearby objectives, batched turn-ins, optional reward detours."}
end
function D:Finish(guide, key, continuation)
    local target = guide.targetLevel or guide.maxLevel
    guide.steps[#guide.steps + 1] = {id = key .. "-level" .. target, type = "grind", targetLevel = target,
        text = "Reach level " .. target .. " before leaving this section", note = "Finish nearby active quests or fight suitable mobs along your route. This checkpoint completes automatically at the indicated level."}
    local hub = guide.lastTrainer
    if hub then self:Trainer(guide, key .. "-class" .. target, "Level " .. target .. " class checkpoint", hub.zone, hub.x, hub.y, target) end
    self:Note(guide, key .. "-finish", guide.minLevel .. "-" .. target .. " guide finished", continuation .. " Finish useful active quests before leaving; choose your next section from the minimap book.")
    F.GuideLibrary:Register(guide)
end
function D:Checkpoint(guide, key, target, note)
    guide.steps[#guide.steps + 1] = {id=key, type="grind", targetLevel=target,
        text="Level " .. target .. " checkpoint", note=note}
end
function D:ClassStop(guide, key, note)
    self:Note(guide,key,"Class training and supplies",note)
    guide.steps[#guide.steps].classAdvice = true
end
