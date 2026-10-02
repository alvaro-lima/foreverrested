# Alliance 1–10 beta guides

Use `/reload`, then left-click the minimap book or run `/fg guides`. Four routes are installed:

| Route | Main circuit |
| --- | --- |
| Dun Morogh | Coldridge → Kharanos → western hunting loop → eastern quarry |
| Elwynn Forest | Northshire → Goldshire → eastern camps → Westbrook |
| Teldrassil | Shadowglen → Dolanaar → nearby lake, timberling and barrow circuits |
| Zephras Isle | Alliance High Order opening → Shendar → western circuit → Valanaar and Windfield |

These are independently authored, rough routes using nearby objectives and batched turn-ins. They are not measured fastest routes. Real routes use explicit quest IDs and never bind arbitrary quests from your log.

## Classes and progress

Class advice covers Warrior, Paladin, Hunter, Rogue, Priest, Mage, Warlock, Druid and Shaman. Nearby sourced class quests appear at trainer checkpoints only when class/race restrictions permit. This does not imply every class can use every race or starting zone. Only take quests actually offered by your trainer. Full class quest chains and beta availability still need in-game verification.

Required tasks complete from the live quest log; optional alongside tasks do not block a step. Live objective counts take precedence over historical counts. A ready quest still needs its turn-in. **Next confirms manual trainer/note checkpoints**, saved separately for each guide. Back browses, Skip explicitly skips, and Auto returns to the first unfinished, unskipped step. The level-10 checkpoint completes from the player's level. [10–20 guides and the optional Zephras continuation](ALLIANCE_10_20.md) are now available.

## XP, rewards and navigation

Pickup/turn-in entries show current-build observed reward XP at the same player level when available, otherwise approximate listed reference XP. Do not interpret listed XP as a verified reward at your level. Reward names use quality colors; recipes are not treated as equipment upgrades. Class advice and optional reward detours provide context, but equipped-item comparison and automatic gear scoring are not implemented.

Native client quest waypoints take priority. Public representative NPC/drop locations supply approximate fallback destinations and loot-source target names. They do not describe walkable paths or moving creatures. Established map IDs are checked against native map names; Zephras resolves its native map at runtime instead of using an invented ID. Missing map support hides navigation safely.

Beta prerequisites, availability, coordinates, XP and rewards may change. If a mandatory quest is not offered, check its preceding turn-in and level first, then use Skip where appropriate and report the quest/step ID with `/fg debug`. Routes have not yet been walked in-game.

## Refresh public references

From the addon folder, with Python available:

```powershell
./tools/refresh_alliance_reference.ps1 -Python python
```

Then `/reload` in WoW. `-UseCache` rebuilds from previously downloaded pages. Fetch failures prevent compilation; review changes before relying on a tuned route. This refresh updates facts for the existing reference set, not the authored route order or a complete newly discovered quest inventory. Stable step IDs preserve progress. Adjust `Guides/Alliance_01_10.lua` when prerequisites or route structure change.

`/fg refresh` and `/fg data` separately capture/export current-client observations through the workflow in [README.md](README.md). Public references do not become build-verified observations just because they were downloaded again.

## Sources and scope

The reference contains 554 selected quest records, not an exhaustive inventory; 90 use sourced zone summaries with missing coordinates/reward stats explicitly labeled. `Data/alliance-reference.json` retains page URLs, retrieval times, checksums, restrictions, listed XP, available locations and reward metadata. `Guides/AllianceQuestData.lua` is its runtime counterpart. No third-party route ordering, quest prose or addon code is included.

Sources: [Dun Morogh](https://www.wowhead.com/forever/quests/eastern-kingdoms/dun-morogh), [Elwynn Forest](https://www.wowhead.com/forever/quests/eastern-kingdoms/elwynn-forest), [Teldrassil](https://www.wowhead.com/forever/quests/kalimdor/teldrassil), [Zephras Isle](https://www.wowhead.com/forever/zone=16593/zephras-isle), individual Forever quest/item records and class quest lists. Public data remains sourced, not in-game verified.
