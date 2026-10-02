# Beta quest data workflow

This first build establishes refreshable data and progress migration. The catalog is intentionally empty until real data is collected/imported. It is not a complete Dun Morogh inventory or an efficient leveling route yet.

## Collect and refresh

1. `/reload` after installing this version.
2. Play normally. The addon observes your active quest titles, levels, objectives, and required counts. Opening quest dialogues records available reward choices and cached item details. `QUEST_TURNED_IN` records the reported XP reward. No quests or items are selected automatically.
3. `/fg refresh` rescans the live quest log. The minimap menu also has **Refresh** and **Data** buttons.
4. `/fg data` opens a native-styled copy window. Ctrl+A, Ctrl+C; paste into a UTF-8 JSON file, such as `Data/live-export.json`.
5. Run `python tools/refresh_quest_data.py --input Data/live-export.json --check` to validate and preview changes. The tool uses only Python's standard library.
6. Run the same command without `--check` to write `Data/quest-catalog.json`, `Data/QuestCatalog.lua`, and `Data/REFRESH_REPORT.md`.
7. `/reload` loads the refreshed catalog. There is no in-game filesystem/network updater or external addon dependency.

The import tool accepts structured JSON, not executable Lua or downloaded code. It rejects unknown schema versions, wrong games, missing/unknown build stamps, duplicate quest IDs, invalid counts/coordinates, non-finite numbers, and unsupported quest fields. A repeated identical import keeps the same revision. Partial refreshes retain omitted quests; omission is not proof that a quest was removed. Keep exports out of shared releases if you do not intend to distribute your observation data.

## Beta tuning and evidence

- Data records carry a `buildKey` made from client version, build, and interface number.
- A new build marks previous observations stale. Stale records are excluded from live exports and `QuestData:Get()` results until freshly observed/imported for the current build.
- Same-build hotfixes are reflected when quests/dialogues are observed again. Unvisited quests cannot be assumed unchanged or automatically checked.
- Live objective counts and completion drive guide progress; the engine does not hard-code required kill counts.
- `rewardXPObserved` is the reward at a particular observed player level/context, not a universal base XP value. Turn-in events can coincide with level-ups: a prior dialogue level is retained where available, and the post-event level is separately labeled. Without a pre-turn-in observation, the reward's original player level is unknown.
- Missing item details stay unknown (`detailsCached=false`). Reopen the dialogue once cached to capture those details. Reward choices are stored separately from guaranteed rewards.
- The catalog can carry sourced prerequisites, restrictions, and coordinates, but those require explicit evidence and build stamps. Unknown fields are absent, not fabricated or set to zero.
- Observations are bounded to 300 quests per character; oldest observations are evicted when the limit is reached. This is a lightweight collector, not an exhaustive server crawler or a combat timing recorder.

## Format

The input document uses `schemaVersion=1`, a `source` object with `game="forever"`, `kind`, `client`, and `buildKey`, and a `quests` array. Each quest needs `questID`, matching `buildKey`, and a confidence of `observed`, `sourced`, `estimated`, or `verified`. Non-observed records require `evidence`.

Optional quest fields: title, questLevel, requiredLevel, requiredRaces/requiredClasses masks, zone, lastSeen, objectives, rewardXPObserved, guaranteedRewards, choiceRewards, prerequisites, followups, locations, baseRewardXP, and evidence. Base XP must have supporting evidence; copying an observed XP number into baseRewardXP is rejected without it. Location coordinates use normalized 0–1 values and map IDs, with evidence distinguishing approximate areas from exact NPC positions.

Generated Lua strings use UTF-8 byte escapes, preserving localization and preventing text from becoming code. Only `QuestCatalog.lua` is loaded by WoW; Python and JSON/report files are offline tools/artifacts.

## Guide revision rules

Every registered step has an explicit unique `id`; guides have a `revision`. Keep IDs when a step's meaning stays the same, including when inserting or reordering other steps. Give materially different steps new IDs and increment the guide revision. Do not reuse deleted IDs for different actions.

Saved progress and skips map by stable step IDs. When the selected step disappears, resume from the start and recheck live quest state rather than carrying an unrelated numeric index. Completed quest IDs remain per character. Legacy numeric progress migrates for the current initial revision; future revisions must use stable IDs.

This protects progress across authored guide updates. It does not yet automatically optimize/reorder routes when rewards change: the XP/time estimator, gear valuation, and planner are subsequent checklist builds.

## Validation

`tests/validate_data.py` exercises changed builds, changed objective requirements, XP/reward capture, absent APIs, bounded storage, export/import round-trips, partial merges, invalid imports, and inserted/removed guide steps. These mocked Lua 5.1 checks do not establish in-game acceptance.
