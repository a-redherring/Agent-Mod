# Implementation status

The original build specification, its Continuation 01 and the **Revised Implementation Plan** are the design authority. Where they conflict, the newest governs, and the revised plan sets the build order (phases A–I). This repository implements a bounded technical prototype of parts of baseline phases 0, 1, 3 and 4. It also covers the out-of-game parts of revised-plan Phase A (the start) and the campaign designed in `Elenwen_Agent_Campaign_Opening.md`: Riverwood, Markarth, an interval and the College of Winterhold. **None of the specification's full in-game phase exit conditions has been certified.**

| Module | Current implementation | Remaining work |
| --- | --- | --- |
| EA_Core | Persistent service, hidden trust, cover-state API, assignments (including class 4 standing instructions, 32 open), scoped authority, emergency review, deadline suspension | Migration, full facts/incidents model, roster query, shared expense/report API, production recovery |
| EA_Dispatch | Delayed queue, physical reports/replies, unsolicited letters (`Send`), archive, copy recovery, idempotent callbacks | World placement, couriers, sensitive-material routing, long-running queue retention, game save/load tests |
| EA_Service | The campaign: four phases, 21 instructions and 8 letters gated by conditions read from vanilla state (nights at the inn, residence days, visits, deliveries, quest stages and outcomes, factions, actors, level, magic skill, optional-plugin globals and quests). Alternative replies with trust and phase-weight effects, enclosed books, the Riverwood leash, the release with advance authority, the removal authority for the adviser, status counts | In-game validation of every vanilla FormID and stage; later arcs (Civil War, Dark Brotherhood, Dawnguard, main quest); compromised-cover replies; forged-letter hook |
| EA_Accounts | One operation (hiring the Dunmer, 500-septim advance), one claim, four decisions, explanation, debt, partial repayment, audit. Operation and amounts are plugin properties | Multi-entry ledger, operation allocation, receipt integrations, broader garnishment/rewards, ongoing audits |
| EA_Prototype | Dispatch case controller; console-placed test box with one-time commission and supplies | Development harness only; remove from the eventual production profile |
| EA_Start | Alternate Perspective start outside Northwatch (registration JSON, start-up stage, map-marker alias, reversible Northwatch courtesy), journal recap of the prisoner premise, sealed packet with the residence order, civilian papers, conditional release, two books, allowance and portable dispatch case; opening it begins the campaign | In-game validation |
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
| A. Start revision ("Arrival and First Posting") | Built and tested in the simulator, revised for the prisoner premise: Northwatch release, journal recap, packet, dispatch case, then the Riverwood instructions. The Establish Cover report was removed in 0.4.0. **Not yet run in game** |
| B. Elenwen style pass | Letters were rewritten against her vanilla lines (campaign doc, "Her voice") and follow the letter tradecraft rules. The full dialogue export is still needed for a final pass |
| C. Authored service jobs | Replaced by the campaign: 21 instructions in three active phases |
| D. Accounts refinement | The Accounts case is now the Dunmer's fee; claims are not yet spread across more jobs |
| E–I | Not started; the main quest stays last |

## The campaign (0.4.0)

`content/campaign.json` implements the design in `Elenwen_Agent_Campaign_Opening.md`.

| Phase | Instructions | Letters |
| --- | --- | --- |
| 1 Riverwood | 2001 Inn, 2002 Proprietor, 2003 Neighbours, 2004 Preacher, 2005 Roads, 2006 Hillside (Sanyon's orders) | Settled; Release (encloses *The Red Eagle*, grants the advance authority) |
| 2 Markarth | 2007 Dunmer (hire Jenassa), 2008 Market, 2009 OldMan (Madanach freed, or killed as the alternative), 2010 Feast, 2011 Skald (amulet to Ondolemar), 2012 Shrine, 2013 Translator (Calcelmo, optional) | Reach; Interval (when the phase weight is reached) |
| 3 Interval | none | College (after seven days and magic skill 20; encloses two books) |
| 4 College | 2014 Admission, 2015 Saarthal, 2016 Books, 2017 Monk, 2018 Eye, 2019 Library (an Arcanaeum book), 2020 Town, 2021 Lesson (CQE only) | Adviser (removal authority), Declined (At Your Own Pace: Tolfdir made Arch-Mage), Accepted |

**Implemented differently from the design, or not at all:**
- **Courier.** Orders and letters arrive in the dispatch case, not by the vanilla courier; no courier integration exists.
- **Unsolicited finds.** All of a phase's instructions are issued when the phase begins, and conditions are checked when a report is filed, not from the order. Something done early (Sanyon's orders found before Riverwood ends) therefore counts. There is no separate unsolicited report.
- **Remark letters** on suggested reading were dropped. Suggested books are named in letters and never checked.
- **Ancano** is covered by removal authority only; EA never kills or changes him, and the vanilla College quests decide his fate.
- **Optional plugins.** At Your Own Pace and College of Winterhold - Quest Expansion are read with `Game.GetFormFromFile`, never as masters. Their local IDs (`000813`, `000870`) and behaviour were read from their archives and are untested in game. Without CQE, instruction 2021 is never issued; without AYOP, the Declined letter waits on a global that never resolves.
- **Vanilla FormIDs** (listed in ARCHITECTURE.md) come from Mutagen FormKeys lists and the Fandom wiki. None has been checked against Skyrim.esm, and neither have the quest stages the conditions use.

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

The next milestone is a clean in-game run of the start and the Riverwood phase, then Markarth and the College, following TESTING.md, with xEdit validation and save/load, death/reload, double-activation, and lost-document tests. Production release additionally requires every quest route and compatibility test in the original specification. An automated build or passing simulated test is not a substitute for those gates.
