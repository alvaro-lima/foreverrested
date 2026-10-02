local _, F = ...
-- Vertical-slice fixtures, NOT a verified Forever route. Resolve these titles
-- from the live log, then fill empty slots with live quests. Persist IDs once
-- bound so accepting/removing other quests cannot retarget a guide step.
F.Guide = {
    id = "gnome-dwarf-slice-v1", title = "Dun Morogh - Test Guide",
    minLevel = 1, maxLevel = 10, races = {"Gnome", "Dwarf"}, status = "test",
    quests = {
        {title = "The Troll Cave", mob = "Frostmane Troll Whelp"},
        {title = "A Refugee's Quandary"},
        {title = "Bring Back the Mug"},
    },
    steps = {
        {id = "accept-first", type = "pickup", slot = 1, text = "Accept the first test quest."},
        {id = "objective-first", type = "objective", slot = 1, objective = 1, text = "Complete the first live objective."},
        {id = "turnin-first", type = "turnin", slot = 1, text = "Turn in the first test quest."},
        {id = "objective-second", type = "objective", slot = 2, objective = 1, text = "Complete the second live objective."},
        {id = "turnin-second", type = "turnin", slot = 2, text = "Turn in the second test quest."},
        {id = "objective-third", type = "objective", slot = 3, objective = 1, text = "Complete the third live objective."},
        {id = "turnin-third", type = "turnin", slot = 3, text = "Turn in the third test quest."},
        {id = "slice-end", type = "note", text = "Vertical slice finished. The full Forever route is not installed yet."},
    },
}
F.GuideLibrary:Register(F.Guide)
F.GuideLibrary:Register({
    id = "gnome-dwarf-concurrent-v1", title = "Dun Morogh - Concurrent Test",
    minLevel = 1, maxLevel = 10, races = {"Gnome", "Dwarf"}, status = "test",
    quests = F.Guide.quests,
    steps = {
        {id = "accept-tests", type = "group", text = "Pick up the three test quests", tasks = {
            {type = "pickup", slot = 1}, {type = "pickup", slot = 2}, {type = "pickup", slot = 3},
        }},
        {id = "concurrent-tests", type = "group", text = "Work on these quests together", tasks = {
            {type = "objective", slot = 1, objective = 1},
            {type = "objective", slot = 2, objective = 1},
        }, alongside = {
            {type = "objective", slot = 3, objective = 1, optional = true},
            {type = "objective", slot = 2, objective = 2, optional = true},
        }, note = "Side objectives are tracked here without holding up this step. These are test bindings, not a verified route."},
        {id = "finish-tests", type = "group", text = "Finish remaining objectives before returning", tasks = {
            {type = "objective", slot = 1}, {type = "objective", slot = 2}, {type = "objective", slot = 3},
        }},
        {id = "turnin-tests", type = "group", text = "Turn in the test quests", tasks = {
            {type = "turnin", slot = 1}, {type = "turnin", slot = 2}, {type = "turnin", slot = 3},
        }},
        {id = "concurrent-end", type = "note", text = "Vertical slice finished. The full Forever route is not installed yet."},
    },
})
