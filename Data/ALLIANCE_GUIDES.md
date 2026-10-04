# Alliance 1–10 beta guides

Use `/reload`, then left-click the minimap book or run `/fg guides`. The starter routes now use short linked sections:

| Route | Sections (authored step counts) |
| --- | --- |
| Dun Morogh | 1–5 Coldridge (30) → 5–8 Kharanos (41) → 8–10 eastern road (27) |
| Elwynn Forest | 1–5 Northshire (28) → 5–10 Elwynn (64) |
| Teldrassil | 1–5 Shadowglen (28) → 5–10 Teldrassil (56) |
| Zephras Isle | 1–5 Thendal Grove (44) → 5–8 village/highlands (46) → 8–10 western circuit (36) |

These are independently authored, rough routes using nearby objectives and batched turn-ins. They are not measured fastest routes. Real routes use explicit quest IDs and never bind arbitrary quests from your log.

## Classes and progress

Class advice covers Warrior, Paladin, Hunter, Rogue, Priest, Mage, Warlock, Druid and Shaman. Nearby sourced class quests appear at trainer checkpoints only when class/race restrictions permit. This does not imply every class can use every race or starting zone. Only take quests actually offered by your trainer. Full class quest chains and beta availability still need in-game verification.

Quest collection, objectives and delivery are separate actions. Optional side quests have their own numbered, skippable rows; trainer checkpoints retain class advice. Live objective counts take precedence over historical counts. A ready quest still needs its turn-in. **Next confirms manual trainer/note checkpoints**, saved separately for each guide. Back browses, Skip explicitly skips, and Auto returns to the first unfinished, unskipped step. Finishing a section automatically opens its linked successor, including the [10–20 routes](ALLIANCE_10_20.md). Accepted unfinished objectives remain in the Objectives panel across sections; explicitly skipping a quest removes its objectives.

Old whole-zone guides are hidden from the chooser and retained internally to migrate saved progress by stable action ID within the original route. Authored counts exclude travel and class-unlock actions inserted at runtime. Level bands are not measured quest-only XP guarantees. Starter sections now include concrete local XP recovery before higher-level pickups and chapter exits. These complete at the actual target level; optional XP is never assumed. Skip bypasses a recovery step explicitly. See [the starter audit](STARTER_AUDIT.md) for verified facts, fixes and missing drop/XP data.

The guides menu's **Recommend Guide** button directly loads a section using level, location, the race's linked route and accepted quests. Loading a linked section checks known missing essential quests and prerequisites without inferring completion from level. Catch-up actions appear before the regional route, marked with a yellow running figure. Accepted quests omit their pickup action; objective-complete quests need only delivery. Completed prerequisite alternatives are respected, and an accepted descendant supplies evidence that its acceptance prerequisites were met. Explicit skips persist. Tooltips explain the reason for each catch-up action. This depends on the available quest policy and client completion history; it does not identify every undocumented beta prerequisite.

On guide load, entry travel uses the first unfinished quest or located trainer's destination and the character's current region. A matching hearthstone is suggested only when present in the bags and its cooldown is confirmed ready. Named town bindings and home locations observed when binding are supported; unknown home locations are not inferred. Otherwise known flight destinations are preferred, with reviewed roads, boats and the tram as fallback. Entry rows show short instructions such as “Hearth to Thelsamar” or “Fly to Thelsamar.” Travel remains optional; arrival advances to the route. Changes in hearth availability or newly observed flight paths replan unfinished entry travel. Saved progress refers to the original action so entry travel is rebuilt from the current location on reload.

## XP, rewards and navigation

The Objectives panel lists current-area work first, then a collapsed **Other areas** group counted by quest. Expanded remote work is grouped by objective location, not by the guide's title. Source guide names appear in quest tooltips. Unknown or ambiguous locations remain visible under **Location uncertain**. Accepted objectives stay queued across areas, and the visible scrollbar and mouse wheel navigate overflow within the main window's height.

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

The reference contains 558 selected quest records, not an exhaustive inventory; Records outside the audited 1–20 chapters may still use sourced zone summaries with missing coordinates/reward stats explicitly labelled. `Data/alliance-reference.json` retains page URLs, retrieval times, checksums, restrictions, listed XP, available locations and reward metadata. `Guides/AllianceQuestData.lua` is its runtime counterpart. No third-party route ordering, quest prose or addon code is included.

Sources: [Dun Morogh](https://www.wowhead.com/forever/quests/eastern-kingdoms/dun-morogh), [Elwynn Forest](https://www.wowhead.com/forever/quests/eastern-kingdoms/elwynn-forest), [Teldrassil](https://www.wowhead.com/forever/quests/kalimdor/teldrassil), [Zephras Isle](https://www.wowhead.com/forever/zone=16593/zephras-isle), individual Forever quest/item records and class quest lists. Public data remains sourced, not in-game verified.

The [10–20 audit and fixes](10_20_AUDIT.md) covers all twelve continuation chapters, with sourced quest facts, labelled combat forecasts, optional/class XP exclusion, saved action identities and live mainland level recovery. Zephras continuation is labelled 10+ and preserves early departure.
