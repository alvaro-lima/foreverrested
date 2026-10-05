# Playable quest NPC location audit

The installed Forever QuestieDB is the authority for quest starter and finisher NPC IDs, zones, and NPC spawn coordinates. The audit reads the locations loaded by all playable guides, including location supplements.

- 711 quest records and 3,576 distinct NPC pins reviewed, including class and unlock quest records.
- 3,163 pins have a matching installed Forever Questie spawn. No supported pin remains in the wrong zone or more than six map-percent units from a recorded spawn. No quest starter or finisher NPC ID differs from Questie where both records exist.
- 92 stale or missing pins across 62 quests were corrected from Forever Questie, including pickup/turn-in pins in Stormwind, escort pickup zones, and class quests.
- 14 more pins have explicitly labeled Anniversary Questie fallback evidence: 11 Season of Discovery baseline matches and three Classic Era faction corrections. They do not count as Forever verification.
- 222 quest records are absent from this installed Forever Questie build. The remaining 399 NPC pins lack verified spawn evidence and stay in the audit rather than receiving guessed coordinates.

Re-run `python tools/audit_questie_npc_locations.py --report Data/QUESTIE_NPC_LOCATION_AUDIT.json` after QuestieDB updates. The correction source records the exact installed QuestieDB checksum; review and regenerate it when the database changes.
