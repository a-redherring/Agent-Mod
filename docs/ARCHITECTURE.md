# Prototype architecture and state contract

Six plugins are generated from source, with explicit local FormIDs. `content/record-ids.json` is the stable record map; do not compact or renumber it in an update. Records removed from the build are listed in `content/retired-records.json`, and their IDs are never reassigned (0.2.0 retired the 37 records of the generic flowers, firewood, leather and wheat duties; 0.4.0 retired the 159 records of the packet-era job pool, Establish Cover and field papers). Runtime assignment IDs (campaign instructions 2001–2021) and dispatch subjects (2899–2907) are independent of plugin FormIDs. Core transaction IDs monotonically increase and are retained as replay guards.

Plugin headers are explicitly 1.70, all new IDs begin at 0x800, and no plugin is ESL-flagged. This avoids requiring the newer extended-ID format merely because of a library default; older runtimes can reject 1.71 headers, as documented by the [Backported Extended ESL Support project](https://github.com/Nukem9/skyrimse-backported-esl-support). Actual runtime compatibility still needs game testing.

Dependencies are `Skyrim.esm → EA_Core`; `EA_Dispatch → EA_Core`; `EA_Service / EA_Accounts → EA_Core + EA_Dispatch`; `EA_Prototype → all four`; and `EA_Start → EA_Core + EA_Dispatch + EA_Prototype`. The builder orders masters according to this graph. Core references no optional mod.

`EA_Module` is a shared Papyrus callback type in Core. Service and Accounts extend it. Dispatch stores callback instances supplied by those modules, so its plugin never masters a downstream client. All player mutations enter through the prototype controller's Busy state. No SKSE mod-event listener exposes authorization, gold, or quest changes to generated conversation. Papyrus is not a sandbox against other installed scripts: the boundary is a design/API contract, not security against malicious mods.

## Core API

| Call | Contract |
| --- | --- |
| `Commission()` | Initializes service once; repeated calls return false |
| `RegisterAssignment(id, class, dueDay)` | Rejects duplicate/nonpositive IDs, invalid classes and capacity overflow |
| `RecordFact(id, 1)` | One authored fact per assignment; no player free text |
| `FileAssignment(id)` | Requires open assignment and recorded fact |
| `CompleteAssignment(id)` | Requires filed status; applies success once |
| `GetAuthority(operation, category)` | Returns only a matching unexpired grant; zero means no authority |
| `GrantAuthority(operation, category, mode, expiryDay)` | Trusted authored EA code only; no user/generated dialogue route |
| `RecordEmergency` / `ReviewEmergency` | Immediate authorized choice followed by explicit accountability |
| `RefreshDeadlines(nowDay)` | Marks active overdue once; no hard failure. Assignments registered with due day 0 have no deadline |
| `SuspendDeadlines` / `ResumeDeadlines` | Balanced nested scene hooks; freeze each assignment from its own pause/creation time |
| `SetCoverStatus` / cover queries | Set established by the sealed packet and by the console commission; compromise is not yet used |
| `AdjustTrust(delta)` | Hidden trust; never displayed |

Classes: 1 major (capacity 1), 2 routine intelligence (capacity 3), 3 duty (capacity 6), 4 standing campaign instruction (capacity 32 open at once; open across phases until reported). States: 0 unknown, 1 active, 2 overdue, 3 report filed, 4 completed; 5 withdrawn and 6 failed are reserved, with no implemented transition yet. Categories: 1 investigation, 2 disclosure, 3 removal, 4 faction commitment, 5 expenditure. Modes: 1 standing, 2 prior, 3 emergency. Mode 3 is accepted only by explicit emergency handling; it is not automatically interchangeable with prior permission.

Prototype limits: 64 lifetime assignments, 64 authority keys, 128 lifetime dispatch transactions, 128 unique retained document forms, 32 campaign instructions open at once (21 authored), 128 campaign conditions (checked by the builder), eight instruction positions in the report menu, and one accounting case. Slots are not recycled: exhaustion refuses new work rather than losing replay history. A long-running production workload requires a versioned retention design. Campaign instructions have no deadline. Deadlines that exist catch up at dispatch interaction; responses use one-shot game-time notifications and are also checked on collection. There are no continuously polling update loops.

Dispatch reserves document slots for both the outgoing paper and its future reply before accepting a transaction. A reserved reply remains unavailable for recovery until it has actually been delivered. This makes catalogue exhaustion fail before accepting unrecoverable correspondence.

Deadline suspension supports balanced nested brackets. Each assignment records when its clock froze, so new work issued during a pause does not receive time from before it existed, and an extension during a pause does not count elapsed time twice. Time resumes after the final matching resume call. An extra resume is a no-op; a missing resume still requires diagnosis by the caller. No vanilla scene hooks exist in this build, and no campaign instruction has a deadline to suspend.

## Documents and transactions

The physical order exists before a report can be filed. A report is accepted only when its conditions hold (see "Campaign"); deliveries are removed from the player only after dispatch accepts the report. Removed items are consigned permanently; the player-accessible archive contains documents only. Filing commits a transaction ID, subject, authored outcome, response book, recipient callback, and arrival day. Arrival only notifies; collection delivers the response and applies its callback once.

`Dispatch.Send(transactionID, subjectID, letter, receiver)` queues a letter that answers no report. It is ready at once, the player is told "Something has been left in the dispatch case.", and it is collected like any reply (Check Correspondence), which runs the receiver's callback once. It reserves the letter's document slot like a reply.

Queue state 1 is in transit/awaiting collection, 2 is claimed while its callback executes, and 3 is delivered. Both receivers require a positive transaction ID, a due state-2 dispatch, matching recipient, subject and outcome, and their own expected request ID. Accounts marks a settlement final before transferring gold. Prior authorization (mode 2) is specifically required for the advance. An interrupted callback can be retried by a gated development function without intentionally replaying final payments. Real VM interruption timing remains an in-game test requirement; this is not a transactional game-inventory database.

The document catalog permits reprints even if both player and archive copies were removed. Reprints do not call response callbacks. Distinct authored BOOK records carry known facts, declarations and decisions. The meal explanation/decision records match the selected declaration and allowance. This prototype does not generate free-form prose or dynamic receipt totals. The Accounts statement uses a native message with actual money figures. Return receipts still refer to the current statement rather than printing unique transaction totals.

Notifications check that a due response still exists. The minimum scheduled callback interval is 0.1 game hour; collection independently checks the exact arrival time.

## Accounting rules

Accounts is parameterised by the plugin: `OperationID` (the Core assignment the advance is for), `AdvanceAmount`, `ClaimAmounts` for the four claim forms, `AllowedAmount` for the inflated claim and `ExplainedAllowance` for an explained meal. The campaign sets the operation to instruction 2007 (hiring the Dunmer), with a 500-septim advance. The advance needs prior authority (category 5, mode 2) on that operation, which the release letter grants, and the instruction must still be open. A claim needs the instruction's report filed or completed. The one-time 100-septim allowance from the packet is separate.

Claims are declarations. The fee declared at 500 is approved; 650 receives 500; a 60-septim gift is denied; a 40-septim meal is returned for explanation, then may receive 20 or be denied.

For a final claim, `funded = min(claimed, outstanding advance)`. Remove that amount from the advance. Allowed amounts up to the funded portion discharge the advance; denied funded portions become debt. Only allowed amounts exceeding the funded portion can become cash, after discharging an existing audited liability. A denied self-funded claim does not invent a debt to the Embassy. Returning money reduces the actual outstanding advance/debt and removes no more gold than the player has. `ReturnAmount(maximum)` caps each payment at the requested amount (10 or 25 from the menu); zero means all affordable outstanding funds and a negative value is rejected. The original zero-argument `ReturnFunds()` delegates to the all-funds path. The confirmation message shows the amount actually removed and balance left, while the physical receipt refers to the live statement.

An audit occurs on the next interaction after fourteen days, once per advance. Only actual claim/explanation return transit defers it, for at most that dispatch's one-day journey. An uncollected response or unanswered explanation does not suspend the debt. A later valid claim can discharge allowed costs against an audited balance. Audit notices are collected locally, without a courier integration.

## Opening: Alternate Perspective start (EA_Start)

`EA_Start.esp` masters Skyrim, Core, Dispatch and Prototype, and overrides nothing. The package registers its start with Alternate Perspective through `SKSE/AlternatePerspective/ElenwenAgent.json` (generated from `content/start.json`). Alternate Perspective is never a master, so the plugin loads safely without it; the start quest simply never runs.

`EA_StartQuest` is not start-game enabled. Alternate Perspective calls `Start()`. Stage 10 is the start-up stage, and its fragment (`EA_Opening.Fragment_10`) runs the handoff:
- add the player to `MS09NorthwatchFaction`;
- move the player to alias 1, the Northwatch Keep map marker;
- issue a dagger and the sealed packet;
- show the first objective.

Alias 0 is `NorthwatchKeepLocation`, and alias 1 is filled as a location-alias reference of `MapMarkerRefType`. If it cannot fill, the quest fails to start, and Alternate Perspective reports this and falls back to its Helgen inn.

The faction membership is the same reversible device Alternate Perspective uses (`APAddFactionWhileInLoc`). A single-update chain removes it once the player is more than 4,096 units from the marker, and it is never re-added. Northwatch's own quest therefore meets the keep as vanilla left it. No MQ101, Helgen or Alternate Perspective record is touched.

Reading the sealed packet (`EA_SealedPacket.OnRead` → `EA_Opening.OpenPacket`) works only after the handoff, and only once. It starts Core, Dispatch and Service if needed, then:
- `Core.Commission()` and `Core.SetCoverStatus(True, False)`: the civilian papers are his cover, and there is no Establishment Report;
- issues `PacketPapers` (the residence order, civilian papers, conditional release and case instructions) and `PacketBooks` (vanilla books to read, not archived);
- issues the `Allowance` (100 septims) and the dispatch case;
- calls `Service.BeginCampaign()`, which issues the Riverwood instructions;
- completes objective 10 and sets stage 20, which completes the start quest.

The controller has no separate opening mode. Without the start, the console-placed box offers the commission once (Core commissioned, cover set, the commission paper and 100 septims), then calls `Service.BeginCampaign()`; the controller calls it on every use, and it acts only once.

**Dispatch case.** `EA_DispatchCaseItem` (Prototype) carries `EA_DispatchCase`. When it leaves the player's inventory for the world, the controller places the dispatch box where it lies, deletes the case reference, and moves and enables the archive beside the box. Case and archive → Pack the case returns the item, deletes the box and disables the archive; filed papers remain in it. Open filed correspondence activates the archive from the box.

## Campaign (EA_Service)

`content/campaign.json` is the source for the campaign; `Elenwen_Agent_Campaign_Opening.md` is its design. It holds instructions, letters, the wander letter, the Arcanaeum book list, the inn and leash Locations, the advance and removal operation IDs, the packet books and Service's messages.

**Phases.** 1 Riverwood residence, 2 released (Markarth), 3 interval, 4 College. `BeginCampaign()` sets phase 1 once the service is commissioned, and records Most Gold Carried as the earnings baseline. Instruction *i* belongs to one phase and is Core assignment 2001 + *i*, class 4, with no deadline. Whenever the state is evaluated (when the campaign begins, on waking, on arrival and on collecting a reply or letter), every unissued instruction of the current phase is issued, unless its `RequireCond` fails (used for an optional plugin that is absent). Issuing reserves and archives the order, registers the assignment and shows objective 100 + *i*. Instructions stay open across phases until reported. The officer is an underling: orders direct, replies acknowledge, restrict or redirect, and nothing explains what a report meant.

**Conditions.** Instructions and letters own consecutive ranges of one flat condition table (`CondKinds`, `CondForms`, `CondOtherForms`, `CondValues`, `CondPlugins`, `CondFormIDs`). Conditions read vanilla state and never change it. The kinds are:

| # | Kind | # | Kind |
| --- | --- | --- | --- |
| 1 | nights slept at the inn | 12 | actor dead |
| 2 | days of residence (plus wander delay) | 13 | actor alive |
| 3 | visited a place (or inside it) | 14 | global at least |
| 4 | deliver an item, or any of a form list | 15 | earned money (Most Gold Carried above baseline) |
| 5 | hold an item | 16 | player level |
| 6 | quest stage done | 17 | best magic school (base value) |
| 7 | quest begun (running, completed or stage above 0) | 18 | days in phase |
| 8 | quest not begun | 19 | phase weight |
| 9 | player in faction | 20 | form present (optional plugin loaded) |
| 10 | actor in faction | 21 | quest completed |
| 11 | actor holds item | 22 | quest stage at least |

A form from a plugin that may be absent (At Your Own Pace, College of Winterhold - Quest Expansion) is named by file and local ID and resolved with `Game.GetFormFromFile`; neither is a master. An unresolved form fails every kind except "not begun".

**Reports.** `FileReport(i)` requires an issued, open instruction with no report yet, and all its conditions holding at filing. Conditions are not measured from the order, so something done before the order counts. Otherwise filing is refused: 0 not issued, 1 already filed or closed, 2 dispatch could not accept it, 3 not yet (the instruction's own `NotYetMessages` entry, which says nothing has been filed). If `AltCond` holds at filing, the alternative reply is queued (outcome 2) instead of the ordinary one (outcome 1). An accepted report removes its deliveries, records the fact, files the assignment and swaps objective 100 + *i* for 200 + *i*. Collecting the reply a day later completes the assignment and both objectives. An ordinary outcome adds the instruction's `Weights` to the phase weight; an alternative adds `AltWeights` and applies `AltTrust`.

**Letters.** Letter *j* belongs to a phase and is sent with `Dispatch.Send` as subject 2900 + *j*, once, when its conditions hold. Collecting it adds its enclosures (vanilla books, from `EnclosureStart`/`EnclosureCount` into `Enclosures`) and applies its action once: 1 next phase; 2 next phase and advance authority (`AdvanceOperation`, category 5, mode 2); 3 removal authority (`RemovalOperation`, category 3, mode 2). A letter with no conditions is sent as soon as its phase begins.

**Residence and leash.** `EA_ServicePlayer`, on the Service quest's forced player alias, registers for sleep on init and on load. `OnSleepStop` calls `Service.OnWake()`; in phase 1, waking at the inn Location (or inside it) counts a night, and the first such night starts the residence. `OnLocationChange` calls `RecordVisit`, which marks visited conditions and then checks the leash. In phase 1, after the residence has started, leaving the `Bounds` (Whiterun and Falkreath holds) adds three days to the residence requirement and costs one trust, once per absence; a wander letter (subject 2899, no callback effect) is sent at most every three game days. There is no recall and no dismissal.

**Menus.** File Report lists open instructions in eight positions: those whose conditions already hold first, then the rest, each in issue order. The menu text shows each position's instruction number, or 0 for an empty position; choosing an empty position does nothing. Review status shows counts of open, filed and closed instructions and correspondence waiting.

Objectives are 100 + *i* (order) and 200 + *i* (reply awaited).

The larger runtime arrays and the new phase state require a fresh save; no prior-version state migration is implemented.

## Development recovery

Use only on throwaway test saves. A busy controller normally retains its running Papyrus stack through save/load. If a stack demonstrably aborted, inspect the Papyrus log before intervention. The console can call `cqf EA_PrototypeQuest GoToState ""` to unlock the controller after the stack is no longer running. This does not repair a partially completed inventory operation.

`EA_Dispatch.DebugRecoverPending(transactionID)` operates only on a state-2 transaction and only with `EA_Core.DebugEnabled` explicitly enabled in a debug build/CK property. Enable debug logging in the same way; normal builds leave it false. Recovery is deliberately absent from normal menus. Do not reset controller or transaction variables indiscriminately, replay commissioning, or stop/restart the framework quests.

## Tooling sources

[Caprica v0.3.0](https://github.com/Orvid/Caprica/releases/tag/v0.3.0) compiles the Skyrim target. One miscompilation was found: a comparison whose two sides were a call result and another comparison shared one temporary register. Code avoids that shape, and a plugin test scans the emitted assembly for it. [Mutagen's source](https://github.com/Mutagen-Modding/Mutagen) supplies typed plugin schemas and binary serialization. The upstream [Skyrim SE FormKeys](https://github.com/Mutagen-Modding/Mutagen.Bethesda.FormKeys/tree/release/Mutagen.Bethesda.FormKeys.SkyrimSE/Skyrim) identify Gold001 (`00000F`) and HighPolyNote (`097788`); the campaign's vanilla forms come from those lists and the Fandom wiki:

| Use | Form | FormID |
| --- | --- | --- |
| Inn | Riverwood Sleeping Giant Inn Location | `01CB8C` |
| Leash | Whiterun Hold, Falkreath Hold Locations | `016772`, `01676F` |
| Places | Whiterun, Markarth, Markarth Talos shrine, Understone Keep | `018A56`, `018A59`, `06E830`, `01F316` |
| Places | Winterhold longhouse, the Frozen Hearth | `01EB7D`, `01EB7C` |
| Quests | MS01, MS02, DA11, MQ106 | `018B4B`, `040A5E`, `02C358`, `032926` |
| Quests | MG01–MG04, MG07, MG08 (MG06 was not found in the FormKeys list; the adviser letter waits for MG07 to begin) | `01F251`–`01F254`, `01F257`, `01F258` |
| Actors | Jenassa (reference), Madanach, Verulus, Ondolemar | `0E1BA9`, `019916`, `01BB8F`, `01990D` |
| Factions | CurrentHireling, Arch-Mage | `0BD738`, `103372` |
| Items | Thalmor Orders (Sanyon), Ogmund's amulet | `097803`, `064796` |
| Books (packet, enclosures) | Madmen of the Reach, Bear of Markarth, Red Eagle | `07EB03`, `07EB9E`, `0C1771` |
| Books (enclosures) | Falmer study, Dwemer Inquiries I | `0E0D68`, `0E7F31` |
| Books (Arcanaeum list) | Dragon Language, Alduin is Real, Dragon War, Mysterious Akavir | `0EF2C0`, `0EA5B0`, `0EDDD5`, `01ACD4` |
| Optional | At Your Own Pace global (Tolfdir Arch-Mage); CQE reading quest | local `000813`; local `000870` |

None of these has been checked against Skyrim.esm. Before release, each must be confirmed in xEdit: the form is the one named, each Location covers the place the order describes, each quest stage means what the condition assumes, and the optional plugins' local IDs match the installed versions. No proprietary game assets or base scripts are distributed.
