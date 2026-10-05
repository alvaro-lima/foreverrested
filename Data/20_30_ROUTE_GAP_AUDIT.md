# Alliance 20–30 route gap audit

Historical baseline before the 2026-10-05 handoff redesign. See `20_30_ROUTE_REDESIGN.md` for the current playable sequence.

Audited the currently loaded 11 chapters on 2026-10-04 with the installed Forever QuestieDB and recorded Forever quest pages. The RestedXP screenshots supplied by the player are used only to compare level-band structure, not as quest facts or route instructions.

## Current XP and pacing

| Route chapter | Required turn-ins | Listed reward XP | Counted reward + modeled combat XP | Unresolved acquisition inputs |
| --- | ---: | ---: | ---: | ---: |
| 20–24 Ashenvale / Stonetalon | 18 | 25,535 | 48,341–49,731 | 5 |
| 24–27 Ashenvale | 2 | 4,550 | 4,896 | 1 |
| 27–30 Ashenvale | 11 | 19,850 | 21,890–21,974 | 3 |
| 20–22 Wetlands | 4 | 5,580 | 14,679–15,124 | 0 |
| 22–24 Duskwood | 14 | 11,310 | 20,429–21,223 | 0 |
| 24–25 Wetlands | 4 | 5,255 | 11,555–11,945 | 0 |
| 25–26 Duskwood | 12 | 12,110 | 34,574–36,242 | 0 |
| 26–27 Wetlands | 8 | 10,790 | 15,846–16,288 | 5 |
| 27–28 Duskwood | 7 | 7,050 | 10,398–10,560 | 1 |
| 28–29 Wetlands | 4 | 7,100 | 11,087–11,393 | 0 |
| 29–30 Duskwood | 4 | 10,050 | 20,118–21,259 | 0 |

The counted range is **not** a total XP forecast. It includes only modeled, known combat groups and listed quest rewards. Missing drop rates, object acquisition, live XP modifiers, travel, and level-adjusted rewards remain unknown. Optional and class-only XP is excluded. The 20–24 chapter has 57 actions and two required level gates (23 and 24); the 24–27 chapter has only six actions and one exit gate (27). This makes the latter chapter mostly a combat-recovery instruction rather than a quest circuit.

## Evidence and eligibility findings

- The installed Forever QuestieDB reports no required prerequisite gap for the current 20–30 routes, but that does not prove the live beta offers every quest. The player observed that Elune's Tear (1033) was not offered at level 22. Its 1,750 listed XP must not be treated as certain until its live acceptance path is resolved.
- The nearby Stonetalon side work is excluded from the required baseline. Gerenzo's Orders includes an escort, Further Instructions crosses into the Barrens, and city delivery chains add transport. Reclaiming the Charred Vale has higher-risk enemies. Promoting these automatically would hide difficulty or travel cost.
- Stonetalon Supply Run (86574) has no quest record in the installed Forever QuestieDB. Its public Forever page supplies some facts, but this alone is insufficient to make it a required route dependency.
- The 27–30 Ashenvale chapter contains an 11-turn-in Raene/forest circuit while the 24–27 chapter has only two. Reconsidering the safe starting point of that chain may reduce the middle gap, but moving actions requires checking level, enemies, prerequisite handoffs, and saved-progress migration.
- The screenshot comparison shows RestedXP leaving Ashenvale/Stonetalon at 23, visiting Wetlands at 23–24, then returning to Ashenvale later. That is evidence that a regional handoff is worth evaluating. It is not evidence that the same order is fastest for this addon, character, or current beta build.

## Route decision

The current Kalimdor 20–30 route should not be described as a well-filled quest route. A replacement needs a verified 20–23 local circuit, a level-23/24 handoff using suitable quest work, and a stronger 24–27 circuit before the 27–30 Ashenvale return. Compare regional travel with known flight paths and current position; do not infer a fastest route from straight-line map distances. Keep optional and uncertain quests outside the required XP baseline until their availability and prerequisites are confirmed.

The generated `20_30_AUDIT.json` gives per-quest source and combat details. `XP_PROGRESSION_AUDIT.json` records the current required quest IDs and recovery steps. This document audits the route; it does not change saved guide steps.
