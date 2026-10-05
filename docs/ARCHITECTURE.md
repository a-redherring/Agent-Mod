# Prototype architecture and state contract

Five plugins are generated from source, with explicit local FormIDs. `content/record-ids.json` is the stable record map; do not compact or renumber it in an update. Runtime assignment IDs 1001–1006 are independent of plugin FormIDs. Core transaction IDs monotonically increase and are retained as replay guards.

Plugin headers are explicitly 1.70, all new IDs begin at 0x800, and no plugin is ESL-flagged. This avoids requiring the newer extended-ID format merely because of a library default; older runtimes can reject 1.71 headers, as documented by the [Backported Extended ESL Support project](https://github.com/Nukem9/skyrimse-backported-esl-support). Actual runtime compatibility still needs game testing.

Dependencies are `Skyrim.esm → EA_Core`; `EA_Dispatch → EA_Core`; `EA_Service / EA_Accounts → EA_Core + EA_Dispatch`; and `EA_Prototype → all four`. The builder orders masters according to this graph. Core references no optional mod.

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

Prototype limits: 64 lifetime assignments, 64 authority keys, 128 lifetime dispatch transactions, 128 unique retained document forms, six authored duties, and one accounting case. Slots are not recycled: exhaustion refuses new work rather than losing replay history. A long-running production workload requires a versioned retention design. Deadlines catch up at dispatch interaction; responses use one-shot game-time notifications and are also checked on collection. There are no continuously polling update loops.

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

## Packet progression, status and evaluations

Instructions 1004–1006 remain unregistered until all first-packet completion responses are collected and the player next chooses Collect Orders. The new orders request six firewood, four leather strips and six wheat, each with a ten-day deadline, five-day first extension and final refusal. These duties use the initial allowance and authorize no new accounting cases or completion rewards. Their displayed objectives are 13–15 and response objectives 23–25. The player may leave the second packet uncollected without a running deadline.

The physical register counts only these six duties. Dispatch counts ready and in-transit state-1 responses without collecting them. Each instruction displays a textual state; active/overdue instructions show remaining/elapsed days using the same frozen clock as deadline suspension. No hidden trust, creditworthiness or numeric assessment score is shown. Failure messages distinguish unread papers, missing item quantities, uncollected orders, filed work, pending requests, refused extensions, missing advance permission, settled claims, empty balances and insufficient gold.

Each report selects its authored reply at filing time. A report with at least five days remaining, no used extension and no missed deadline receives a prompt-service letter. Other timely work receives the ordinary response. Any recorded missed deadline selects the late response, including after an approved extension. Core retains this history separately from the current active/overdue state. Delayed collection cannot change a letter already in transit.

The controller submits a closing docket after all six completion responses are collected and any claim/explanation has reached a final decision. Service receives an Accounts snapshot from the controller, keeping its plugin independent of Accounts. Subject 1099 and outcomes 10–12 identify the evaluation; objective 30 tracks collecting it. There is a full additional day in transit, callback validation and a persistent transaction guard. Reprinting the letter does not repeat any effect. The assessment grants no money, public rank or additional authority.

The three assessments are: commendation for no missed deadlines and clean settled finances; qualified acceptance for one late duty or a partially allowed expense; reprimand for two or more late duties, outstanding funds, an actual overdue-advance audit finding, or a denied expense. A check after timely full repayment is not an adverse audit. The snapshot is fixed when the docket is sent; later claims/repayments do not rewrite it. An unanswered meal explanation holds the review, with guidance available in Review status. Normal accounting remains available afterward.

The archive reserves 128 unique document slots, enough for all 70 authored forms including every alternative. Transaction and assignment history remain bounded; this update does not create an endless repeatable workload. The larger runtime arrays require a fresh save; no prior-version state migration is implemented.

## Development recovery

Use only on throwaway test saves. A busy controller normally retains its running Papyrus stack through save/load. If a stack demonstrably aborted, inspect the Papyrus log before intervention. The console can call `cqf EA_PrototypeQuest GoToState ""` to unlock the controller after the stack is no longer running. This does not repair a partially completed inventory operation.

`EA_Dispatch.DebugRecoverPending(transactionID)` operates only on a state-2 transaction and only with `EA_Core.DebugEnabled` explicitly enabled in a debug build/CK property. Enable debug logging in the same way; normal builds leave it false. Recovery is deliberately absent from normal menus. Do not reset controller or transaction variables indiscriminately, replay commissioning, or stop/restart the framework quests.

## Tooling sources

[Caprica v0.3.0](https://github.com/Orvid/Caprica/releases/tag/v0.3.0) compiles the Skyrim target. [Mutagen's source](https://github.com/Mutagen-Modding/Mutagen) supplies typed plugin schemas and binary serialization. The upstream [Skyrim SE FormKeys](https://github.com/Mutagen-Modding/Mutagen.Bethesda.FormKeys/tree/release/Mutagen.Bethesda.FormKeys.SkyrimSE/Skyrim) identify Gold001 (`00000F`), FoodWineAlto (`03133B`), MountainFlower01Blue (`077E1C`), and HighPolyNote (`097788`). The new supply references are Firewood01 (`06F993`), LeatherStrips (`0800E4`) from [MiscItem.cs](https://github.com/Mutagen-Modding/Mutagen.Bethesda.FormKeys/blob/release/Mutagen.Bethesda.FormKeys.SkyrimSE/Skyrim/MiscItem.cs), and Wheat (`04B0BA`) from [Ingredient.cs](https://github.com/Mutagen-Modding/Mutagen.Bethesda.FormKeys/blob/release/Mutagen.Bethesda.FormKeys.SkyrimSE/Skyrim/Ingredient.cs). These references still require validation against the installed game records before release. No proprietary game assets or base scripts are distributed.
