# Prototype architecture and state contract

Six plugins are generated from source, with explicit local FormIDs. `content/record-ids.json` is the stable record map; do not compact or renumber it in an update. Records removed from the build are listed in `content/retired-records.json`, and their IDs are never reassigned (0.2.0 retired the 37 records of the generic flowers, firewood, leather and wheat duties). Runtime assignment IDs 1001–1011 are independent of plugin FormIDs. Core transaction IDs monotonically increase and are retained as replay guards.

Plugin headers are explicitly 1.70, all new IDs begin at 0x800, and no plugin is ESL-flagged. This avoids requiring the newer extended-ID format merely because of a library default; older runtimes can reject 1.71 headers, as documented by the [Backported Extended ESL Support project](https://github.com/Nukem9/skyrimse-backported-esl-support). Actual runtime compatibility still needs game testing.

Dependencies are `Skyrim.esm → EA_Core`; `EA_Dispatch → EA_Core`; `EA_Service / EA_Accounts → EA_Core + EA_Dispatch`; `EA_Prototype → all four`; and `EA_Start → EA_Core + EA_Dispatch + EA_Prototype`. The builder orders masters according to this graph. Core references no optional mod.

`EA_Module` is a shared Papyrus callback type in Core. Service and Accounts extend it. Dispatch stores callback instances supplied by those modules, so its plugin never masters a downstream client. All player mutations enter through the prototype controller's Busy state. No SKSE mod-event listener exposes authorization, gold, or quest changes to generated conversation. Papyrus is not a sandbox against other installed scripts: the boundary is a design/API contract, not security against malicious mods.

## Core API

| Call | Contract |
| --- | --- |
| `Commission()` | Initializes service once; repeated calls return false |
| `RegisterAssignment(id, class, dueDay)` | Rejects duplicate/nonpositive IDs, invalid classes and capacity overflow |
| `RecordFact(id, 1)` | One authored fact per prototype assignment; no player free text |
| `FileAssignment(id)` | Requires open assignment and recorded fact |
| `CompleteAssignment(id)` | Requires filed status; applies success once |
| `GetAuthority(operation, category)` | Returns only a matching unexpired grant; zero means no authority |
| `GrantAuthority(operation, category, mode, expiryDay)` | Trusted authored EA code only; no user/generated dialogue route |
| `RecordEmergency` / `ReviewEmergency` | Immediate authorized choice followed by explicit accountability |
| `RefreshDeadlines(nowDay)` | Marks active overdue once; no hard failure |
| `SuspendDeadlines` / `ResumeDeadlines` | Balanced nested scene hooks; freeze each assignment from its own pause/creation time |
| `SetCoverStatus` / cover queries | Storage for later validated hooks; prototype does not establish cover |

Classes: 1 major (capacity 1), 2 routine intelligence (capacity 3), 3 duty (capacity 6). States: 0 unknown, 1 active, 2 overdue, 3 report filed, 4 completed; 5 withdrawn and 6 failed are reserved, with no implemented transition yet. Categories: 1 investigation, 2 disclosure, 3 removal, 4 faction commitment, 5 expenditure. Modes: 1 standing, 2 prior, 3 emergency. Mode 3 is accepted only by explicit emergency handling; it is not automatically interchangeable with prior permission.

Prototype limits: 64 lifetime assignments, 64 authority keys, 128 lifetime dispatch transactions, 128 unique retained document forms, sixteen packet positions in Service's arrays (twelve authored), three open instructions at once, and one accounting case. Slots are not recycled: exhaustion refuses new work rather than losing replay history. A long-running production workload requires a versioned retention design. Deadlines catch up at dispatch interaction; responses use one-shot game-time notifications and are also checked on collection. There are no continuously polling update loops.

Dispatch reserves document slots for both the outgoing paper and its future reply before accepting a transaction. A reserved reply remains unavailable for recovery until it has actually been delivered. This makes catalogue exhaustion fail before accepting unrecoverable correspondence.

Deadline suspension supports balanced nested brackets. Each assignment records when its clock froze, so new work issued during a pause does not receive time from before it existed, and an extension during a pause does not count elapsed time twice. Time resumes after the final matching resume call. An extra resume is a no-op; a missing resume still requires diagnosis by the caller. No vanilla scene hooks exist in this build.

## Documents and transactions

The physical order exists before a report can be filed. A report is backed by an OnRead fact or actual consigned supplies. Reading field papers is remembered even before collecting the protocol order. Supply removal consigns the items permanently; the player-accessible archive contains documents only. Filing commits a transaction ID, subject, authored outcome, response book, recipient callback, and arrival day. Arrival only notifies; collection delivers the response and applies its callback once.

Queue state 1 is in transit/awaiting collection, 2 is claimed while its callback executes, and 3 is delivered. Both receivers require a positive transaction ID, a due state-2 dispatch, matching recipient, subject and outcome, and their own expected request ID. Accounts marks a settlement final before transferring gold. Prior authorization (mode 2) is specifically required for the advance. An interrupted callback can be retried by a gated development function without intentionally replaying final payments. Service also reconciles completed journal objectives on recovery. Real VM interruption timing remains an in-game test requirement; this is not a transactional game-inventory database.

The document catalog permits reprints even if both player and archive copies were removed. Reprints do not call response callbacks. Distinct authored BOOK records carry known facts, declarations and decisions. All six assignments have their own extension forms and decisions, and the meal explanation/decision records match the selected declaration and allowance. This prototype does not generate free-form prose or dynamic receipt totals. The Accounts statement uses a native message with actual money figures. Return receipts still refer to the current statement rather than printing unique transaction totals.

A second extension request receives a refusal; further requests for that instruction are rejected locally so they cannot exhaust the shared queue. Notifications check that a due response still exists. The minimum scheduled callback interval is 0.1 game hour; collection independently checks the exact arrival time.

## Accounting rules

The one-time allowance is separate from the single 80-septim wine advance. Claims are declarations tied to an actually filed wine delivery. Supplies declared at 30 are approved; supplies declared at 80 receive 30; a 30-septim gift is denied; a meal is returned for explanation, then may receive 15 or be denied.

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

Reading the sealed packet (`EA_SealedPacket.OnRead`) issues its contents once and starts the service:
- `Core.Commission()`;
- `Core.SetOpening` registers the opening as an `EA_Module`;
- Establish Cover becomes Core assignment 900 (class 1, no deadline);
- statistics are snapshotted at that moment.

**Establishment Report.** While an opening is registered and Core has no established cover, the controller shows only File Establishment Report, Check Responses and Case and archive. The report asks for an occupation, lodgings and an attestation. It is filed only if:

| Declaration | Evidence since the packet was opened |
| --- | --- |
| Guild membership | Member of the Companions, College of Winterhold, Thieves Guild or Bards College faction |
| Trade or craft | Weapons Made + Armor Made + Potions Mixed + Magic Items Made increased by 3 |
| Hunting and provisioning | Animals Killed increased by 5 |
| Paid work | Quests Completed + Misc Objectives Completed increased by 1 |
| Study | Skill Books Read + Spells Learned + Training Sessions increased by 2 |
| Rented room | Hours Slept increased |
| Own house | Houses Owned of at least 1 |
| Guild quarters | Member of the Companions, College or Thieves Guild |
| Independent income | Most Gold Carried exceeds its value when the packet was opened |

A refused declaration names what is missing and files nothing. A filed report queues one of five reports and the matching assessment for one day's transit. Collecting the assessment completes assignment 900, sets Core's cover as established, issues the field papers, and completes the quest (stage 40). The controller then shows the full menu. The console-only prototype path presumes a cover when the commission is opened, so it is unchanged.

**Dispatch case.** `EA_DispatchCaseItem` (Prototype) carries `EA_DispatchCase`. When it leaves the player's inventory for the world, the controller places the dispatch box where it lies, deletes the case reference, and moves and enables the archive beside the box. Case and archive → Pack the case returns the item, deletes the box and disables the archive; filed papers remain in it. Open filed correspondence activates the archive from the box.

## Authored packets and circulation

`content/packets.json` is the source for every instruction. Packet index *i* is assignment 1001 + *i*; the builder rejects gaps. Each packet supplies eight papers (order, filed report, ordinary, prompt and late replies, extension request, approval and refusal) and an objective. It may also name:
- a **supply**: a fixed Skyrim.esm base object and count, with its shortage message;
- a **visit**: a vanilla Location, with a "not yet been there" message;
- a **lead**: a vanilla quest, with a "not yet involved" message. A lead always has a visit too.

A packet with none of these must be the protocol acknowledgment, which rests on the field-papers reading fact.

The officer is an underling. Orders direct rather than explain, and replies never state what a report showed, so there are no case papers and no conclusions to choose. This supersedes Continuation 01, section 5.1 (orders answering at least three "why" questions) and the case-paper judgement built in 0.2.0, whose records are retired.

Service holds the per-packet papers in parallel arrays. Optional parts are reached through `SupplyIndex`, `VisitIndex` and `LeadIndex`, which hold -1 where a packet has none; the compact `Supplies`/`SupplyCounts`/`MissingMessages`, `Locations`/`VisitMessages` and `Leads`/`LeadMessages` arrays avoid empty VMAD entries. `Orders.Length` is the authored count. Runtime arrays are allocated for sixteen packets.

**Circulation.** Collect Orders issues unissued packets in index order while fewer than three are open (active, overdue or filed and awaiting the completion reply). A packet that cannot be issued blocks every later one, so a later instruction never overtakes an earlier one. Each order and its case papers are reserved in the archive before the assignment is registered, then issued and archived together; repeat collection only recovers missing copies. A deadline starts when its order is collected. The packet notice appears once for each newly issuable packet after a position frees.

**Menus.** A native message box holds at most nine buttons, so File Report, Request Extension and Review status list the open instructions by position. The menu text shows each position's instruction number, or 0 for an empty position; choosing an empty position does nothing.

**Named items.** A supply is satisfied only by `GetItemCount` of its exact base object. Another wine, another book or a different edition of the same title does not count. The full count is removed only after dispatch accepts the report, and then recorded as the packet's fact. Shortage messages report the missing quantity and take nothing.

**Visits.** The Service quest has a forced player alias whose `EA_ServicePlayer` script passes every `OnLocationChange` to `Service.RecordVisit`. A visit counts only for an issued, still-open instruction, and only if the new location is the named one or lies inside it (`Location.IsChild`). Arriving before the order, or after the report, records nothing. Being somewhere when the order is collected does not count until the player arrives again. A counted visit also records the packet's fact.

**Leads.** A lead is read with `IsRunning()` or `IsCompleted()` on the vanilla quest; EA never sets its stages. The leads are:
- `MS01` (The Forsworn Conspiracy), from Markarth;
- `MG01` (First Lessons), from Winterhold;
- `MS09` (Missing in Action), from Whiterun.

Whatever the player does inside those questlines is their own choice. The reply only restricts. Missing in Action can end with Thorald freed from Northwatch; reconciling that with the player's loyalty belongs to a later module. No instruction may lead into the main quest.

Service failure codes: 0 uncollected, 1 closed or already filed, 2 field papers unread, 3 extension pending, 4 extension refused, 5 authority pending, 6 authority held, 7 dispatch full, 8 named place not yet visited, 9 named item short, 10 lead not yet followed. Codes 8–10 are shown through the packet's own message.

Order objectives are 100 + *i*, response objectives 200 + *i*, and the closing assessment is objective 300.

## Status and evaluations

The physical register counts the authored instructions and shows the total. Dispatch counts ready and in-transit state-1 responses without collecting them. Each instruction displays a textual state; active/overdue instructions show remaining/elapsed days using the same frozen clock as deadline suspension. No hidden trust, creditworthiness or numeric assessment score is shown. Failure messages distinguish unread papers, places not yet visited, leads not yet followed, missing item quantities, uncollected orders, filed work, pending requests, refused extensions, missing advance permission, settled claims, empty balances and insufficient gold.

Each report selects its authored reply at filing time. A report with at least five days remaining, no used extension and no missed deadline receives a prompt-service letter. Other timely work receives the ordinary response. Any recorded missed deadline selects the late response, including after an approved extension. Core retains this history separately from the current active/overdue state. Delayed collection cannot change a letter already in transit.

The controller submits a closing docket after every authored instruction's completion response is collected and any claim/explanation has reached a final decision. Service receives an Accounts snapshot from the controller, keeping its plugin independent of Accounts. Subject 1099 and outcomes 10–12 identify the evaluation; objective 300 tracks collecting it. There is a full additional day in transit, callback validation and a persistent transaction guard. Reprinting the letter does not repeat any effect. The assessment grants no money, public rank or additional authority.

A fault is a missed deadline. The three assessments are: commendation for no faults and clean settled finances; qualified acceptance for one fault or a partially allowed expense; reprimand for two or more faults, outstanding funds, an actual overdue-advance audit finding, or a denied expense. A check after timely full repayment is not an adverse audit. The snapshot is fixed when the docket is sent; later claims/repayments do not rewrite it. An unanswered meal explanation holds the review, with guidance available in Review status. Normal accounting remains available afterward.

The archive reserves 128 unique document slots. There are 120 authored forms, but each packet delivers only one of its alternative replies. A test runs the whole series with both extension requests on every instruction and the full meal-claim path. It issues 81 distinct documents and 37 transactions, within both limits of 128. Transaction and assignment history remain bounded; this update does not create an endless repeatable workload. The larger runtime arrays require a fresh save; no prior-version state migration is implemented.

## Development recovery

Use only on throwaway test saves. A busy controller normally retains its running Papyrus stack through save/load. If a stack demonstrably aborted, inspect the Papyrus log before intervention. The console can call `cqf EA_PrototypeQuest GoToState ""` to unlock the controller after the stack is no longer running. This does not repair a partially completed inventory operation.

`EA_Dispatch.DebugRecoverPending(transactionID)` operates only on a state-2 transaction and only with `EA_Core.DebugEnabled` explicitly enabled in a debug build/CK property. Enable debug logging in the same way; normal builds leave it false. Recovery is deliberately absent from normal menus. Do not reset controller or transaction variables indiscriminately, replay commissioning, or stop/restart the framework quests.

## Tooling sources

[Caprica v0.3.0](https://github.com/Orvid/Caprica/releases/tag/v0.3.0) compiles the Skyrim target. [Mutagen's source](https://github.com/Mutagen-Modding/Mutagen) supplies typed plugin schemas and binary serialization. The upstream [Skyrim SE FormKeys](https://github.com/Mutagen-Modding/Mutagen.Bethesda.FormKeys/tree/release/Mutagen.Bethesda.FormKeys.SkyrimSE/Skyrim) identify Gold001 (`00000F`) and HighPolyNote (`097788`), and each packet's named item, place and lead:

| Instruction | Kind | Editor ID | FormID | Source list |
| --- | --- | --- | --- | --- |
| 1002 | item | FoodSolitudeSpicedWine | `085368` | Ingestible.cs |
| 1003 | place | MarkarthLocation | `018A59` | Location.cs |
| 1003 | lead | MS01 (The Forsworn Conspiracy) | `018B4B` | Quest.cs |
| 1004 | item | Book3ValuableBlades | `0F4530` | Book.cs |
| 1005 | item | FoodHonningbrewMead | `0508CA` | Ingestible.cs |
| 1005 | place | WhiterunHonningbrewMeaderyLocation | `0DAB88` | Location.cs |
| 1006 | place | WinterholdLocation | `018A51` | Location.cs |
| 1006 | lead | MG01 (First Lessons) | `01F251` | Quest.cs |
| 1007 | item | Book2CommonRisingThreatV1 | `0ED5F4` | Book.cs |
| 1008 | item | Book3ValuableDragonborn | `0F86FE` | Book.cs |
| 1008 | place | WhiterunLocation | `018A56` | Location.cs |
| 1009 | item | JazBay | `06AC4A` | Ingredient.cs |
| 1010 | place | WhiterunLocation | `018A56` | Location.cs |
| 1010 | lead | MS09 (Missing in Action) | `01CF26` | Quest.cs |
| 1011 | item | MoonSugar | `0D8E3F` | Ingredient.cs |
| 1011 | place | WindhelmStablesLocation | `0209F5` | Location.cs |
| 1012 | item | PaperRoll | `033761` | MiscItem.cs |

The FormKeys lists give Editor IDs only. These must all be checked against the installed game before release: the display names the orders use (for example *The Rise and Fall of the Blades* and *The Rising Threat, Vol. I*); the items' prices and where they can be bought; whether any quest reserves them; whether each Location covers the place the order describes; and which quest each lead's Editor ID actually is. No proprietary game assets or base scripts are distributed.
