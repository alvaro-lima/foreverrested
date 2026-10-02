# Alliance 20–30 guides

Use `/reload`, then `/fg guides` and choose **Levels 20–30**.

| Guide | Circuit |
| --- | --- |
| Duskwood / Redridge | Optional Lakeshire cleanup, Darkshire, western road wildlife, Raven Hill deliveries, Night Watch, worgen and ogres |
| Wetlands | Dun Algaz or boat arrival, Menethil coast, Greenwarden, Whelgar's excavation, coastal hovels and shipwrecks |
| Ashenvale / Stonetalon | Astranaar, northern cure chain, Zoram Strand, Stonetalon introductions and local work, eastern Ashenvale and Raene's Cleansing |

These are independently authored regional circuits using sourced quest identities, rewards and approximate representative locations. They have not been walked or timed in the Forever beta. Level checkpoints check readiness; the routes do not guarantee enough quest XP to reach 30 without additional accepted quests, optional work or suitable nearby mobs. All guides remain selectable regardless of starting race.

Group quests, escorts, long city-delivery branches and higher-level camps are optional notes with alongside tasks. Next confirms the note and continues. Check an offered quest's preceding turn-in and your level before using Skip for unavailable or dangerous work. Live objective counts and client waypoints take priority.

## Class unlocks

Known class unlocks remain visible with key markers after completion or skipping. Available class detours appear near the entry of the route; the region chosen does not remove character unlocks.

Key quests with known destinations in another region include outbound and return travel checkpoints. `Travel.lua` supplies reviewed road, tram and boat connections; unknown connections use a clearly labelled destination checkpoint rather than invented transport instructions. These checkpoints retain key markers and do not increase the unique critical-quest count. Next confirms final arrival when no usable destination coordinate is available. Completed objectives bypass obsolete outbound journeys; turned-in quests bypass their journeys entirely. Entering the final zone alone does not prove arrival at its lake or NPC.

For the blue waterskin, follow the road to Menethil Harbor, take the Auberdine boat (the Forever quest describes an intermediate Southshore stop), then follow the road south to Astranaar. Fill the waterskin in Astranaar's water and return through Auberdine and Menethil to Hervdana. An already unlocked flight or appropriately placed hearthstone can replace a leg. Source: [blue waterskin stage](https://www.wowhead.com/forever/quest=94500/call-of-water).

At level 20, Dwarf Shamans gain the sourced Alliance **Call of Water** chain:

`94495 → 94497 → 94499 → 94500 → 94501 → 94502 → 94503 → 94505`

It starts with Norric Lochthane in Loch Modan, visits Hervdana Saegrund in the Wetlands, collects water in Redridge and Ashenvale, returns to Loch Modan, visits Stendel's Pond in Westfall and returns for the Water Totem. Do not leave the Westfall shrine before speaking to the manifestation. Shared NPC map data inherits Horde locations for that spirit; those coordinates are omitted rather than used for Alliance navigation. Native quest waypoints can still direct that stage.

Sources: [Call of Water start](https://www.wowhead.com/forever/quest=94495/call-of-water), [Westfall shrine](https://www.wowhead.com/forever/quest=94503/call-of-water), [Water Totem reward](https://www.wowhead.com/forever/quest=94505/call-of-water).

## Sources and refresh

The new factual supplement contains 153 quest records, with individual source URLs, retrieval times and checksums in `alliance-20-30-reference.json`. Authored ordering stays in `Guides/Alliance_20_30.lua`. No source quest descriptions or third-party route ordering are bundled.

Sources: [Duskwood quest inventory](https://www.wowhead.com/forever/quests/eastern-kingdoms/duskwood), [Wetlands quest inventory](https://www.wowhead.com/forever/quests/eastern-kingdoms/wetlands), [Ashenvale quest inventory](https://www.wowhead.com/forever/quests/kalimdor/ashenvale), [Stonetalon quest inventory](https://www.wowhead.com/forever/quests/kalimdor/stonetalon-mountains). Acquisition dependencies also use the pinned Questie Vanilla baseline described in `QUEST_POLICY.md`; this is not proof that every Forever prerequisite is unchanged.

```powershell
python tools/build_20_30_reference.py --cache "$env:TEMP\ForeverRested-2030Research"
```

Add `--use-cache` for an offline rebuild. A failed fetch aborts before rewriting the loaded supplement. Rebuild the Classic policy with the documented pinned sources after adding quest IDs; its compiler also includes the 20–30 supplement.
