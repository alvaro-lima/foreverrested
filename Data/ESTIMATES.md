# XP/time estimator — first build

Run `python tools/estimate_routes.py --input Data/estimate-example.json` for a Markdown comparison, or add `--json` for detailed totals and time breakdowns. The supplied file is a synthetic arithmetic example, not a playable guide or measured Forever data. This tool is offline and has no runtime cost or external dependencies.

For each cluster, total XP is turn-in rewards plus XP from required kills. Total time includes supplied pickup/objective/turn-in travel, combat, finding mobs/looting/recovery, and NPC interaction. XP per minute is total XP divided by total minutes. Exploration and unrelated kills are currently excluded.

## Inputs

- Player profile: class, current level, client buildKey, movement speed in yards/second, and per-mob combat/overhead times and net XP per kill. Profiles can include group mode and playstyle context. Supply a different profile for different classes, levels, equipment, groups, or bonuses; the tool does not invent scaling formulas.
- Reward XP: explicitly evaluated/observed for the profile's player level. Different-level rewards remain unknown until a verified formula or matching observation supplies them. Base XP is not automatically treated as current-level XP.
- Kill objectives: remaining mob count.
- Collection objectives: remaining items, drop chance (0–1), and expected items per successful drop. Estimated kills are ceil(remaining / (dropChance × itemsPerDrop)). This is a planning approximation; random drops can take longer. Drop protection, competing players, and item sharing need verified data before modeling.
- Travel: explicitly supplied duration, or walkable path distance divided by movement speed. Include pickups, objectives, turn-ins, prerequisite detours, and transport waits. Normalized map coordinates alone cannot establish walkable distance. Use zero-duration/empty travel only when genuinely appropriate.
- Shared work: objectives with the same explicit shareGroup and mob key use the largest required kill estimate once. Without explicit sharing, work is added. A repeated travel-leg ID is counted once, but conflicting definitions are rejected.

Shared collection estimates are approximate: max of individual expected kills is not the exact expected stopping time for several independent random drops. The output labels this limitation. Kill-count overlap is exact when those kills really provide concurrent credit; authors must verify that assumption.

## Expected and slower scenarios

Times/speed/drop chance accept either one supplied number or `{expected, slow}`. Slow times must be larger; slow movement speed/drop chance must be lower. Both scenarios recompute kills, kill XP, and duration. More required kills may therefore also earn more XP in the slow scenario. The slow result is a supplied scenario, not a statistical confidence bound or guaranteed finish time.

Missing reward XP, combat/drop/travel data produces an unranked result instead of optimistic zero-filled totals. Invalid numbers, inconsistent sharing, duplicate quests, and mismatched build stamps are rejected. This estimator does not change the active in-game guide, skip quests, or automate gameplay.

## Next inputs and work

Populate real Dun Morogh quests/clusters after inventory and field verification. Connect live observations to explicit planner inputs, add measured class/level combat profiles, validate actual walking paths, and verify reward/kill XP modifiers. Gear-upgrade valuation and chain-aware route generation remain separate upcoming builds. Re-run estimates after beta data refreshes; same-build hotfixes require new observations or updated sourced inputs.
