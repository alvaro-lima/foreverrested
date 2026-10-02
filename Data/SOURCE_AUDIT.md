# Quest data source audit — 2026-10-01

## Installed client/addons

The addon and nearby Forever addon TOCs use Interface 16001. This is interface compatibility evidence, not an exact runtime build. `GetBuildInfo()` is captured in-game by the collector.

Installed ForeverWisp has route/target data and a Classic-derived quest-mob subset. Its subset is not a full Forever quest/reward inventory. Existing ForeverRested mappings cover quest 95212 and item 267414 with a sourced approximate hunting area. No new third-party database payload has been bundled in this build.

## QuestieDB candidate

- Repository: https://github.com/Questie/QuestieDB
- Forever boundaries/coverage: https://github.com/Questie/QuestieDB/blob/master/docs/forever.md
- XP/drop/map support: https://github.com/Questie/QuestieDB/blob/master/docs/support-data.md
- Provenance: https://github.com/Questie/QuestieDB/blob/master/PROVENANCE.md

The Forever branch owns quest, NPC, object, item, correction, XP, and map inputs. Its documentation explicitly identifies inherited baseline data, incomplete new-content coverage, coordinate limitations, and validation requirements. The raw quest schema contains restrictions and dependencies; it is not itself a complete reward-stat/XP/time dataset.

At inspection, no top-level LICENSE file was present in QuestieDB's repository listing. Provenance identifies Questie-derived source, but that does not by itself resolve reuse terms for every payload. Before importing/bundling its data, resolve upstream terms, record an exact source commit/checksum, apply the correct correction layers, and keep original field provenance. This candidate remains a reference pending that review; no runtime Questie dependency has been added.

## Blizzard Forever API evidence

Inspected Blizzard UI source mirror at Forever commit `70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e` (documented by Questie's audit as version 1.60.1/build 69913):

- https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_APIDocumentationGenerated/QuestLogDocumentation.lua
- https://github.com/Gethe/wow-ui-source/blob/70ef1b2fd78061a73f886c4a1e79dc5b5cff6d5e/Interface/AddOns/Blizzard_UIPanels_Game/Vanilla/QuestInfo.lua

The event documentation declares QUEST_TURNED_IN with questID, xpReward, and moneyReward. Objective declarations contain text, type, fulfilled/required counts, completion, and optional objectiveType. The Vanilla reward UI reads GetNumQuestRewards/GetNumQuestChoices, GetQuestItemInfo, and GetQuestItemLink. That UI suppresses displayed XP and does not establish that GetRewardXP is usable on the current client. The collector treats dialogue XP as optional and uses event XP when provided.

Runtime availability is exported in capabilities. Read helpers fail gracefully when APIs are missing. No selected-log mutation, protected actions, or whole-world quest enumeration is used. The source mirror and automated mocks do not prove current-client behavior; reward capture and copy-window interaction need in-game acceptance.

## Remaining inventory work

The Alliance reference build additionally extracts factual fields for 554 selected public Wowhead Forever quest records from individual pages and class/zone lists. 90 are summary-only records with missing locations and reward stats. Source URLs, retrieval times and checksums are retained in `alliance-reference.json`. This is separate from current-build observations and is not a complete inventory. Route ordering is independently authored; no third-party route payload or quest prose is bundled. See [ALLIANCE_GUIDES.md](ALLIANCE_GUIDES.md) and [ALLIANCE_10_20.md](ALLIANCE_10_20.md).

Collect verified Dun Morogh quest identities and acquisition chains, NPC/objective locations, restrictions, base-XP behavior, and reward equipment details. Cross-check coverage before calling the zone inventory complete. XP formulas, drop rates, travel paths, and combat times remain unverified until sourced or measured; Classic values will not be silently promoted to Forever facts.
