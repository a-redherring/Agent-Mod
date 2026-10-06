# Implementation status

The original build specification, its Continuation 01 and the **Revised Implementation Plan** are the design authority. Where they conflict, the newest governs, and the revised plan sets the build order (phases A–I). This repository implements a bounded technical prototype of parts of baseline phases 0, 1, 3 and 4. It also covers the out-of-game parts of revised-plan Phase A (the start), and part of Phase C (authored jobs, built earlier as Continuation 01's Revision Phase B). **None of the specification's full in-game phase exit conditions has been certified.**

| Module | Current implementation | Remaining work |
| --- | --- | --- |
| EA_Core | Persistent service, hidden trust, cover-state API, assignments, scoped authority, emergency review, deadline suspension | Migration, full facts/incidents model, roster query, shared expense/report API, production recovery |
| EA_Dispatch | Delayed queue, physical reports/replies, archive, copy recovery, idempotent callbacks | World placement, couriers, sensitive-material routing, long-running queue retention, game save/load tests |
| EA_Service | Twelve authored instructions in fixed circulation (three open at once), written for an underling: named places (counted on arrival after the order), named vanilla items, and three leads into vanilla quests of Thalmor interest. Also deadlines/extensions, supply authorization, status register, contextual replies and closing review | Eligibility rules and cooldowns, more leads (vampire casework, Dark Brotherhood contact, Civil War observation), world-placed objects, compromised-cover replies |
| EA_Accounts | One operation, one advance and claim, four decisions, explanation, debt, partial repayment, audit and review findings | Multi-entry ledger, operation allocation, receipt integrations, broader garnishment/rewards, ongoing audits |
| EA_Prototype | Console-placed test box and one-time supplies | Development harness only; remove from the eventual production profile |
| EA_Start | Alternate Perspective start outside Northwatch (registration JSON, start-up stage, map-marker alias, reversible Northwatch courtesy), journal recap, sealed packet, Establish Cover with evidence-checked report, assessment, portable dispatch case | In-game validation; hand-placed lodgings or world objects; corrective follow-up if the plan wants one |
| EA_Vice | Not built | Curated roster, permanent relationship restrictions, SFW behavior, verified optional integrations |
| EA_CivilWar | Not built | Both enlistment paths, Season Unending and Neutral Stance conflict review |
| EA_DarkBrotherhood | Not built | Elenwen-directed destruction, Maro liaison, isolated quest overrides |
| EA_Dawnguard | Not built | Operational brief, immediate/emergency decisions, reports, Harkon cleanup |
| EA_Serana | Not built | Exact Sinister Serana dependency, authored timing/disclosure/favor hooks |
| EA_MainQuest | Not built | Pro-Thalmor Diplomatic Immunity, independent removals, alias/scene safety and Blades cleanup |
| Compatibility patches | None created | Inspect actual records; create only confirmed patches |

The future vice roster is exactly Elenwen, Faralda, Brelyna, Karliah, Aranea Ienith, Jenassa, Niranye, Elisif, and Serana. No relationship behavior is changed by this prototype. ORomance and the excluded targets remain outside scope.

## Revised plan progress

| Revised plan phase | Status |
| --- | --- |
| A. Start revision ("Arrival and First Posting") | Built and tested in the simulator: Northwatch start, journal recap, civilian equipment, packet, Establish Cover, Establishment Report, dispatch introduction, assessment, then the first instructions. **Not yet run in game** |
| B. Elenwen style pass | Letters were written against the Continuation 01 voice guide. The vanilla dialogue corpus and internal style sheet need the game's dialogue export |
| C. Authored service jobs | 12 of 20–30 built (below). Eligibility rules and cooldowns are not yet built; issue order is fixed |
| D. Accounts refinement | The Accounts case is tied to the spiced wine job; claims have not yet been spread across more jobs |
| E–I | Not started; the main quest stays last |

The plan's milestone list maps onto the build as follows. Steps 1–4 are the start-up stage, journal and packet. Step 5 is the Northwatch courtesy ending. Steps 6–8 are the Establishment Report checks. Step 9 is the assessment. Step 10 is Collect Orders, which issues instructions 1001–1003.

## Job pool and the underling design (2026-10-06)

Two design decisions changed the job pool after 0.2.0:
- **The player is an underling, not an analyst.** Orders give directions (who or what, and where), not reasons. Reports state what was done, and Elenwen's replies do not say what it meant. The 0.2.0 case papers and three-answer conclusions are removed and their records retired. This supersedes Continuation 01, section 5.1, which asked orders to answer at least three "why" questions.
- **Investigations lead into vanilla quests the Thalmor care about.** The instruction sends the player toward the quest and waits until it has begun. It reads the vanilla quest's state and never changes it.

| # | Instruction | Kind | Rests on |
| --- | --- | --- | --- |
| 1001 | Field Protocol | administrative | Reading the field papers |
| 1002 | Solitude Spiced Wine | procurement (Accounts case) | 3 bottles |
| 1003 | Trouble in Markarth | **lead** | Markarth, then *The Forsworn Conspiracy* begun |
| 1004 | A Public History | procurement | *The Rise and Fall of the Blades* |
| 1005 | Honningbrew | verification | Honningbrew Meadery, 2 bottles |
| 1006 | The College of Winterhold | **lead** | Winterhold, then *First Lessons* begun |
| 1007 | A Title in Circulation | procurement | *The Rising Threat, Vol. I* |
| 1008 | A Book from Whiterun | procurement | Whiterun, *The Book of the Dragonborn* |
| 1009 | For the Table | personal favor | 6 jazbay grapes |
| 1010 | A Family in Whiterun | **lead** | Whiterun, then *Missing in Action* begun |
| 1011 | The Windhelm Caravan | verification | Windhelm stables, 1 moon sugar |
| 1012 | Paper | administrative | 1 roll of paper |

**Candidate leads for later phases.** These are not built, because they belong to unbuilt modules or need their policy first:
- Aventus Aretino's Black Sacrament in Windhelm, leading to Dark Brotherhood contact (Phase E);
- vampire attacks and Fort Dawnguard rumours (Phase G);
- observing either Civil War camp without enlisting (Phase F);
- Heimskr's Talos preaching in Whiterun, which has no vanilla quest and would need an EA-authored follow-up.

The main quest is never a lead target.

**Known tension.** *Missing in Action* ends with Thorald Gray-Mane freed from Northwatch. The 1010 reply forbids going near Northwatch, but the vanilla quest still allows it. How Elenwen reacts if the player does it is left for a later module.

## Conflict inspection required before quest work

No game or dependency files were present. Every row below is an **uninspected candidate**, not a confirmed conflict, and no supported version is claimed.

| Dependency/family | Records and behavior to inspect | Acceptance evidence |
| --- | --- | --- |
| Skyrim SE/AE official masters | Target game version, quest conditions, aliases, scenes, NPC flags | Exact versions/hashes; clean xEdit error check |
| Alternate Perspective | **Inspected 2026-10-05: version 4.1.0 (Nexus 50307), see below** | Register EA start by JSON; verify Helgen stays dormant in game |
| Main quest and dialogue expansions | Embassy route, Delphine/Esbern/Paarthurnax ownership and aliases, peace council | Dependency graph and scene tests before any protection changes |
| Dawnguard and Harkon dialogue | Harkon's offer, player vampire/faction changes, Serana quest bindings | Uninterrupted offer; post-action reporting; continuing service state |
| Sinister Serana | Actual plugin filename/version and changed records | Required master identified from installed file; conflict-specific forwarding |
| Civil War / Season Unending Neutral Stance | Enlistment dialogue and quest gates, council outcomes | Both enlistments blocked without preventing the council |
| Dark Brotherhood expansions | Destruction conditions, Maro exchanges, rewards | Destruction route and reporting without career recruitment |
| Legacy of the Dragonborn | Affected quests and display collection requirements | Record intersection, not an assumed blanket patch |
| Courier/social/AI mods | Their documented callbacks, exact versions and record changes | No generated dialogue can invoke EA mutation functions; only required adapters included |

### Alternate Perspective 4.1.0 findings

Inspected from the distributed archive (`AlternatePerspective.esp`, its Papyrus sources and SKSE configuration). The archive is not committed or redistributed.

- **Plugin:** `AlternatePerspective.esp`, form version 1.71, not ESM- or ESL-flagged, masters Skyrim, Update, Dawnguard, HearthFires and Dragonborn. 6,344 records.
- **Runtime requirements:** SKSE and JContainers. The start menu is an SKSE custom menu. Without JContainers, only AP's default starts are offered.
- **Start registration (4.0 and later):** AP lists every `.json` file in `Data/SKSE/AlternatePerspective/`, validated by its `Schema/schema.json`. An entry gives `mod` (plugin file name), `text` (card headline), `description`, an optional `color`, and either an `id` (start quest FormID, local to that plugin) or `suboptions` of `{text, id}`. The older `APAddToQueue` helper script is deprecated.
- **Launch contract:** when the player leaves AP's start cell, `APMessengerUtil.enterGame()` calls `Start()` on the selected quest. That quest must move the player out of the start cell within about five seconds, or AP moves the player to the Helgen inn. AP then requests a save. AP's own starts do this in their first stage fragment (`MoveTo` a reference alias) and then stop.
- **Consequence for EA:** `EA_Start.esp` does not need AP as a master. A JSON file naming the EA start quest is enough, and the quest can stand on its own without AP (it simply never runs). Core keeps its single Skyrim.esm master.
- **Helgen:** AP replaces the vanilla MQ101 fragment script. Under a non-Helgen start, the dragon attack begins only when the player deliberately sleeps in the Helgen inn bed (`APStartIntroBedScript`, MQ101 stage 3) or uses AP's explicit skip triggers. This matches the specification's delayed activation, but the EA start must not touch MQ101, Helgen or AP's records. To be confirmed in game.
- **Conflict note:** AP's own "Guilds" starts (College, Thieves Guild, Dark Brotherhood, Companions) and "Home" starts change faction and house state at game start. A cover route that checks College membership must therefore read the actual faction or quest state, not assume it was earned after the EA start. This also concerns the Brotherhood doctrine.

To unblock these modules, provide the installed game version and a load-order export (`plugins.txt` / `loadorder.txt`), plus accessible official/dependency plugins and extracted Creation Kit script sources. These files need not be committed or redistributed. Begin with a frozen development profile, inspect in xEdit and Creation Kit, and record the findings before choosing record overrides.

## Release gate

The next milestone is a clean in-game run of the prototype's paper loop, including the Phase B item and case checks in TESTING.md, with xEdit validation and save/load, death/reload, double-activation, and lost-document tests. Production release additionally requires every quest route and compatibility test in the original specification. An automated build or passing simulated test is not a substitute for those gates.
