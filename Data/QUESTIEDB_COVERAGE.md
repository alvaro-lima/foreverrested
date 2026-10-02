# QuestieDB coverage check — 2026-10-01

Checked upstream master at `cac1eff815923f896d082764d023cf812454a023`. Downloaded source files were inspected in a temporary directory; no database payload or runtime dependency was added to the addon. Machine-readable counts are in `QUESTIEDB_COVERAGE.json`.

**Finding:** sufficient quest inventory to begin rough Alliance 1–10 and 10–20 guides. This is a coverage conclusion, not proof that completing one selected zone yields all required leveling XP.

| Zone | Raw quests at quest levels 1–10 | Raw quests at quest levels 11–20 | Additional generated quests at levels 1–20 |
| --- | ---: | ---: | ---: |
| Dun Morogh | 26 | 4 | 20 |
| Elwynn Forest | 35 | 1 | 25 |
| Teldrassil | 24 | 9 | 13 |
| Zephras Isle | 0 | 0 | 109 |
| Westfall | 6 | 24 | 18 |
| Loch Modan | 4 | 32 | 5 |
| Darkshore | 5 | 59 | 6 |
| Redridge Mountains | 0 | 21 | 1 |

Counts use quest level, not minimum acceptance level. Raw entries include Alliance-compatible or unrestricted race masks. They have not been filtered for a particular class, profession, dungeon, repeatability or viable chain. Additional generated counts exclude IDs already present in the raw table, but are not faction-filtered: Zephras includes both sides and unresolved eligibility assumptions. These columns must not be added together and presented as a character's available quest count. Corrections may change categories/levels; full effective counts require the official layering and dynamic facts.

## What is useful

- Raw quest fields include minimum/quest levels, race/class restrictions, starter/finisher references, objectives, prerequisite groups/singles, exclusive branches and breadcrumbs.
- NPC/object records provide spawn locations and links. Forever map support and converted coordinates are available, with documented unresolved areas.
- XP support entries exist for 29/30 raw Westfall quests, 36/36 Loch Modan, 63/64 Darkshore and 21/21 Redridge in this level range.
- Generated Forever additions substantially extend each zone and supply the new Zephras records.

## Gaps relevant to our addon

- None of the additional generated low-level IDs counted here has an entry in the inspected Forever quest XP support table. That table is an inherited Classic baseline; presence does not verify beta XP tuning. Continue using public Forever reference XP and current-build observed turn-in XP.
- Generated new-content records do not guarantee complete objectives, restrictions or prerequisites. Apply inherited corrections, generated base, traces, authored fixes and dynamic corrections in upstream order.
- Quest records do not provide a complete equipment reward-choice/stat dataset for class-aware upgrade scoring. Our public reward references and live item/reward reads remain necessary.
- This check does not establish drop rates, kill times, walkable travel costs or native client acceptance.

The practical next use is an offline Forever catalog with provenance, joined to our XP/reward reference data, followed by authored Westfall, Loch Modan and Darkshore drafts. Do not make QuestieDB a mandatory runtime dependency. Reuse terms remain to be resolved before redistributing its payload; the upstream tree inspected here has no top-level license file.

## Sources

- [Raw Forever quest database](https://github.com/Questie/QuestieDB/blob/cac1eff815923f896d082764d023cf812454a023/data/Forever/foreverQuestDB.lua)
- [Generated Forever quest additions](https://github.com/Questie/QuestieDB/blob/cac1eff815923f896d082764d023cf812454a023/src/corrections/Forever/generated/foreverBaseQuest.lua)
- [Forever XP support](https://github.com/Questie/QuestieDB/blob/cac1eff815923f896d082764d023cf812454a023/support/Forever/QuestXP/xpDB-classic.lua)
- [Forever layering and limitations](https://github.com/Questie/QuestieDB/blob/cac1eff815923f896d082764d023cf812454a023/docs/forever.md)
- [Generated-data limitations](https://github.com/Questie/QuestieDB/blob/cac1eff815923f896d082764d023cf812454a023/docs/forever-delta-base.md)
