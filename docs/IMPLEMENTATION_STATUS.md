# Implementation status

The original build specification and its Continuation 01 are the design authority; the continuation governs where they conflict. This repository implements a bounded technical prototype of portions of baseline phases 0, 1, 3 and 4, and the out-of-game portion of Revision Phase B. **None of the specification's full in-game phase exit conditions has been certified.**

| Module | Current implementation | Remaining work |
| --- | --- | --- |
| EA_Core | Persistent service, hidden trust, cover-state API, assignments, scoped authority, emergency review, deadline suspension | Migration, full facts/incidents model, roster query, shared expense/report API, production recovery |
| EA_Dispatch | Delayed queue, physical reports/replies, archive, copy recovery, idempotent callbacks | World placement, couriers, sensitive-material routing, long-running queue retention, game save/load tests |
| EA_Service | Eleven authored packets in fixed circulation (three open at once), named vanilla items, case papers with three-conclusion judgement and misjudged replies, deadlines/extensions, supply authorization, status register, contextual replies and closing review | Establish Cover, observation/dead-drop and world-placed recovery cases, random selection among eligible packets, compromised-cover replies, major operations, location/cooldown/conflict rules |
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

## Revision Phase B: authored service pool

| Phase B requirement (Continuation 01, section 11) | Status |
| --- | --- |
| Convert generic prototype duties into fixed authored packets | Done. The flowers, firewood, leather and wheat duties and their 37 records are retired; their IDs are not reused. Alto wine became Solitude spiced wine |
| First wine/provenance job | Instruction 1002 (Solitude spiced wine, with the Accounts case) and 1004 (Black-Briar Reserve, with case papers) |
| First named-book job | Instruction 1003 (*The Rise and Fall of the Blades*); 1005 and 1006 are further book cases |
| At least one commercial-intelligence errand with a report judgement | Instructions 1004, 1008 and 1009; 1005 and 1011 are archival judgements |
| Item recovery and replay protection | Orders and case papers are archived and recoverable without duplication. Named items are consumed once, only on an accepted report. Every response and conclusion is guarded by its transaction |
| Elenwen voice checklist applied to all responses | Applied by hand to every packet and Accounts letter, and checked mechanically for signature, length, distinct variants and a starter prohibited-phrase list. The corpus-based review is Revision Phase C and needs the game's dialogue export |
| **Exit:** no launch assignment satisfied by an arbitrary common item | Met in the build: every item is one exact base object, and a test rejects a list of generic and quest-reserved forms. **Not yet confirmed in game** |
| **Exit:** at least ten polished packets circulate without repetition or duplication | Eleven packets are issued in order, at most three at a time, each exactly once; this is tested through the whole series. **Not yet played in game** |

Packet families and the launch target in section 5.4 (about thirty packets) are only partly covered:

| Family | Packets | Gap |
| --- | --- | --- |
| A. Provenance procurement | 1002, 1003 | More vintages and editions; EA-specific marked or annotated objects need hand placement |
| B. Commercial intelligence | 1004, 1008, 1009 | — |
| C. Archival and textual | 1005, 1011 | — |
| D. Observation attached to an errand | none | Needs world-placed people or objects to observe. "Observations appear only when discovered" cannot be honoured with papers alone |
| E. Recovery and denial | 1006 | A world-placed packet, codebook or ledger page needs Creation Kit placement |
| Mundane or personal duty | 1001, 1007, 1010 | — |

Spec 12.2 behaviour not yet built: random choice among eligible packets (issue order is fixed), compromised-cover reply variants (cover state belongs to Phase A), recovery of EA-specific case *items* (only papers exist so far), and optional observations.

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

The next milestone is a clean in-game run of the prototype's paper loop, including the Phase B item and case checks in TESTING.md, with xEdit validation and save/load, death/reload, double-activation, and lost-document tests. Production release additionally requires every quest route and compatibility test in the original specification. An automated build or passing simulated test is not a substitute for those gates.
