# Level 1-10 audit and fixes

Reviewed 2026-10-03. Ten playable chapters across four starter routes; 142 authored quests.

Quest objective counts were read from the objective table of fetched Forever pages. Live client objectives remain authoritative.

**Required routes and progression repaired; XP forecasts remain approximate.** Optional rewards and kills are excluded. Listed quest XP is reference XP, not a measured reward at the character's level. The initial HTTP 403 responses cleared on retry. Paced batches collected 139 mob/item pages; unavailable published loot samples remain unknown.

| Chapter | Required turn-ins | Listed required reward XP | Direct kill objectives | Recovery steps |
| --- | ---: | ---: | ---: | ---: |
| 1-5 Coldridge Valley | 8 | 2,125 | 38 | 2 |
| 5-8 Dun Morogh: Kharanos circuits | 10 | 5,280 | 22 | 2 |
| 8-10 Dun Morogh: quarry and eastern road | 3 | 1,880 | 16 | 1 |
| 1-5 Northshire | 6 | 1,435 | 32 | 2 |
| 5-10 Elwynn Forest | 20 | 9,835 | 13 | 2 |
| 1-5 Shadowglen | 8 | 2,005 | 25 | 2 |
| 5-10 Teldrassil | 15 | 8,610 | 13 | 1 |
| 1-5 Zephras: Thendal Grove | 9 | 1,510 | 38 | 4 |
| 5-8 Zephras: village and highlands | 7 | 2,400 | 11 | 2 |
| 8-10 Zephras: Windfield and scholar | 11 | 5,885 | 5 | 1 |

Direct kill counts are objective requirements, not a full combat XP total. Item drops, supplied quest items, object looting and talk/escort credit are not silently converted into kills. Shared work must be resolved before summing kill XP.

Known prerequisite ordering passes for the required route using the existing policy; undocumented Forever prerequisites remain unverified. Objective collection stays in the chapter that schedules it.

Each chapter now has a sourced local combat recovery step at its exit, plus checks before required pickups above its entry level. These use actual player level and live XP to the next level, complete automatically, and can be bypassed explicitly with Skip. They do not add later-chapter quest objectives or turn optional quests mandatory.

The required route now includes the Stonefield/Maclure necklace chain, eastern logging/Defias work, the western Shimmerweed quest, Zenn's collection/redemption, Denalan's delivery, the road ambushers and the properly ordered Sleeping Druid / Druid of the Claw stages. Named/elite group detours and dropped-item starts remain optional. Former optional action IDs are retained for promoted work so saved positions and explicit skips survive.

The importer now excludes provided items from collected objectives and retains scripted objective rows. Navigation excludes 81 incidental loot locations using a documented inference: where a source has at least 5% published drop frequency, targets more than ten times less likely are unsuitable fallback farming targets. Full raw source evidence is preserved in the cache and STARTER_COMBAT.json.

STARTER_COMBAT.json contains sourced Forever mob levels and loot samples, including tiny-sample and incidental-drop flags. STARTER_ROUGH_ESTIMATES.json combines required rewards and approximate combat XP, selecting local normal mobs and counting shared work once. Estimates use the chapter entry level and the Classic solo XP formula; actual XP changes with level, modifiers, drops and scripted encounters. These are planning estimates, not promised finish levels. Provided items, talk and escort credit are not silently counted as kills.

Sources: individual quest URLs and page checksums in STARTER_AUDIT.json; [QuestieDB NPC baseline](https://github.com/Questie/QuestieDB/blob/cac1eff815923f896d082764d023cf812454a023/data/Forever/foreverNpcDB.lua); [Classic XP formula reference](https://github.com/cmangos/mangos-classic/blob/master/src/game/Tools/Formulas.h).

Remaining field verification: conditional quest drop rates, actual Forever XP modifiers and scripted combat. Further route expansion may reduce recovery grinding. The runtime fix does not establish that quests alone fill the advertised bands.

Validation: starter source/parser checks, all ten live level handoffs, prerequisite ordering, early-section migration, optional-XP arithmetic, objective queue, linked catch-up, entry travel and optional tooltips pass. The broader legacy validate.py harness fails at its secure-target macro assertion both before and after these audit edits; it is not a passing full-suite result.

Rebuild from the saved cache with tools/build_starter_combat.py, then tools/audit_01_10.py --apply --combat Data/STARTER_COMBAT.json, supplying --cache to both. The paced fetch helper stops at the first failed request. No third-party quest prose or route ordering is imported.

## Rough required-work XP

Fixed entry-level comparison only; no rested, class, exploration, optional or incidental XP. Ranges reflect mob levels, not the probability of lucky or unlucky drops.

| Chapter | Approximate required reward + combat XP |
| --- | ---: |
| 1-5 Coldridge Valley | 4,807–4,847 |
| 5-8 Dun Morogh: Kharanos circuits | 11,118–11,356 |
| 8-10 Dun Morogh: quarry and eastern road | 4,615–4,764 |
| 1-5 Northshire | 5,175–5,271 |
| 5-10 Elwynn Forest | 16,951–17,091 |
| 1-5 Shadowglen | 5,450–5,570 |
| 5-10 Teldrassil | 14,748–15,053 |
| 1-5 Zephras: Thendal Grove | 3,617–3,656 |
| 5-8 Zephras: village and highlands | 5,445–5,537 |
| 8-10 Zephras: Windfield and scholar | 10,305–10,513 |
