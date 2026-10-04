# Levels 20–30 audit

Checked 11 playable chapters and 138 distinct current Forever quest pages. Required prerequisite gaps: 0.

## Changes

- Every chapter has a concrete normal-enemy recovery location and an actual-level exit check. Pickup level gates get recovery checks where needed.
- Optional and class-specific quest XP contributes zero to the required budget.
- Rare Sida bag loot and the Bronze Tube / high-level ogre star branch are optional.
- Final Duskwood requires quests 222 and 223, completing the ordinary worgen chain at level 29. Stable action IDs are retained.
- Objective tables were refreshed without importing third-party route prose. Young Crocolisk Skins requires six skins; installed text still says four.
- Collection objectives remain owned by the chapter scheduling them.

## Chapter results

| Chapter | Required listed quest XP | Rough reward + combat XP | Unresolved acquisition inputs |
|---|---:|---|---:|
| 20-22 Wetlands: Coast and Greenwarden | 5,580 | 14679–15124 | 0 |
| 22-24 Duskwood: road and introductions | 11,310 | 20429–21223 | 0 |
| 24-25 Wetlands: gnolls and excavation | 5,255 | 11555–11945 | 0 |
| 25-26 Duskwood: Raven Hill investigations | 12,110 | 34574–36242 | 0 |
| 26-27 Wetlands: relics and coastal goods | 10,790 | Unknown | 5 |
| 27-28 Duskwood: worgen and the hermit | 7,050 | Unknown | 1 |
| 28-29 Wetlands: shipwrecks and final raptors | 7,100 | 11087–11393 | 0 |
| 29-30 Duskwood: final patrols | 10,050 | 20118–21259 | 0 |
| 20-24 Ashenvale / Stonetalon: introductions | 22,755 | Unknown | 4 |
| 24-27 Ashenvale: eastern camps | 7,330 | Unknown | 2 |
| 27-30 Ashenvale: cleansing and lake circuits | 19,850 | Unknown | 3 |

These routes can require substantial additional combat. The recovery checks make this explicit; quest work alone is not guaranteed to fill each bracket.

## Evidence and limits

Installed QuestieDB 1.0.4, baked Forever flavor, build 365537a340473291f5af3b7a53a5eca94e2a5f1a. Local database supplies IDs, prerequisite relationships, normal enemy levels and spawn locations. Objective quantities come from current Forever pages; local objective tuples omit quantities.

[Current Young Crocolisk Skins objective table](https://www.wowhead.com/forever/quest=484/young-crocolisk-skins). Full per-quest source URLs, retrieval dates and hashes are in `20_30_AUDIT.json`.

- Installed Forever objective quantities are unavailable; objective text may retain Classic counts. Current page tables supply quantities.
- Installed Forever support drop/XP tables are Classic-derived; samples are not verified current-build conditional drop rates.
- Mob XP is a Classic normal solo estimate at chapter entry; actual level, modifiers, scripted combat and acquisition can differ.
- Shared group/NPC kills use the maximum count; multi-source expected drop overlap is not simulated in this model. Unknown inputs remain unknown.
- Collection estimates assume one item per successful drop; quest-specific multi-item drops and stack sizes have not been verified.

## Unresolved acquisition evidence

### 26-27 Wetlands: relics and coastal goods

- Quest 288, Flagon of Dwarven Honeymead: usable local drop/acquisition evidence
- Quest 299, Ados Fragment: object sources require acquisition verification; incidental containers do not prove zero combat
- Quest 299, Golm Fragment: object sources require acquisition verification; incidental containers do not prove zero combat
- Quest 299, Modr Fragment: object sources require acquisition verification; incidental containers do not prove zero combat
- Quest 299, Neru Fragment: object sources require acquisition verification; incidental containers do not prove zero combat

### 27-28 Duskwood: worgen and the hermit

- Quest 134, Abercrombie's Crate: object sources require acquisition verification; incidental containers do not prove zero combat

### 20-24 Ashenvale / Stonetalon: introductions

- Quest 1007, Ancient Statuette: object sources require acquisition verification; incidental containers do not prove zero combat
- Quest 1010, Bathran's Hair: object sources require acquisition verification; incidental containers do not prove zero combat
- Quest 1033, Elune's Tear: object sources require acquisition verification; incidental containers do not prove zero combat
- Quest 1034, Handful of Stardust: object sources require acquisition verification; incidental containers do not prove zero combat

### 24-27 Ashenvale: eastern camps

- Quest 1016, Divined Scroll: usable local drop/acquisition evidence
- Quest 1017, Sarilus Foulborne's Head: usable local drop/acquisition evidence

### 27-30 Ashenvale: cleansing and lake circuits

- Quest 1011, Bottle of Disease: object sources require acquisition verification; incidental containers do not prove zero combat
- Quest 1026, Iron Shaft: object sources require acquisition verification; incidental containers do not prove zero combat
- Quest 1027, Iron Pommel: object sources require acquisition verification; incidental containers do not prove zero combat

