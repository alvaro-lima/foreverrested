local _, F = ...
-- Reviewed Forever changes belong here, separate from generated Vanilla facts.
-- Each replacement should cite its source and client build in QUEST_POLICY.md.
-- records[id] = false disables that baseline quest as an unlock alternative.
-- unlocks[key] = false disables a Vanilla milestone; a table replaces it.
F.ForeverQuestPolicy = {records = {}, unlocks = {
    ["forever-shaman-earth"] = {class="SHAMAN",races=0,level=4,terminals={94375},reason="Earth Totem"},
    ["forever-shaman-fire"] = {class="SHAMAN",races=0,level=10,terminals={94468},reason="Fire Totem"},
    ["forever-shaman-water"] = {class="SHAMAN",races=4,level=20,terminals={94505},reason="Water Totem"},
}}
-- Public Forever quest pages list these core chains. The level-10 Earth
-- breadcrumb and replacement Sapta errand are not required unlock steps.
for _, chain in ipairs({{94373,94374,94375},{94449,94465,94466,94467,94468}}) do
    for index,id in ipairs(chain) do
        F.ForeverQuestPolicy.records[id] = {classes={"SHAMAN"},requiredRaces=0,critical=true,
            reason=chain[1]==94373 and 'Earth Totem' or 'Fire Totem',
            minLevel=chain[1]==94373 and 4 or 10,
            prerequisites=index>1 and {chain[index-1]} or {}}
    end
end
-- Alliance Water Totem series, checked against public Forever quest pages.
for index,id in ipairs({94495,94497,94499,94500,94501,94502,94503,94505}) do
    local chain={94495,94497,94499,94500,94501,94502,94503,94505}
    F.ForeverQuestPolicy.records[id]={classes={"SHAMAN"},requiredRaces=4,critical=true,
        reason="Water Totem",minLevel=20,prerequisites=index>1 and {chain[index-1]} or {}}
end
