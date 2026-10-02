# Forever Rested

Forever Rested is a leveling guide addon for **WoW Forever**, with step-by-step quest routes, live progress tracking, a navigation arrow, and a native WoW-style interface. It has no external addon dependencies.

**Beta:** Alliance level 1–30 routes are included, with an optional Zephras Isle 10–14 continuation. Routes still need in-game validation; quest availability, prerequisites, rewards, and coordinates may change between beta builds. Horde guides are planned but are not included.

[Source](https://github.com/alvaro-lima/foreverrested) · [Report an issue](https://github.com/alvaro-lima/foreverrested/issues)

## Installation

1. Download or clone this repository.
2. Place the addon files in your WoW Forever client's `Interface/AddOns/ForeverRested` folder. Rename the downloaded repository folder to **ForeverRested** if necessary.
3. Check that `ForeverRested.toc` is directly inside that folder, rather than inside another nested folder.
4. Enable **Forever Rested** in the AddOns menu at character selection, then log in. Use `/reload` after updating an existing installation.

The included TOC targets **Interface 16001**. Compatibility with other WoW clients is not verified. Progress and settings are saved per character in `ForeverRestedDB`; each guide retains its own progress.

## Included guides

| Levels | Routes |
| --- | --- |
| 1–10 | Dun Morogh, Elwynn Forest, Teldrassil, Zephras Isle |
| 10–20 | Westfall / Redridge, Loch Modan / Redridge, Darkshore |
| 10–14 | Optional Zephras Isle continuation with exit-choice checkpoints |
| 20–30 | Duskwood / Redridge, Wetlands, Ashenvale / Stonetalon |

Guides filter applicable tasks by class and race. This does not imply that every class can use every starting zone. Routes are independently authored beta routes; their leveling speed has not been measured.

See the [Alliance 1–10 guide notes](Data/ALLIANCE_GUIDES.md) and [Alliance 10–20 / Zephras notes](Data/ALLIANCE_10_20.md) for route details and sources.

See [Alliance 20–30 guide notes](Data/ALLIANCE_20_30.md) for the new regional circuits and Shaman Water Totem coverage.

## Getting started

- Run `/fg guides` or right-click the minimap compass to choose a guide.
- Run `/fg` or left-click the minimap compass to show or hide the tracker.
- Drag the tracker title bar to move it, and its bottom-right grip to resize it. The navigation arrow and target icons can be moved independently.
- Use the **Steps** tab to browse the route and the **Quests** tab to view your active quest log. Click a step to inspect it; **Auto** returns to live progress.
- Open `/fg options` to adjust text size, arrow size, and the map step limit (default 10, range 1-100). Position and size settings save per character.

### Progress and controls

Quest actions advance from live quest state. A quest that is ready to turn in is not complete until it has been rewarded. Required tasks block progression; **Do alongside** tasks are optional and can be completed while working on the current step. Trainer and note checkpoints require manual confirmation with **Next**.

**Back** browses earlier steps. **Next** moves forward and resumes automatic progress. **Skip** records an explicit skip. **Auto** returns to the first unfinished, unskipped step.

Loading a guide reconciles completed quests and can catch up to your character's level. Essential class unlocks and recorded prerequisites are protected from automatic catch-up skipping, though you can skip them manually. See [quest protection rules](Data/QUEST_POLICY.md) for coverage.

To revisit earlier content, select a step and click **From**, or use `/fg reset <step>`. This reopens skips from that point onward and clears later manual checkpoint confirmations while retaining skip history. `/fg reset` resets the guide and clears remembered skips. Completed quests still reflect live quest state.

The step search supports quest names, NPCs, notes, exact step numbers, priorities such as `critical` or `gear`, and statuses such as `skipped` or `ready`. Combine terms, for example `gear to do`. **Clear** or Escape restores the full list.

### Navigation and targets

The arrow and numbered map/minimap markers show the current destination. Native quest waypoints take priority; sourced NPC locations or approximate hunting areas provide fallbacks where available. Missing map or position data can hide navigation. Coordinates identify destinations, not walkable paths.

The movable target icons show unfinished kill targets from current and alongside tasks. Clicking an icon targets the named creature and attempts to apply its raid marker, subject to normal game permissions. Buttons do not attack. Changes to secure target buttons are deferred during combat.

After clicking a target icon, the arrow can follow the selected creature when the client exposes compatible position data. Otherwise it uses the guide destination. Map markers continue to represent the guide step.

### Quest interactions

When interacting with a quest giver, the addon can automatically accept and turn in matching quests from the selected guide's current step onward, including alongside tasks. Skipped and inapplicable tasks are excluded.

**Hold Shift during quest interactions to pause this behavior.** Multiple reward choices and quests requiring gold remain manual.

## Commands

| Command | Action |
| --- | --- |
| `/fg` | Toggle the tracker |
| `/fg guides` | Open the guide menu |
| `/fg options` | Open display options |
| `/fg next` | Move forward / confirm a manual checkpoint |
| `/fg back` | Browse the previous step |
| `/fg skip` | Skip the current step |
| `/fg auto` | Resume live guide progress |
| `/fg reset [step]` | Reset the guide, or restart from a specified step |
| `/fg debug` | Toggle diagnostics |
| `/fg refresh` | Rescan live quest data |
| `/fg data` | Open the observation export window |

## Reporting bugs and contributing

Please [open an issue](https://github.com/alvaro-lima/foreverrested/issues) with:

- Your client version/build and addon version from `ForeverRested.toc`.
- Character faction, race, class, and level.
- Guide name, step number, and quest ID where applicable.
- What you expected, what happened, and steps to reproduce it.
- Relevant Lua errors or `/fg debug` details; screenshots are helpful for interface problems.

For route corrections, include a source or in-game evidence for prerequisites, quest availability, coordinates, or rewards. Review exported data and screenshots before posting them publicly.

Focused pull requests for fixes, route corrections, and documentation are welcome. Keep stable guide step IDs when their meaning has not changed so existing progress can migrate correctly. Separate authored routes from sourced facts, and record evidence for data changes.

## Development

The addon is loaded through [ForeverRested.toc](ForeverRested.toc). Runtime code is Lua; scripts in `tools/` and `tests/` run offline and are not loaded by WoW.

- `Guides/`: authored routes, quest references, and target mappings.
- `GuideEngine.lua` / `GuideLibrary.lua`: progression and per-guide state.
- `QuestLog.lua` / `QuestPolicy.lua`: live quest state and catch-up protection.
- `Navigation.lua`, `Arrow.lua`, `StepPins.lua`: destinations and navigation displays.
- `UI.lua`, `Tracker.lua`, `SecureTarget.lua`, `Minimap.lua`: interface and target controls.
- `Data/`: quest catalogs, provenance, policy data, and workflow documentation.

The validation scripts use **Python and `lupa` with Lua 5.1 support**. From the repository root:

```sh
python -m pip install lupa
python tests/validate.py
python tests/validate_guides.py
```

Additional `tests/validate_*.py` scripts cover specific behavior, including catch-up, resets, search, navigation, combat restrictions, and quest interactions. Run the checks relevant to your changes. Mocked tests do not establish in-game API behavior, visual layout, or route correctness; those require client testing.

See the [quest data workflow](Data/README.md) for collecting and importing build-stamped observations, the [source audit](Data/SOURCE_AUDIT.md) for data provenance, and the [build checklist](BUILD_CHECKLIST.md) for release checks. Observation exports are local and copied manually through `/fg data`; the addon has no in-game network or filesystem updater. Automatic route optimization and equipment scoring are not implemented.
