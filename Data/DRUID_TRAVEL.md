# Druid travel shortcut

Corrected player observation on 2026-10-04: Moonglade has separate ordinary and druid flight masters. Without the ordinary Auberdine flight path, use Teleport: Moonglade, Silva Fil'naveth's druid flight toward Darnassus (Rut'theran Village), then the Auberdine boat. The earlier assumed direct druid flight to Auberdine was incorrect and is superseded.

Silva Fil'naveth: NPC 11800, installed Forever QuestieDB, area 493, recorded spawn 44.15 / 45.23. Navigation resolves the zone map against its native name. Never use the ordinary Moonglade flight-master marker for this leg.

Teleport, flight and boat are separate actions. Learned spell 18960 and its available cooldown are checked; a ready matching hearth has priority. No measured journey times or fastest-route guarantee. Flight and boat are player actions. The existing reviewed Rut'theran -> Auberdine dock connection is reused.

Validation: tests/validate_druid_travel.py, entry and turn-in travel checks. Mock tests do not establish in-game transport availability.

Transport selection checks a ready matching hearth, then known ordinary departure and destination nodes, then the available class shortcut, then reviewed ground/boat connections. Ordinary Moonglade -> Auberdine requires both ordinary nodes known; Silva is never substituted for that departure. Destination-only cache entries do not suppress the class detour. These are availability-based preferences, not measured time optimization.
