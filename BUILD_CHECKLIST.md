# Forever Rested build checklist

Goal: a lightweight, native WoW-styled leveling guide for WoW Forever, with routes chosen for efficient XP per minute. Start with Gnome/Dwarf Dun Morogh 1–10, then expand in level brackets.

Checked items describe implemented features, not proof of in-game acceptance. Estimates must remain distinguishable from measured results.

## Build 0 — Vertical slice and presentation

- [x] Native-styled tracker with live quest objectives and alternating subtle rows.
- [x] Grouped steps and optional objectives to work on alongside the current step.
- [x] Independent arrow with yards, saved position, and invalid-waypoint hiding.
- [x] Independent secure target buttons with native raid-marker icons.
- [x] Back, Next, Skip, Auto, and per-character guide progress.
- [x] Resizable tracker, saved window position, and font-size options.
- [x] Delayed button tooltips and optional debug display.
- [x] Minimap guide selector with level brackets 1–10 through 50–60.
- [ ] Complete an in-game acceptance pass: combat lockdown, reload persistence, Auto recovery, quest completion/turn-in, targets, arrow direction/distance, resizing, fonts, and tooltips.

## Build 1 — Forever quest inventory

- [ ] Inspect candidate Forever databases, their coverage, version/build, provenance, and reuse licenses.
- [x] Choose an offline import format; keep guide data separate from engine/UI logic. JSON validation/merge produces a versioned Lua catalog; see Data/README.md.
- [ ] Inventory all Dun Morogh quests relevant to Gnomes/Dwarves, including Forever additions and class-specific quests.
- [ ] Record IDs, quest/minimum levels, race/class restrictions, prerequisites, alternatives, and follow-up chains.
- [ ] Record pickup, objective, and turn-in locations, including multiple objective areas.
- [ ] Record base reward XP, required kills/items, mob levels, and drop-rate estimates where supported.
- [ ] Record guaranteed and choice item rewards: item ID, quality, required level, slot, armor/weapon type, stats, weapon damage/speed, and relevant effects.
- [x] Label missing, estimated, sourced, and in-game-verified fields; never silently substitute Classic values. Build stamps/confidence/evidence are required; unknown fields remain absent.
- [ ] Validate IDs and available quest/reward APIs against the installed Forever client.

## Build 2 — XP and time estimation

- [x] Define a player profile: class, level, movement speed, solo/group, and relevant bonuses. Offline inputs hold profile-specific times/net kill XP; measured defaults and bonus formulas remain pending.
- [ ] Include equipped gear, weapon/armor proficiency, and combat role/playstyle when estimating reward usefulness.
- [ ] Calculate expected reward XP at the player's level using verified Forever behavior.
- [ ] Estimate kill XP separately from turn-in XP, including relevant group/rested modifiers.
- [x] Estimate combat, finding the next mob, looting, recovery, interaction, and respawn time. Explicit combat and combined overhead/scenario inputs; real averages remain pending.
- [x] Estimate collection kills from remaining items and supported drop data; account for multi-item drops where known. Requires explicit drop chance/items per drop; live rates remain pending.
- [ ] Estimate travel using walkable paths, terrain, transport, and hearthstone availability.
- [x] Calculate expected XP/minute plus a slower-case time estimate. Unknown inputs stay unranked; slower scenarios are supplied assumptions, not statistical bounds.
- [x] Count shared travel and kills once when objectives overlap. Explicit share groups and travel-leg IDs; joint random collection completion is labeled approximate.
- [ ] Validate the estimator with small hand-calculated examples and measured quest clusters.

## Build 2A — Class- and level-aware reward value

- [ ] Verify available item, equipment, reward-choice, proficiency, and item-data-loading APIs in the Forever client.
- [ ] Compare usable quest rewards with the player's equipped item in the relevant slot; evaluate two-handed versus main-hand/off-hand combinations correctly.
- [ ] Evaluate rewards by class and playstyle: weapon damage for relevant attacks, useful primary/secondary stats, survivability, and recovery benefits.
- [ ] Scale reward value to the player's current level, expected replacement level, and current equipment; a low-level blue is not automatically better than a later green.
- [ ] Account for reward choice: count only the best usable choice, rather than adding mutually exclusive rewards together.
- [ ] Treat item quality as useful context, not as the upgrade score; useful greens and whites can outperform irrelevant blues.
- [ ] Estimate the future time saved by an upgrade over a bounded leveling horizon, with confidence labels and conservative limits to avoid oversized detours.
- [ ] Evaluate the complete prerequisite chain and travel cost needed to obtain the reward.
- [ ] Avoid double counting overlapping upgrades and their projected combat-speed benefits.
- [ ] Offer Fast XP and Balanced XP + Gear route preferences; keep reward priorities understandable and manually overridable.
- [ ] Explain high-value reward detours with the item, expected upgrade, extra time, and estimated benefit.
- [ ] Handle missing/uncached item data as unknown and refresh when available; never score it as a confirmed upgrade.
- [ ] Validate representative class/level/equipment comparisons, including unusable rewards, outdated blues, weapon upgrades, and choice rewards.

## Build 3 — Lightweight gameplay recorder

- [ ] Verify supported quest, XP, combat, loot, movement, and level-up events/APIs.
- [ ] Record quest accept/completion/turn-in timing and observed reward XP.
- [ ] Record kill timing and observed kill XP where attribution is reliable.
- [ ] Handle XP changes across level-ups and overlapping XP sources without double counting.
- [ ] Separate active play, AFK, deaths, and unrelated detours where detectable; label uncertainty.
- [ ] Maintain averages by class and relative mob level, with sample counts and confidence.
- [ ] Add an opt-in recorder toggle, local reset, and an export workflow for reviewing measurements.
- [ ] Bound saved-data size and sampling frequency; verify low CPU usage.

## Build 4 — Route planner

- [ ] Build prerequisite-aware quest chains and identify mutually exclusive branches.
- [ ] Group objectives by nearby locations and shared mobs/items.
- [ ] Rank clusters by estimated XP/minute, including pickup and turn-in travel.
- [ ] Include useful gear rewards in route decisions: compare added detour time with projected future time savings and survival benefits, scaled to current class, level, and equipment.
- [ ] Evaluate low-XP prerequisites by the useful follow-up chains they unlock.
- [ ] Batch turn-ins and plan trainer/vendor/hearthstone stops.
- [ ] Include level requirements, quest-log capacity, difficulty, and death risk.
- [ ] Produce explicit grouped steps, alongside objectives, and intentional skip decisions.
- [ ] Support safe level/progress checkpoints when players enter a guide partway through.
- [ ] Show short explanations for recommended detours/skips without cluttering the tracker.
- [ ] Generate routes offline first; keep runtime work lightweight and predictable.

## Build 5 — Gnome/Dwarf 1–10 guide

- [ ] Replace test quest bindings with verified quest IDs and route coordinates.
- [x] Author a draft opening route, filtering race/class requirements; in-game acceptance remains open.
- [x] Add concurrent hunting/collection objectives and native secure target entries.
- [x] Add pickups, turn-ins, trainer checkpoints, and useful custom notes to the draft.
- [ ] Identify worthwhile early equipment rewards and class-specific detours; verify the full acquisition chains and reward choices in-game.
- [x] Add level checkpoints, saved manual confirmations and safe manual overrides.
- [ ] Walk the route in-game; record actual XP, completion time, and failures.
- [ ] Compare alternative quest clusters against the initial route and revise bottlenecks.
- [ ] Mark the guide ready only after acceptance; retain development tests separately.

## Build 6 — Expand level sections

Each section needs its own zone/quest inventory, estimates, prerequisites, authored route, and in-game acceptance pass. Choose zones from the data rather than assuming a fixed zone per bracket. Share quest chains across section boundaries.

- [x] 10–20: author Westfall / Redridge, Loch Modan / Redridge and Darkshore drafts, plus an optional Zephras 10–14 continuation with exit reviews.
- [ ] 10–20: walk and validate each draft, including prerequisite availability, level gains and transport transitions.
- [x] Compare Zephras exit policies offline using sourced listed XP and explicit rough time/kill assumptions; expose uncertainty and avoid claiming an optimal exit level.
- [ ] Measure Zephras versus mainland speed by class/gear and validate the actual departure gate.
- [ ] 20–30: choose and validate routes.
- [ ] 30–40: choose and validate routes.
- [ ] 40–50: choose and validate routes.
- [ ] 50–60: choose and validate routes.
- [ ] Add transitions between sections, preserving per-guide progress and chain state.
- [x] Author rough 1–10 drafts for all Alliance starting zones: Dun Morogh, Elwynn Forest, Teldrassil and Zephras Isle; cover all nine class advice profiles with filtered sourced class tasks.
- [ ] Validate each Alliance race/class route in-game; complete missing class chains and tuned prerequisites.
- [ ] Expand to Horde starting zones.

## Build 7 — Release and maintenance

- [ ] Revalidate affected APIs/data after Forever client updates.
- [x] Version route data and migrate saved state safely when steps change. Explicit stable IDs preserve positions/skips through insertions/reorders; removed steps trigger live reconciliation.
- [ ] Check missing APIs/templates and missing quest/location data degrade gracefully.
- [ ] Verify no protected gameplay automation, insecure combat mutations, or external addon requirement.
- [ ] Review performance and saved-data growth during extended play.
- [ ] Document installation, controls, estimate limitations, and reporting incorrect route data.

Implemented foundation: bounded live quest/reward observations, build invalidation, current-build export, offline validated partial refresh with change report, and stable guide-step migration. See Data/README.md and Data/SOURCE_AUDIT.md. In-game acceptance and the complete Dun Morogh inventory remain open; automated route optimization is not implemented yet.

Next acceptance pass: walk the Alliance 1–10 and 10–20 drafts, test `/fg refresh` and `/fg data`, and record unavailable quests, prerequisite gaps and incorrect locations. The 554 sourced reference records are a selected subset, not a complete inventory; 90 are summaries without location/reward details. See Data/ALLIANCE_DRAFTS.md and Data/ALLIANCE_10_20.md for refresh and limitations.

Estimator foundation: tools/estimate_routes.py accepts explicit profiles and quest clusters, outputs expected/slower XP/time comparisons, and rejects stale/incomplete inputs. Hand-calculated tests pass; measured cluster validation is still open. See Data/ESTIMATES.md. Real quest data, gear scoring, and automatic route planning remain pending.
