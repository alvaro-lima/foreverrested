# Alliance 20â€“30 regional visits

Use `/reload`, then `/fg guides` and choose **Levels 20â€“30**.

The eastern route alternates short visits:

| Planning band | Visit | Authored steps |
| --- | --- | --- |
| 20â€“22 | Wetlands coast and Greenwarden | 25 |
| 22â€“24 | Duskwood road and introductions | 46 |
| 24â€“25 | Wetlands gnolls and excavation | 16 |
| 25â€“26 | Duskwood Raven Hill investigations | 36 |
| 26â€“27 | Wetlands relics and coastal goods | 25 |
| 27â€“28 | Duskwood worgen and hermit | 19 |
| 28â€“29 | Wetlands shipwrecks and final raptors | 43 |
| 29â€“30 | Duskwood final patrols | 27 |

Ashenvale / Stonetalon is a separate linked alternative: 20â€“24 introductions,
24â€“27 eastern camps, and 27â€“30 cleansing / lake circuits.

Completing or skipping the last action automatically loads the next visit.
Manual browsing holds progression. Accepted objectives remain in the objective
queue across visits in the same route, with their section name shown when needed.
Explicit quest skips persist across handoffs. Automatic level catch-up is disabled
for these visits so an approximate level band cannot discard their quest chains.

The broad regional guides and provisional 20â€“25 / 25â€“30 chapters are retired from
the chooser. Retired regional definitions remain as internal circuit sources and
for progress migration. Existing positions migrate using stable quest action IDs;
missing positions recheck from the recommended visit. Saved skip choices survive.

Spoils of War and Alchemical Hazards have explicit optional actions in the first
Wetlands visit using sourced Forever identities, level requirements and locations.
Dropped-item, group and uncertain branches remain optional; no quest availability
is assumed from a level band alone. No third-party route instructions are bundled.

**Level bands remain provisional.** Prerequisite ordering, progression and handoffs
are tested, but these routes have not been field-tested or given a complete live XP
budget. There are no mandatory grind-to-level gates. Completing every visit is not
proof that the character reached 30; finish useful accepted work or select the
other regional route if under-level. Class detours and travel add character-specific
rows to the counts above.

## Class unlocks

Known class unlocks remain visible with key markers after completion or skipping. Available class detours appear near the entry of the route; the region chosen does not remove character unlocks.

Key quests with known destinations in another region include outbound and return travel checkpoints. `Travel.lua` supplies reviewed road, tram and boat connections; unknown connections use a clearly labelled destination checkpoint rather than invented transport instructions. These checkpoints retain key markers and do not increase the unique critical-quest count. Next confirms final arrival when no usable destination coordinate is available. Completed objectives bypass obsolete outbound journeys; turned-in quests bypass their journeys entirely. Entering the final zone alone does not prove arrival at its lake or NPC.

For the blue waterskin, follow the road to Menethil Harbor, take the Auberdine boat (the Forever quest describes an intermediate Southshore stop), then follow the road south to Astranaar. Fill the waterskin in Astranaar's water and return through Auberdine and Menethil to Hervdana. An already unlocked flight or appropriately placed hearthstone can replace a leg. Source: [blue waterskin stage](https://www.wowhead.com/forever/quest=94500/call-of-water).

At level 20, Dwarf Shamans gain the sourced Alliance **Call of Water** chain:

`94495 Ã¢â€ â€™ 94497 Ã¢â€ â€™ 94499 Ã¢â€ â€™ 94500 Ã¢â€ â€™ 94501 Ã¢â€ â€™ 94502 Ã¢â€ â€™ 94503 Ã¢â€ â€™ 94505`

It starts with Norric Lochthane in Loch Modan, visits Hervdana Saegrund in the Wetlands, collects water in Redridge and Ashenvale, returns to Loch Modan, visits Stendel's Pond in Westfall and returns for the Water Totem. Do not leave the Westfall shrine before speaking to the manifestation. Shared NPC map data inherits Horde locations for that spirit; those coordinates are omitted rather than used for Alliance navigation. Native quest waypoints can still direct that stage.

Sources: [Call of Water start](https://www.wowhead.com/forever/quest=94495/call-of-water), [Westfall shrine](https://www.wowhead.com/forever/quest=94503/call-of-water), [Water Totem reward](https://www.wowhead.com/forever/quest=94505/call-of-water).

## Sources and refresh

The new factual supplement contains 153 quest records, with individual source URLs, retrieval times and checksums in `alliance-20-30-reference.json`. Authored ordering stays in `Guides/Alliance_20_30.lua`. No source quest descriptions or third-party route ordering are bundled.

Sources: [Duskwood quest inventory](https://www.wowhead.com/forever/quests/eastern-kingdoms/duskwood), [Wetlands quest inventory](https://www.wowhead.com/forever/quests/eastern-kingdoms/wetlands), [Ashenvale quest inventory](https://www.wowhead.com/forever/quests/kalimdor/ashenvale), [Stonetalon quest inventory](https://www.wowhead.com/forever/quests/kalimdor/stonetalon-mountains). Acquisition dependencies also use the pinned Questie Vanilla baseline described in `QUEST_POLICY.md`; this is not proof that every Forever prerequisite is unchanged.

```powershell
python tools/build_20_30_reference.py --cache "$env:TEMP\ForeverRested-2030Research"
```

Add `--use-cache` for an offline rebuild. A failed fetch aborts before rewriting the loaded supplement. Rebuild the Classic policy with the documented pinned sources after adding quest IDs; its compiler also includes the 20Ã¢â‚¬â€œ30 supplement.

Optional quest branches use numbered Accept, Objective and Turn-in actions, not
Alongside bundles. Skipping a quest action skips its remaining actions and removes
its objectives from the queue. Advice remains in the action tooltip.

## Required XP progression correction

The introductory Ashenvale/Stonetalon chapter now includes Super Reaper 6000 as required local work and Aggressive Defense before optional city detours. Aggressive Defense keeps its stable action IDs and is removed from the next chapter; a level-23 safety check precedes its circuit. Required listed quest rewards increase from 19,155 to 22,755 XP, excluding optional and class-specific work. This does not guarantee the full level-24 requirement.

Mainland chapter bands describe quest circuits plus **Required XP recovery**, with actual level and live XP governing completion. Level-24 Ashenvale recovery uses Foulweald Warriors (23-24); earlier recovery retains Wrathtail Myrmidons (20-21). Final Ashenvale recovery uses Ghostpaw Alphas (27-28) instead of lower-level furbolgs. Optional XP is never assumed.

The all-chapter review is in [XP_PROGRESSION_AUDIT.md](XP_PROGRESSION_AUDIT.md). Recovery is explicitly skippable; skipping bypasses the intended level gate. Zephras 10+ retains its flexible exit. This correction supersedes earlier prose above stating that there are no mandatory grind-to-level gates.
