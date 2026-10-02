local _, F = ...
-- Explicit loot-source mappings belong in data, not UI or inferred item names.
-- Verified 2026-10-01 against Forever quest 95212 and item 267414:
-- https://www.wowhead.com/forever/quest=95212/never-saddle-on-quality
-- https://www.wowhead.com/forever/item=267414/pristine-leopard-pelt
F.QuestTargets = {
    [95212] = {
        title = "Never Saddle on Quality",
        -- Approximate hunting area, not the exact position of a moving creature.
        -- Public route reference and installed Forever route agree on this point:
        -- https://www.foreverwisp.com/guides/wow-forever-dwarf-gnome-leveling-guide
        location = {mapID = 1426, zone = "Dun Morogh", x = .764, y = .614,
            label = "Elder Snow Leopard hunting area", approximate = true},
        objectives = {
            {index = 1, itemID = 267414, item = "Pristine Leopard Pelt", mob = "Elder Snow Leopard"},
        },
    },
}
