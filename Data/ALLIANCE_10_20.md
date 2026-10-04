# Alliance 10–20 guides and Zephras exit choice

Use `/reload`, then the minimap book or `/fg guides`. Browse **Levels 10–20**:

| Route | Linked sections (authored step counts) |
| --- | --- |
| Westfall / Redridge | 10–12 farms/first militia (45) → 12–15 militia/Defias (38) → 15–20 Redridge (40) |
| Loch Modan / Redridge | 10–13 western shore (49) → 13–15 excavation/lodge (40) → 15–20 Redridge (40) |
| Darkshore | 10–13 coast/ruins (54) → 13–17 northern circuits (48) → 17–20 final work (35) |
| Zephras continuation | 10+ service/wind (23) → 10+ tower/village (52) → 10+ optional work/exit (17) → Westfall |

The addon automatically opens the next section when the current one is finished. The mainland routes then link into the [20–30 regional visits](ALLIANCE_20_30.md). Accepted objectives persist across linked sections in the Objectives panel. Optional collection/objective/delivery actions have their own rows and can be skipped. Class training stops are manual city visits; the addon does not assume every regional hub has every class trainer. Counts exclude runtime class-unlock and travel actions.

The [10–20 audit](10_20_AUDIT.md) refreshed all 147 authored quests from Forever pages and reviewed 159 NPC/item pages. Optional and class-specific XP are excluded from the baseline. Level bands still do not establish that quests alone fill them: the nine mainland sections now use sourced local recovery steps before level gaps and at their handoffs. These check actual level and display live XP; use Skip to bypass an unwanted branch. Zephras remains an optional 10+ continuation, with no forced grind to 12 or 14. Entering at 12–14 is supported through completed-quest reconciliation and manual Skip; the engine does not silently discard unaccepted quests based solely on your level. Full beta prerequisites and in-game timings still need acceptance.

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

The reference now contains 558 selected records. Some records outside the reviewed 1–20 chapters still use zone-list summaries because individual pages were unavailable during the original build; those records explicitly lack locations and reward stats. Native quest waypoints and live counts remain usable; the addon does not fabricate fallback coordinates. Summary records show sourced listed XP, not build-verified XP.

Use the refresh workflow in [ALLIANCE_GUIDES.md](ALLIANCE_GUIDES.md). `-UseCache` rebuilds available cached pages and summaries without network requests. A normal refresh tries individual pages and stops on a failed fetch, leaving the loaded reference unchanged. Newly available individual pages replace summaries on a later rebuild. Route ordering remains authored separately.

Sources: public Forever [Westfall](https://www.wowhead.com/forever/quests/eastern-kingdoms/westfall), [Loch Modan](https://www.wowhead.com/forever/quests/eastern-kingdoms/loch-modan), [Darkshore](https://www.wowhead.com/forever/quests/kalimdor/darkshore), [Redridge](https://www.wowhead.com/forever/quests/eastern-kingdoms/redridge-mountains), [Zephras](https://www.wowhead.com/forever/zone=16593/zephras-isle) lists and individual cached quest/item records. Chain ordering was cross-checked against QuestieDB's raw quest fields and authored Forever corrections at `cac1eff815923f896d082764d023cf812454a023`; no QuestieDB payload or runtime dependency was bundled.

Automated checks cover Lua 5.1 loading, section action coverage, stable IDs, saved-progress migration, automatic handoffs, objective carry-over, live progress and navigation. They do not establish a fastest route, an XP guarantee or in-game availability. The 20–30 regional visits are installed and linked.
