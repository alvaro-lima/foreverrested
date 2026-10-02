# Catch-up quest protection

Coverage is scoped to the installed Alliance 1–20 guides. The baseline contains
21 Vanilla ability-unlock milestones and 454 factual quest records, including
all prerequisite ancestry found for referenced Vanilla quests and the Alliance
class-quest inventory available by level 20. Class gear quests are not mandatory
unless the retained route requires them as prerequisites.

The milestones cover Defensive Stance, Redemption and Sense Undead, hunter pet
training, Bear Form/Cure Poison/Aquatic Form, Imp/Voidwalker/Succubus, Poisons,
and the Alliance priest racial abilities. Vanilla mages have no required
ability-unlock quest within this level range. Higher-level unlocks are outside
these installed routes.

Critical quest actions appear as individual numbered Accept, Complete and Turn
in steps. A native warning icon identifies them; the tooltip gives the reason.
Their rows do not contain catch-up explanations or generic class-review text.
Catch-up never marks an unfinished protected action skipped. Skip is an explicit
manual bypass, saved by stable step ID per guide and retained across reloads.
Reset from here clears those manual bypasses from the chosen step onward.
Completed live quests display Done even if the action was previously skipped.

Catch-up checks actual turn-in history. It preserves all required dependencies,
selects one applicable alternative when the database allows alternatives, and
recognizes completed mutually exclusive variants. An accepted descendant proves
its acceptance prerequisites were met; it does not cause fabricated completion
flags for its ancestors. Required active parent quests are accepted without
prematurely turning them in. Missing or cyclic prerequisite data produces a
separate review step. Ordinary prerequisites still ahead in the retained route
remain in authored order; bypassed or missing requirements are recovered first.

## Data and provenance

- `Data/ClassicQuestPolicy.lua`: generated Vanilla facts and milestone manifest.
- `Data/classic-unlocks.json`: reviewed Alliance unlock classification.
- `Data/classic-policy-coverage.json`: source hashes, coverage and missing IDs.
- `Data/ForeverQuestPolicy.lua`: separately maintained Forever overrides.
- `Data/ForeverUnlockFacts.lua`: factual additions for the Forever Fire chain.
- `Data/forever-unlock-facts.json`: its editable source snapshot.

The Vanilla snapshot is pinned to Questie v8.0.0, commit
`dd4b24e392e5bdd5d04d6dfb0c5c201e9de3d876`. Both base quest records and relevant
Classic/Alliance correction fields are imported. The correction that swaps
Druid quest 26/27 faction assignments is also applied to the corresponding
lake prerequisite links. No Questie runtime or authored guide prose is bundled.

Source: https://github.com/Questie/Questie/tree/dd4b24e392e5bdd5d04d6dfb0c5c201e9de3d876/Database

Unlock classification sources:
- https://www.wowhead.com/classic/guide/warrior-class-quests-classic-wow
- https://www.wowhead.com/classic/guide/paladin-class-quests-classic-wow
- https://www.wowhead.com/classic/guide/hunter-class-quests-classic-wow
- https://www.wowhead.com/classic/guide/druid-class-quests-classic-wow
- https://www.wowhead.com/classic/guide/warlock-class-quests-classic-wow
- https://www.wowhead.com/classic/guide/rogue-class-quests-classic-wow
- https://www.wowhead.com/classic/guide/priest-class-quests-classic-wow

Public Forever pages checked on 2026-10-02 identify the shaman Earth chain
94373 → 94374 → 94375 and Fire chain
94449 → 94465 → 94466 → 94467 → 94468. These are concrete critical actions,
including when joining a mainland guide above their level. The Earth breadcrumb
96243 and replacement Sapta quest are not required unlock milestones.

- https://www.wowhead.com/forever/quest=94375/call-of-earth
- https://www.wowhead.com/forever/quest=94468/call-of-fire

Public data is not proof of availability on every running Forever build. Other
Forever-specific unlocks, races and altered prerequisites still need verified
overrides. The coverage report lists 203 IDs without a Vanilla record (mostly
Forever additions, plus legacy references 490, 912 and 960); do not interpret
missing data as proof that those quests have no prerequisites.

## Updating

Rebuild the Vanilla facts with Python + lupa.lua51:

```powershell
python tools/build_classic_policy.py --quest-db classicQuestDB.lua --npc-db classicNpcDB.lua --corrections classicQuestFixes.lua
```

Download those three files from the pinned revision above, outside the addon.
The compiler reads only literal data, never upstream module code, and refuses
unreviewed nonliteral corrections relevant to the imported subset. Changing the
source revision also requires updating the pinned source in the compiler and
reviewing its generated coverage report.

Forever overrides replace individual Vanilla records. `records[id]` supports
`critical`, `reason`, `classes`, `requiredRaces`, `minLevel`, `prerequisites`
(ALL), `prerequisitesAny` (ANY), `exclusiveTo` and `parentQuest`. `false` disables
a baseline quest as an unlock alternative. `unlocks[key]` replaces or adds a
milestone; `false` disables a milestone. Milestones specify class, level, terminal
quest alternatives, reason and either a race mask or explicit `raceTokens` for
new races. Put quest titles and locations into the factual catalog separately.

For each Forever correction, record its source, date and client build here.
Keep the override file separate from generated Vanilla data. As Forever
QuestieDB and other sources improve, review dependency/reward changes and add
new milestones and factual records. Data refreshes do not rewrite guide IDs or
silently promote all equipment rewards into mandatory quests.

Validation: `tests/validate_catch_up.py`, `tests/validate_critical_rows.py`,
`tests/validate_reset_from.py` and `tests/validate_autoquest.py`. Visual appearance
and actual quest availability still require an in-game check after `/reload`.

## Alliance Water Totem, reviewed 2026-10-02

The level-20 Dwarf Shaman chain 94495 -> 94497 -> 94499 -> 94500 -> 94501 -> 94502 -> 94503 -> 94505 is critical. Individual Forever pages list the ordered eight-stage series; 94505 rewards Water Totem. Sources: https://www.wowhead.com/forever/quest=94495/call-of-water and https://www.wowhead.com/forever/quest=94505/call-of-water. Quest 94503 places the manifestation in Westfall; shared NPC mapper coordinates pointing to Silverpine are excluded. Availability in the running Interface 16001 beta requires in-game validation.
