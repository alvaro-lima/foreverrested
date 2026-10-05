# Anniversary Questie fallback review

Source: installed Anniversary `QuestieDB` addon. Its baked Vanilla QuestieDB matches the Classic Era and beta Vanilla database by SHA-256. The additional `src/corrections/Sod/sodBaseNPCs.lua` and `src/corrections/Era/classicNPCFixes.lua` tables supply separately labeled fallback evidence.

The Forever audit identified 413 NPC pins without a usable Forever Questie NPC spawn. Eleven pins have matching NPC ID, exact name, zone, and coordinates in the Anniversary Season of Discovery baseline. Three Summoned Voidwalker pins have matching faction-specific Classic Era corrections. These 14 pins across eight quests are recorded in `CLASSIC_NPC_FALLBACK_EVIDENCE.json` and applied only when the original pin still matches. Eleven positions were corroborated; three were refined. They are labeled Classic/Season of Discovery fallback, never Forever-verified locations.

The remaining 399 pins have no verified spawn from these sources. All 222 quest records absent from the installed Forever QuestieDB were checked against Anniversary Vanilla by quest ID and exact title; none matched. No unmatched quest or NPC data was imported.

Run `python tools/audit_classic_npc_fallback.py` to refresh the detailed comparison. `python tools/build_classic_npc_fallback.py` compiles the reviewed evidence file and checks the installed source hashes; it does not replace the evidence with a fresh audit's already-corrected coordinates.
