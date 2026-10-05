# Implementation status

The original build specification remains the design authority. This repository implements a bounded technical prototype of portions of phases 0, 1, 3, and 4. **None of the specification's full in-game phase exit conditions has been certified.**

| Module | Current implementation | Remaining work |
| --- | --- | --- |
| EA_Core | Persistent service, hidden trust, cover-state API, assignments, scoped authority, emergency review, deadline suspension | Migration, full facts/incidents model, roster query, shared expense/report API, production recovery |
| EA_Dispatch | Delayed queue, physical reports/replies, archive, copy recovery, idempotent callbacks | World placement, couriers, sensitive-material routing, long-running queue retention, game save/load tests |
| EA_Service | Six duties in two packets, item deliveries, deadlines/extensions, supply authorization, status register, contextual replies and closing review | Establish Cover, investigations, major operations, repeatable workload, location/cooldown/conflict rules, other report types |
| EA_Accounts | One operation, one advance and claim, four decisions, explanation, debt, partial repayment, audit and review findings | Multi-entry ledger, operation allocation, receipt integrations, broader garnishment/rewards, ongoing audits |
| EA_Prototype | Console-placed test box and one-time supplies | Development harness only; remove from the eventual production profile |
| EA_Start | Not built | Alternate Perspective record inspection, start selection, accommodation, pre-Helgen tests |
| EA_Vice | Not built | Curated roster, permanent relationship restrictions, SFW behavior, verified optional integrations |
| EA_CivilWar | Not built | Both enlistment paths, Season Unending and Neutral Stance conflict review |
| EA_DarkBrotherhood | Not built | Elenwen-directed destruction, Maro liaison, isolated quest overrides |
| EA_Dawnguard | Not built | Operational brief, immediate/emergency decisions, reports, Harkon cleanup |
| EA_Serana | Not built | Exact Sinister Serana dependency, authored timing/disclosure/favor hooks |
| EA_MainQuest | Not built | Pro-Thalmor Diplomatic Immunity, independent removals, alias/scene safety and Blades cleanup |
| Compatibility patches | None created | Inspect actual records; create only confirmed patches |

The future vice roster is exactly Elenwen, Faralda, Brelyna, Karliah, Aranea Ienith, Jenassa, Niranye, Elisif, and Serana. No relationship behavior is changed by this prototype. ORomance and the excluded targets remain outside scope.

## Conflict inspection required before quest work

No game or dependency files were present. Every row below is an **uninspected candidate**, not a confirmed conflict, and no supported version is claimed.

| Dependency/family | Records and behavior to inspect | Acceptance evidence |
| --- | --- | --- |
| Skyrim SE/AE official masters | Target game version, quest conditions, aliases, scenes, NPC flags | Exact versions/hashes; clean xEdit error check |
| Alternate Perspective | Start registration interface, selection dialogue, destination references, Helgen activation | Existing start preserved; EA selected once; Helgen remains dormant until deliberate activation |
| Main quest and dialogue expansions | Embassy route, Delphine/Esbern/Paarthurnax ownership and aliases, peace council | Dependency graph and scene tests before any protection changes |
| Dawnguard and Harkon dialogue | Harkon's offer, player vampire/faction changes, Serana quest bindings | Uninterrupted offer; post-action reporting; continuing service state |
| Sinister Serana | Actual plugin filename/version and changed records | Required master identified from installed file; conflict-specific forwarding |
| Civil War / Season Unending Neutral Stance | Enlistment dialogue and quest gates, council outcomes | Both enlistments blocked without preventing the council |
| Dark Brotherhood expansions | Destruction conditions, Maro exchanges, rewards | Destruction route and reporting without career recruitment |
| Legacy of the Dragonborn | Affected quests and display collection requirements | Record intersection, not an assumed blanket patch |
| Courier/social/AI mods | Their documented callbacks, exact versions and record changes | No generated dialogue can invoke EA mutation functions; only required adapters included |

To unblock these modules, provide the installed game version and a load-order export (`plugins.txt` / `loadorder.txt`), plus accessible official/dependency plugins and extracted Creation Kit script sources. These files need not be committed or redistributed. Begin with a frozen development profile, inspect in xEdit and Creation Kit, and record the findings before choosing record overrides.

## Release gate

The next milestone is a clean in-game run of the prototype's paper loop, with xEdit validation and save/load, death/reload, double-activation, and lost-document tests. Production release additionally requires every quest route and compatibility test in the original specification. An automated build or passing simulated test is not a substitute for those gates.
