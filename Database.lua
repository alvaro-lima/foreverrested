local _, F = ...
function F.LoadDatabase()
    ForeverRestedDB = type(ForeverRestedDB) == "table" and ForeverRestedDB or {}
    F.db = ForeverRestedDB
    local d = F.db
    d.version = 3
    d.step = tonumber(d.step) or 1
    d.completed = type(d.completed) == "table" and d.completed or {}
    d.bindings = type(d.bindings) == "table" and d.bindings or {}
    d.skipped = type(d.skipped) == "table" and d.skipped or {}
    d.knownFlightPaths = type(d.knownFlightPaths) == "table" and d.knownFlightPaths or {}
    d.flightPathLocations = type(d.flightPathLocations) == "table" and d.flightPathLocations or {}
    d.fontSize = F.Number(d.fontSize) and math.max(11, math.min(20, math.floor(d.fontSize))) or 12
    if not d.fontDefault12 then
        if d.fontSize == 14 then d.fontSize = 12 end
        d.fontDefault12 = true
    end
    d.arrowSize = F.Number(d.arrowSize) and math.max(24, math.min(96, math.floor(d.arrowSize))) or 48
    d.mapStepLimit = F.Number(d.mapStepLimit) and math.max(1, math.min(100, math.floor(d.mapStepLimit))) or 10
    d.positionsLocked = d.positionsLocked == true
    F.GuideLibrary:Initialize()
    F.QuestData:Initialize()
end
