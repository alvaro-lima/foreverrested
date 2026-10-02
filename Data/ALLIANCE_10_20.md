# Alliance 10–20 drafts and Zephras exit choice

Use `/reload`, then the minimap book or `/fg guides`. Browse **Levels 10–20**:

| Guide | Main circuit |
| --- | --- |
| Westfall / Redridge 10–20 | northern farms → militia/Moonbrook → optional coastal work → Lakeshire hunts/lake/bridge |
| Loch Modan / Redridge 10–20 | south-gate trogg chain → Thelsamar wildlife → northern mine → eastern excavation/lodge → Lakeshire |
| Darkshore 10–20 | Auberdine/Bashal'Aran → Ameth'Aran → northern river/cave/crystal → Onu/glaive → Mathystra |
| Zephras 10–14 / Exit Choice | optional wind/tower/cult story → exit review → optional battle and hermit/refugee circuit |

Grouped objectives and batched hand-ins reduce repeated journeys. Beta additions, difficult named mobs, coastal diversions and dungeon work are optional where practical. The Defias investigation and lodge challenges can also be skipped if their travel/waiting cost is poor. Class training stops are manual city visits; the addon does not assume every regional hub has every class trainer.

Level checkpoints are readiness checks, not evidence that the preceding quests yield exactly that level. Finish useful nearby active quests when short of XP; use Skip to bypass an unwanted checkpoint or branch. Entering at 12–14 is supported through completed-quest reconciliation and manual Skip; the engine does not silently discard unaccepted quests based solely on your level. Full beta prerequisites and in-game timings still need acceptance.

## Zephras: leave at 10, 12 or 14?

There is no measured best exit level yet. The opening route now includes an exit-choice note near Valanaar, and the separate continuation has reviews at 10 and around 12. It never requires grinding to 14 merely to finish the island guide.

Finish your level-10 class unlock first. Check that Alliance transport is actually available: a story-gated departure changes the comparison. Stay for ready turn-ins and a compact nearby cluster; leave when remaining work becomes mostly travel, contention, difficult events or low-value errands. Useful equipment can justify a detour, but the current estimate does not score upgrades.

The illustrative comparison uses sourced listed quest XP plus explicit assumed kill XP and time. It compares three exit policies against the **same 30,000-XP evaluation budget**, not XP required to reach level 14:

| Policy | Normal assumptions | Slower assumptions |
| --- | ---: | ---: |
| Leave now | 144.4 minutes | 215.0 minutes |
| Finish first cluster, then leave | 141.0 minutes | 218.7 minutes |
| Finish both island clusters, then leave | 143.8 minutes | 232.1 minutes |

Normal assumptions: mainland 220 XP/minute, 8-minute transition, first island cluster 35 minutes, later cluster 55 minutes. Slower assumptions: mainland 150 XP/minute, 15-minute transition, island clusters 60/90 minutes. Transition is counted once for each policy. Kill counts/XP and quest reward scaling are assumptions, not measurements. No resting/group bonus or upgrade benefit is silently added.

The small normal-case difference reverses in the slow case, so **do not call level 12 optimal**. First-cluster break-even is about 241 XP/minute; the later cluster is about 209 under these assumptions. Actual speed, completed quests, class, gear and transport availability determine whether staying pays. Reviews at 10/12/14 do not predict the level reached by a cluster.

Edit `Data/zephras-comparison-input.json` to try your own times/mainland rate/reward factor, then run:

```powershell
python tools/compare_zephras.py
```

`Data/ZEPHRAS_COMPARISON.json` records the assumptions and results. This offline tool does not auto-switch guides. Missing XP prevents ranking; repeated quest rewards are rejected.

## Sources and refresh

The reference now contains 554 selected records. 90 use zone-list summaries because individual pages were unavailable during this build: those records explicitly lack locations and reward stats. Native quest waypoints and live counts remain usable; the addon does not fabricate fallback coordinates. Summary records show sourced listed XP, not build-verified XP.

Use the refresh workflow in [ALLIANCE_DRAFTS.md](ALLIANCE_DRAFTS.md). `-UseCache` rebuilds available cached pages and summaries without network requests. A normal refresh tries individual pages and stops on a failed fetch, leaving the loaded reference unchanged. Newly available individual pages replace summaries on a later rebuild. Route ordering remains authored separately.

Sources: public Forever [Westfall](https://www.wowhead.com/forever/quests/eastern-kingdoms/westfall), [Loch Modan](https://www.wowhead.com/forever/quests/eastern-kingdoms/loch-modan), [Darkshore](https://www.wowhead.com/forever/quests/kalimdor/darkshore), [Redridge](https://www.wowhead.com/forever/quests/eastern-kingdoms/redridge-mountains), [Zephras](https://www.wowhead.com/forever/zone=16593/zephras-isle) lists and individual cached quest/item records. Chain ordering was cross-checked against QuestieDB's raw quest fields and authored Forever corrections at `cac1eff815923f896d082764d023cf812454a023`; no QuestieDB payload or runtime dependency was bundled.

Automated checks cover Lua 5.1 loading, IDs, faction/class filtering, level/manual checkpoints, per-guide saves, live objective changes, native navigation with missing reference coordinates, combat safeguards and estimate arithmetic. They do not establish a fastest route or in-game availability. The 20–30 guides remain unbuilt.
