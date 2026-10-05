# Alliance 20–30 regional handoff redesign

The playable Kalimdor-start route now uses five short linked visits:

| Level band | Visit | Required listed quest XP | Counted reward + modeled combat XP |
| --- | --- | ---: | ---: |
| 20–23 | Ashenvale and Stonetalon introductions | 25,535 | 48,341–49,731 |
| 23–24 | Wetlands harbor and excavation | 10,835 | 24,939–26,182 |
| 24–25 | Redridge and Duskwood introductions | 11,310 | 19,239–20,136 |
| 25–27 | Duskwood investigations, then Ashenvale camps | 23,710 | 49,636–51,460 |
| 27–30 | Ashenvale cleansing and lake circuits | 19,850 | 21,890–21,974 |

The former 24–27 Ashenvale-only chapter offered two required turn-ins worth 4,550 listed XP. It remains registered but retired so saved progress on its stable actions can migrate into the rebuilt middle chapter. The 20–23 Ashenvale chapter keeps its ID and quest action IDs; the new Redridge/Duskwood chapters reuse established action IDs. Explicit skips and current actions are preserved by the existing guide migration logic.

The required XP figures exclude optional and class-specific work. Counted combat uses a Classic solo XP approximation and known objective groups; the range is **not** an expected total. Missing object/drop acquisition evidence is not counted as zero. Live quest acceptance, level-adjusted rewards, flight-path availability, travel time, and current XP may change the best handoff. The player's report that Elune's Tear was not offered at level 22 remains unresolved; its listed reward is still included in the nominal required baseline and should be discounted when planning a live run.

The Wetlands visit uses the eastern-continent arrival for harbor and excavation work before continuing through Redridge and Duskwood, then returning to Ashenvale. No fastest-route claim is made because transport costs have not been measured for every flight-path/hearth state. The alternative route remains the existing eastern-continent sequence. The redesigned sequence improves required quest density, but the 27–30 Ashenvale chapter still depends heavily on live XP recovery and needs beta observation before launch.

Regenerate `20_30_AUDIT.json` with `tools/audit_20_30.py --cache <recorded quest cache> --use-recorded` and `XP_PROGRESSION_AUDIT.json` with `tools/audit_xp_progression.py` after route edits. Test saved progress with `tests/validate_xp_progression.py` and the full guide gate.
