# User preferences

- Group the objective panel as Current objectives and Upcoming objectives by planned step, not player zone. During objective travel show its destination quest as Current. Upcoming contains accepted unfinished objectives scheduled in this guide, ordered by step, with zone labels; collapse it by default. Include all objectives explicitly grouped in the active circuit.

- Keep travel explanations collapsed in guide rows by default, including the active row. Clicking a row shows its explanation; clicking it again collapses it. Automatic progression must not expand explanations.

- Keep quest rows focused on their own step; do not add an "Alongside this step" section.
- Objective collection belongs to the chapter/guide that schedules it. Do not bring later-chapter quests into the current guide's objective list, rows, or pins merely because they are accepted or nearby.

# Hunting-area navigation

- For an active hunting objective, direct the arrow to the closest valid recorded hunting area before falling back to the client quest waypoint. Compare world distances when available, including across zone maps; otherwise use same-zone distance. Re-evaluate as the player moves.
- Hunting areas are approximate destinations, not live creature positions. Do not claim that the arrow or target button finds the closest eligible creature.

# Quest target lists

- Group alternative mobs that satisfy the same quest objective under one target icon. Keep distinct objectives and ingredients separate, even within one quest. Remove a group's icon when its objective finishes.
- Use explicit, verified drop-source mappings. Check installed Forever QuestieDB data and the recorded locations in `Guides/Alliance_HuntingLocations.lua`; do not infer eligibility solely from similar mob names. Review surprising imported sources before adding them.
- Add reusable mappings in `Guides/TargetData.lua` with the quest ID/title, objective index, item ID/name, and eligible mob names. Reuse the existing grouping in `GuideEngine.lua` and `SecureTarget.lua` rather than adding quest-specific UI behavior.
- Grouped icon tooltips use the exact title **Target list**, list every eligible mob underneath, and show objective progress. Single-mob icons show that mob's name. Show icon tooltips immediately on hover.
- Use a Blizzard-style tooltip color hierarchy: gold section titles, warm orange target names, white objective progress, green interaction hints, and muted gray secondary explanations. Separate target names from progress with a blank line. Static eligible-source lists must not imply a live creature's reaction, level, corpse, or skinnable state.
- Use exact-name targeting. Start the macro with `/cleartarget`, target the first name, then try subsequent names with `/targetexact [@target,noexists][@target,dead][@target,noharm] NAME`. Keep the first living hostile match. Clear a dead or friendly final result before marking it. Do not revert to unconditional fallback lines that replace a valid target.
- Freeze secure macros, group membership, and protected layout/visibility during combat; apply pending updates afterward. Target following must recognize every eligible name in a group. Preserve all group names when refreshing `desiredTargets`.
- When adding groups, verify their drop sources, separate ingredients, completed-objective removal, macro fallback conditions, tooltip contents, and refresh/combat behavior. Relevant checks include `tests/validate_grouped_targets.py`, `tests/validate_next_targets.py`, `tests/validate_target_visibility.py`, and `tests/validate_multiple_hunting_areas.py`.

# Maintaining these instructions

- When the user establishes or changes a reusable guide behavior, update this file so future guide work follows the latest decision. User instructions in the current conversation take precedence.

# Authoring and revising guides

- Use explicit Forever quest IDs for real routes; never bind an arbitrary quest from the player's log by a similar title. Check faction, race, class, minimum acceptance level, prerequisites, mutually exclusive alternatives, and follow-up unlocks.
- Treat the installed Forever QuestieDB as the authority for quest NPC identities, spawn zones, and NPC pin coordinates. Audit the locations actually loaded by playable guides, including supplements. Correct confirmed mismatches through generated, sourced data; leave NPCs absent from this Questie build explicitly unverified instead of inventing coordinates.
- For quest/NPC records missing from Forever QuestieDB, inspect the installed Anniversary QuestieDB, including its Classic Era and Season of Discovery correction tables, as labeled fallback evidence. Require an exact NPC ID/name/zone match and nearby recorded coordinates for NPC-only corroboration; require an exact quest ID/title and matching actor or objective for quest facts. Preserve source labels and hashes, and keep unmatched Forever content unverified.
- Give Accept, Objective, and Turn-in their own numbered actions. Optional quests also get their own skippable actions; explanatory advice belongs in the relevant action tooltip.
- Prefer short linked regional visits, nearby objective circuits, and batched turn-ins. Verify every successor guide exists and its prerequisites have been scheduled. Route level bands are planning labels, not evidence that a quest chain is completed or that enough XP has been earned.
- Do not leave a long block of unrelated optional detours between the required local circuit and its exit recovery. Keep distant city, escort, and high-level branches out of the playable chapter unless a reviewed visit actually schedules them.
- Preserve stable guide/action IDs when their meaning is unchanged. Use new IDs for materially different actions, increment the guide revision, and check saved progress/skip migration when changing sections or route order. Retired definitions may still be needed for migration.
- Keep authored routes and factual data separate from engine/UI behavior. Use the existing guide constructors, policy, chapter, and route-order mechanisms; generated files should be updated through their source/compiler rather than patched in isolation.
- Maintain source URLs, retrieval/build context, and evidence for quest facts. Distinguish sourced, estimated, observed, and verified fields; unknown values remain absent. Do not silently substitute Classic data for Forever facts or bundle another addon's code, route ordering, or quest prose.

# Progress, optional work, and class unlocks

- Live objective counts and client completion state take precedence over reference counts. Objective completion still requires a separate turn-in; an accepted quest omits its pickup action.
- Respect explicit skips across remaining quest actions and section handoffs. Manual Back/From browsing holds progression until the user resumes. Next confirms only actions designed as manual checkpoints; do not silently complete quest objectives.
- Reconcile catch-up using known prerequisites, completion history, and accepted descendants. Do not infer completion or discard unaccepted quests solely from character level.
- Essential class unlocks and their prerequisite chains must respect class/race restrictions and remain represented across regional choices. Use the existing quest policy and catch-up mechanisms; do not assume every hub has every class trainer.
- Keep dropped-item, group, uncertain, and optional reward branches optional unless verified requirements justify otherwise. Do not use optional/class-specific XP to support a general route's advertised exit level.

# Travel, maps, and objective types

- On advancing to an unaccepted pickup in another region, insert the available transport route before directing the player to the quest NPC. Completed generated class catch-up actions must not be added again as pending route work.

- Flight travel steps need their numbered map pin at the departure NPC. Druid flights must point to Silva Fil'naveth in Moonglade, not the ordinary flight master; preserve departure navigation even for travel actions without runtime entry flags.
- A known ordinary flight path does not automatically override Silva. When her druid route serves the destination and comparable observed world positions place her closer to the player, prefer her departure; unknown positions do not prove proximity. This compares the approach to the NPC, not measured total journey time.

- When the selected travel method is Hearthstone, label the action **Heart to <binding destination>** in rows and instructions. Use the actual observed binding destination, including intermediate stops, and refresh the method when availability changes.

- For reviewed boat routes with a destination-specific dock pin, tell the player to board the named boat at the marked dock. Do not add instructions to check the boat destination.

- Consider learned, available class travel spells as intermediate route connections. For an Alliance druid travelling from Ashenvale to Auberdine without its ordinary flight path, offer Teleport: Moonglade followed by the druid flight from Silva Fil'naveth to Rut'theran Village (toward Darnassus), then the Auberdine boat. Keep teleport, druid flight and boat as separate travel actions; verify the offered destination, do not assume ordinary node ownership or a Classic druid-flight endpoint, and do not claim measured time savings. Prefer a ready matching hearth first. For Ashenvale -> Auberdine, do not let cached ordinary flight-node ownership suppress the learned druid shortcut; cached destination ownership alone does not verify a direct connection. When both ordinary departure and Auberdine nodes are observed as known, prefer the ordinary flight over the druid-flight/boat detour; distinguish the ordinary Moonglade node from Silva Fil'naveth.

- Entry travel should lead to the first unfinished located action from the player's current region. Suggest a hearth only with a known matching binding, the item present, and a confirmed ready cooldown; prefer known flight paths and reviewed road/boat/tram connections otherwise.
- Reconsider transport when a completed ordinary quest becomes the active turn-in, using the player's current location rather than only the authored hunting area. Insert optional runtime travel before the delivery when regions differ; reuse entry travel planning and preserve the underlying action ID, manual holds, and explicit skips. Do not recreate a dismissed suggestion on every refresh.
- Do not invent transport availability, zone map IDs, or walkable paths from straight-line coordinates. Validate map IDs against native zone names; leave unsupported destinations explicitly uncertain and hide invalid arrows safely.
- Keep pickup, objective, and turn-in destinations distinct. For multiple ingredients, use each objective's source/location rather than a quest-wide destination where it is ambiguous.
- Quest tooltip locations must come from that action's own evidence. Never substitute the current guide's region when a quest or class-detour objective lacks a recorded location; show **Not specified in guide data** instead. Known pickup/turn-in locations still apply to those respective actions.
- Missing locations are data defects to resolve before adding playable quest actions, not an acceptable finished guide. Supply evidenced destinations for every quest phase, including class detours and multi-region item assembly; advance the destination from observed quest/bag progress. Do not invent coordinates to satisfy coverage.
- **CANNOT add quests to a playable guide without location data for every scheduled Accept, Objective, and Turn-in action.** Missing evidence blocks inclusion until resolved. Run the action-location coverage check before considering a guide change complete; a guide region, quest giver's unrelated position, or guessed coordinate does not satisfy objective coverage.
- Run `tools/audit_action_locations.py --guide <chapter-id>` for a changed chapter and `tools/audit_action_locations.py` for the complete catalog. A nonzero exit blocks declaring location coverage complete. The repair report is `Data/MISSING_QUEST_LOCATIONS.json`; it includes optional actions too. Existing unresolved catalog defects do not authorize adding more unlocated quests.
- Distinguish creature drops from object gathering and exploration. Do not create combat target icons or describe a carcass/container objective as a hunt merely because it has an objective coordinate.

# Estimates, documentation, and verification

- For guide changes, run `python tools/check_guides.py` as the combined release gate. It must return zero before declaring the catalog ready; review `Data/GUIDE_QUALITY_REPORT.json` and repair every failure. Never narrow the suite or change expected behavior just to make it green. Location checks must use `GuideEngine:ActionLocations`, shared with runtime resolution. Add journey scenarios covering transitions, arrival and reload when changing progression/travel behavior.

- Label approximate locations and XP/time forecasts. Listed base XP is not a verified reward at the player's level. Missing drop rates, travel times, or combat inputs do not become zeroes; avoid claiming a fastest route or guaranteed exit level without evidence.
- Audit required-only XP for every chapter with `tools/audit_xp_progression.py`. Prefer suitable local quest work before optional city detours; explicitly label remaining combat as **Required XP recovery**, display live XP, and use normal enemies that still grant useful XP near the target level. A late chapter must not reuse gray/near-gray low-level mobs to conceal a large shortfall. When moving quest work between chapters, retain stable action IDs, remove duplicate scheduling, and regenerate reviewed orders/audits.
- Count shared kills/travel only with explicit verified overlap. Include prerequisite detours and transport costs when comparing routes; keep reward quality separate from an actual equipment-upgrade assessment.
- Run the existing Lua 5.1/mock checks relevant to the change. Use chapter/policy/migration checks for route changes, hunting/object-gathering checks for destinations, and travel checks for transport changes. Automated passes do not establish in-game acceptance; report material limitations and existing failures honestly.
- Older README/audit/checklist prose may describe superseded behavior, especially cross-chapter objective carry-over and unconditional client-waypoint priority. Follow current user instructions and this file; update affected documentation when changing those behaviors rather than restoring them from stale prose.

- Ordinary Moonglade -> Auberdine flights require an actually observed reachable connection at the ordinary taxi master, not cached node names alone. Druid-flight, teleport and boat legs must retain their transport type; generic flight logic must never redirect them to the ordinary Moonglade master.

- Complete boat transport at the evidenced arrival dock, independently of the quest objective destination. Complete druid flight after landing in its destination zone; do not require reaching the departure flight master or the later quest item.

- For druid travel to Moonglade, prefer learned available Teleport: Moonglade over normal flight suggestions. Apply this to authored class-chain return travel and runtime entry alike, and name the teleport in the row.

- Reconcile known ongoing collection and assembly stages against carried quest items on Auto, reload and bag updates. Use C_Item.GetItemCount with legacy fallback, exclude bank items, and keep joined-result items from restarting consumed ingredient stages. Live quest completion still owns objective completion and separate turn-in.

- Travel instructions must select available transport using current observed binding, carried hearthstone, cooldown and known connections; do not tell the player to use a hearth conditionally. For Westfall, consider a ready evidenced Stormwind/Elwynn binding plus reviewed onward roads. Re-evaluate when cooldowns, bags or binding change; absent binding evidence remains unknown.

- Show a transport leg as "Hearth to <observed binding>" when its selected mode is hearth; preserve the same binding in its instructions. World-map step pins should project evidenced zone coordinates onto the viewed broader map when the client confirms an inverse world-coordinate match, while avoiding unrelated maps.

- Starting a hearth cast must keep its travel leg and binding visible while the cast and loading screen run. A newly started cooldown is not arrival; resume route selection if the cast fails or is interrupted. Explicit Auto may clear the in-flight hold. For final ordinary land travel, entering the destination zone completes travel and passes local movement to the following objective or turn-in. Boat travel still requires its evidenced arrival dock. Verify both rules across route and class-chain tests.

- When a recorded multi-ingredient objective changes stage from bag progress, recalculate its travel on the next refresh, including while the main guide window is hidden. Insert the selected transport before the still unfinished objective; keep assembly and quest turn-in separate. Repeated refreshes must not duplicate travel or reopen the window.

- Treat Darnassus and Rut'theran Village as separate transport stops. The Darnassus portal reaches Rut'theran on the Teldrassil map; from there the boat reaches Auberdine. The reverse route takes the boat then portal. Silva Fil'naveth's druid flight lands at Rut'theran, outside Darnassus. Keep the eastern Darnassus gate route for Teldrassil island work. Do not invent a portal entrance map pin without verified coordinates.

- For Rut'theran Village to Auberdine, cached flight-node names alone do not prove an available taxi connection. Suggest a flight only when the open taxi map has confirmed that exact reachable connection; otherwise use the boat. Keep a selected boat leg labeled and described as a boat even if a hearth becomes ready later.

- Questie's installed Forever zone data identifies Rut'theran Village within Teldrassil but does not provide a fixed coordinate on the moving boat. Use the recorded dock only as an approximate boarding approach, stop the dock arrow after passive boat movement confirms boarding, and keep arrival at the destination dock as the completion condition for runtime entry travel.

- The user observed the Rut'theran boat boarding point at Teldrassil 54.9, 97.1 in the Forever beta. Use that point for the Rut'theran boat arrow, label it as the boarding area, and retain passive boarding detection and destination-dock arrival checks.

- When the player is in a town with a flight master whose path is not learned, insert a separate local flight-path learning step before continuing the guide. Confirm town proximity from the observed subzone or a recorded town area, and complete the step when the client confirms the path. Respect explicit skips and manual browsing; do not mistake Darnassus for Rut'theran's taxi stop.

- Gate optional quest actions that are unavailable until a verified predecessor is turned in. Keep an already accepted quest active even if prerequisite history is incomplete, and reevaluate the gate on refresh. For Forever quest 990, Trek to Ashenvale, installed QuestieDB identifies either Escape Through Force (994) or Escape Through Stealth (995) as the prerequisite; The Tower of Althalaxx is a separate chain.

- Forever quest 976, Supplies to Auberdine, is an escort starting with Feero Ironhand after The Tower of Althalaxx stage 973; its objective is to protect Feero, and its turn-in is Delgren at Maestra's Post. Keep pickup, escort objective, and turn-in as separate actions and gate the optional branch until 973 is turned in or 976 is already accepted.

- Re-evaluate local flight-path learning on refresh and reload, not only zone arrival. Do not treat the global taxi-node map's visible or `isUndiscovered=false` entries as character-owned flight paths. Reset the legacy cache populated from that source once, then learn ownership only from the character's open taxi map (`CURRENT` or `REACHABLE`).

- Proximity to the next quest destination must never auto-skip an unfinished flight-path learning row. Learning the taxi node is a distinct task even when the next NPC is nearby; only observed discovery, explicit confirmation, or an explicit user skip advances it.
