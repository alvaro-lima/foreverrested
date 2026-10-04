# Level 10-20 audit and fixes

Reviewed 2026-10-03. All twelve playable chapters across Westfall/Redridge, Loch Modan/Redridge, Darkshore and the optional Zephras continuation.

147 quest pages and 159 NPC/item pages were read from the public Forever database. Objective quantities come from quest objective tables; each record retains its source, retrieval time and SHA-256 checksum. Live client objectives remain authoritative.

195/200 relevant NPC/item sample ratios are available. Missing ratios stay unknown. 27 incidental loot locations were removed from navigation; full raw evidence remains in the combat reference.

**The routes are repaired, but quests alone do not establish their advertised finish levels.** Required quest rewards and combat forecasts exclude optional and class-specific work. The mainland chapters now check actual level before acceptance gaps, the riskiest early combat and their next-guide handoffs. Recoveries name a sourced local mob area, display live XP to the next level, and complete automatically; explicit Skip still bypasses them. Remaining grind gaps can be substantial, especially in the later bands.

| Chapter | Steps | Required turn-ins | Listed required quest XP | Rough quest + combat XP | Recovery checks |
| --- | ---: | ---: | ---: | ---: | ---: |
| 10-12 Westfall: farms and first militia | 45 | 8 | 7,480 | 19,935–20,365 | 2 |
| 12-15 Westfall: militia and Defias | 38 | 8 | 8,680 | 15,427–15,627 | 2 |
| 15-20 Redridge (Westfall arrival) | 40 | 10 | 10,340 | 27,104–27,890 | 2 |
| 10-13 Loch Modan: western shore | 49 | 7 | 6,660 | 18,295–18,765 | 3 |
| 13-15 Loch Modan: excavation and lodge | 40 | 3 | 3,450 | 9,074–9,214 | 1 |
| 15-20 Redridge (Loch Modan arrival) | 40 | 10 | 10,340 | 27,104–27,890 | 2 |
| 10-13 Darkshore: coast and ruins | 54 | 16 | 12,790 | 21,709–22,278 | 3 |
| 13-17 Darkshore: northern circuits | 48 | 12 | 10,055 | 15,235–15,609 | 1 |
| 17-20 Darkshore: ruins and final work | 35 | 8 | 8,570 | 11,674–12,010 | 1 |
| 10+ Zephras: service and wind | 23 | 4 | 2,070 | 4,110–4,500 | 0 |
| 10+ Zephras: tower and village | 52 | 15 | 7,180 | 10,138–10,445 | 0 |
| 10+ Zephras: optional work and exit | 17 | 0 | 0 | 0–0 | 0 |

## Route repairs

- Westfall farms: Poor Old Blanchy, Goretusk Liver Pie, Patrolling Westfall and Red Leather Bandanas are now required local work. The lower-level objectives come before the level 14-15 Harvest Watchers; a live level-12 recovery precedes that hunt. The level 17-18 final militia ranks have a level-15 recovery.
- Western Loch Modan: Mountaineer Stormpike's Task starts in Thelsamar and is delivered at the northern guard tower. Filthy Paws collects four containers of Miners' Gear; it is not a kobold-ear hunt. Stormpike's Order is an optional Stormwind delivery, not an Ironforge hand-in.
- Eastern Loch Modan: the two timed challenges and the named Grawmug/Gnasher/Brawler pack are explicitly optional, with their XP excluded. Crocolisk Hunting requires five meat and six skins; shared crocolisk kills count once. Existing action IDs survive the optional conversion.
- Both Redridge arrivals: Hilary's Necklace is required during the tools dive. Selling Fish is accepted only after the level-16 acceptance check, then scheduled in the later local circuit. Existing action IDs survive group size and location changes.
- Darkshore coast and ruins: Tools of the Highborne, For Love Eternal and Washed Ashore are required, with the underwater follow-up and southern turtle added. Anaya is level 16, so the pendant objective has a level-13 recovery. Fishing-dependent work remains optional.
- Darkshore northern circuits: the northern beached creature is included on the shore visit. River sampling and moonwell water are item-use objectives; they never generate fictitious kill XP. The handoff checks actual level 17.
- Darkshore final work: southern carcasses, Fruit of the Sea, the Tower of Althalaxx introduction and four-parchment hunt supplement Mathystra. The dangerous tower interior and Ashenvale continuation stay outside this chapter. The exit checks actual level 20.
- Zephras: Catching Wind asks for six data interactions; Avenged Tenfold collects ten charms. The continuation chapters are labelled 10+ and remain available from level 10. They do not claim that short story clusters reach level 12 or 14. The final optional chapter contributes zero required XP and imposes no island grind.

## What the combat forecast means

Mob levels, classifications, acquisition relations and sample counts come from Forever NPC/item pages. The per-kill XP formula is a labelled Classic solo normal-mob approximation, evaluated at each chapter's entry level. It is not measured current-build Forever XP and does not simulate every level-up, rested/group effects, elite multipliers or damage attribution. Listed quest rewards are reference rewards, not measured level-adjusted turn-ins.

Collection forecasts prefer local normal mobs within a suitable entry-level range. Direct kills are established first; expected published-rate drops from shared planned kills reduce remaining collection kills. One item per successful drop is assumed only when stack information permits it. Rates may include kills without the quest and small samples; random outcomes can differ substantially. Shared groups count NPC kills once, rather than adding a full hunt per quest.

Quest containers, provided items and item-use objectives have no invented baseline combat. Incidental chest loot is not treated as a dependable alternative; a quest chest such as the Sunken Chest is retained when the published sample supports it. Four acquisition annotations were manually checked against quest instructions and are bound to page checksums. Unknown acquisition/rate/XP inputs produce an unknown total rather than silently supplying zero.

## Evidence and validation

[10_20_AUDIT.json](10_20_AUDIT.json) contains objective, reward, source and route facts; [10_20_COMBAT.json](10_20_COMBAT.json) contains NPC levels, sample ratios and acquisition evidence; [10_20_ROUGH_ESTIMATES.json](10_20_ROUGH_ESTIMATES.json) contains groups, warnings and assumptions; [10_20_XP_BUDGET.json](10_20_XP_BUDGET.json) separates required, optional and class work. [10_20_ACQUISITION.json](10_20_ACQUISITION.json) records reviewed item-use/object facts. [10_20_ACTION_IDS.json](10_20_ACTION_IDS.json) preserves the previous action identities for migration verification.

Sources: individual [Forever quest pages](https://www.wowhead.com/forever/quests), NPC/item URLs retained in the evidence files; [Classic XP formula](https://github.com/cmangos/mangos-classic/blob/master/src/game/Tools/Formulas.h). Prerequisite ordering is checked against the installed factual policy; this does not prove undocumented beta conditions or current-client availability.

Targeted checks cover all 147 source records, twelve chapters, optional/class XP exclusion, delivery/interaction semantics, shared drop credit, action identity retention, chapter-scoped objectives, nine live mainland handoffs and three optional island exits. Early-section, starter-regression, entry-travel, linked catch-up and optional-tooltip checks are also run. The broader legacy validate.py harness has a pre-existing secure-target macro assertion failure; this is not a passing full-suite claim.

Rebuild: `python tools/audit_10_20.py --cache <saved-cache> --apply`. Export quest requests first with `--export`; `tools/fetch_starter_audit.ps1 -Cache <saved-cache>` performs paced bounded batches and stops on the first failed request. Reviewed acquisition annotations require re-review if their source page changes. No third-party quest prose or route ordering is imported.
