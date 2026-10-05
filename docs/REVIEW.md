# Review record

## Changes in 0.2.0: Revision Phase B

This revision applies Continuation 01's Revision Phase B (authored service pool) as far as it can be built and checked without the game.

- The six generic duties are replaced by eleven authored instructions, defined in `content/packets.json`. The plugin builder generates their papers, shortage messages, conclusion menus, journal objectives and Service bindings from that file, and rejects gaps in numbering or a malformed case.
- Every item requirement is one exact Skyrim.esm base object. Nine instructions name an item; five issue case papers and require one of three conclusions; four do both. The pool covers provenance, commercial-intelligence, archival, denial, personal and administrative work.
- Instructions circulate in a fixed order, three at a time, each exactly once. A later instruction cannot overtake an earlier one. Positional menus replace the seven-button assignment list, which could not hold eleven instructions.
- Case papers are archived and recoverable like orders, and their `EA_CaseFile` script records the reading fact for its own assignment. The conclusion menu appears only after the papers are read and the item is held. Cancel files nothing; a misjudged conclusion completes the work with a specific rejection and a net trust loss, and counts as a fault in the closing assessment.
- Every Elenwen letter in the packets and Accounts was rewritten against the section 6 voice guide. Alto wine became Solitude spiced wine, and the claim, explanation and decision papers follow it.
- 37 records were retired and listed in `content/retired-records.json`. Every retained record kept its FormID and no retired ID was reused. Objectives, runtime arrays and the instruction set changed, so 0.2.0 requires a fresh save.

Test coverage: the automated suite has grown from 87 tests to 108. Several second-packet tests were replaced rather than kept. New behaviour tests cover:
- circulation order, the three-open limit and no repeats across the whole series;
- substitute items being refused;
- the case-paper, conclusion and Cancel paths, and the controller's ordering of those checks;
- the sound and misjudged reply for every conclusion of every case;
- tone with a sound conclusion;
- faults counted in the assessment;
- capacity with every extension in a full series;
- serialization mid-case.

New plugin tests check the packet bindings, case scripts and objectives. A new content suite enforces:
- the pool size;
- complete packets;
- distinct, non-generic and non-quest items;
- three conclusions for each case;
- distinct reply variants;
- signed and economical letters;
- a starter prohibited-phrase list;
- no reuse of retired IDs.

As a check on the tests themselves, three deliberate faults were compiled into the Service script: four open instructions, an inverted judgement, and case papers not required. The suite caught each one (9, 23 and 2 failures) before the source was restored.

Not established: whether the named FormIDs carry the display names the orders use, what the items cost, where they can be obtained, whether a quest reserves any of them, and how long case papers render in the book interface. None of this can be checked without the game, and TESTING.md steps 13–13b record it. Families D (observation) and E (world-placed recovery) need hand-placed references and remain unbuilt, as do random packet selection, compromised-cover replies and the corpus-based voice review (Phase C).

## Review of 0.1.2-prototype


Reviewed the eight runtime scripts, generated plugin schema and bindings, all authored documents, compiler declarations, build/package tools, CI configuration, test interpreter and test coverage against the original specification. This was a source, binary and simulated-behavior review. Skyrim, Creation Kit and the installed dependency plugins remain unavailable.

### Additions in 0.1.2

All six requested additions are implemented:

- The physical dispatch register displays assignment states, individual deadline balances, and ready/in-transit correspondence.
- Specific messages explain why reports, extensions, authorizations, advances, claims and repayments cannot proceed; supply shortages include the missing quantity.
- Every duty has ordinary, prompt and previously overdue responses. Elenwen also comments on the chosen Accounts decision. Response tone is fixed at filing time.
- Accounts accepts up to 10, 25 or all affordable outstanding septims and confirms the actual amount and balance.
- A closing docket selects a commendation, qualified assessment or reprimand after all six completion replies and any pending Accounts decision. Its own reply takes another full game day.
- A second finite packet adds firewood, leather bindings and wheat, with deadlines starting only when collected after the first packet is acknowledged.

The review verified that extensions do not erase deadline history; later collection does not change an already-written response; partial repayments preserve the cash/debt invariant before and after each claim outcome; a pending or returned claim holds the closing review; and a subsequent claim does not mislabel an already-issued review as waiting. The second-packet notice appears once and does not start its deadlines. All existing local FormIDs are retained.

The catalogue grew to 70 authored forms, so retention increased to 128 document slots. Replay guards and bounded transaction history remain in place. No runtime migration is provided: 0.1.2 requires a fresh save.

The automated suite contains 87 tests, including 23 new behavior/binding checks and the prior regressions. Matrix tests include cash conservation across the original 30 repayment/audit/claim combinations and 10 additional partial-payment/audit/claim combinations. Plugin inspection verifies every service letter is bound to the correct instruction slot, all three new supply FormIDs, and native menu/argument limits. Manual engine validation is still pending.

### Earlier fixes retained from 0.1.1

| Finding | Correction and regression coverage |
| --- | --- |
| A zero transaction ID matched empty request slots and could authorize an operation or extend a deadline | All response receivers now require a positive ID and the exact dispatch currently being collected |
| Calling a receiver directly could bypass the transit delay or change the queued outcome | Dispatch validates state, arrival time, recipient, subject and outcome before any response effect |
| Standing/emergency expenditure grants were accepted for the prior-authorized advance | Accounts specifically requires prior authority; a weaker grant no longer prevents a proper authorization request |
| Delivered wine/flowers remained recoverable in the accessible archive | Supplies are permanently consigned; the archive contains papers only |
| Repeated denied extension requests could exhaust the shared transaction queue | A final denial closes further extension applications for that instruction |
| Uncollected responses and unanswered explanations could postpone audit indefinitely | Deferral covers actual return transit only; recognized later costs can still discharge audited liability |
| Nested pauses resumed too early; new assignments/extensions during a pause gained excess time | Balanced suspension depth and per-assignment frozen clocks preserve remaining time |
| Reading field papers before collecting orders did not count | The reading fact is remembered and applied when the instruction is registered |
| Near-arrival activations scheduled extremely short callbacks; stale events could notify after collection | Enforced a 0.1-hour minimum notification interval and checked for a due response before notifying |
| Generic extension and meal papers omitted the chosen case/explanation | Added six assignment-specific extension papers, a separate personal-meal explanation and a distinct fifteen-septim decision |
| A failed quest start was ignored, allowing the UI to continue into incomplete setup | Startup is checked before player transactions; failures release the controller's Busy state |
| Canceling a form displayed a misleading failure message | Canceled selections make no transaction and close without a failure prompt |
| Recovery could leave the quest journal stale after Core recorded completion | Completed response callbacks reconcile the objectives without repeating trust changes |
| A full document catalogue could accept a transaction whose reply was not recoverable | Both document slots are reserved before accepting the transaction; pending replies remain inaccessible |
| Test inventory objects compared by contents; the implicit Papyrus state variable was not persisted by the test interpreter | Corrected identity and state handling and added tests proving non-player activation is ignored and Busy suppresses another menu |
| Compiler identity was only assumed; packaging replaced the ZIP before checking its contents | Pinned executable verification, explicit import paths, package hash/CRC validation and atomic ZIP replacement |

Thirteen targeted regression tests were first run against the original compiled scripts/test interpreter and reproduced failures. The corrected suite additionally checks startup recovery, actual state dispatch, document capacity, wrong outcomes, cash conservation across thirty repayment/audit/claim combinations, and packaging failure behavior. In that revision, existing local FormIDs were retained and eight new BOOK records received explicit unused IDs. There is still no supported saved-game upgrade path.

### What was built in 0.1.2

Five ESPs contain 123 new records, including 70 readable BOOK records. Eight compiled PEX scripts implement the prototype's commission, six duties in two packets, secure dispatch and archive, status register, contextual delayed responses, closing assessment, deadlines/extensions, scoped authority, one accounts case with partial repayments, audit/liability and development recovery. The mod requires no SKSE or optional plugin for this bounded loop and overrides no vanilla records.

The source repository contains the Papyrus, authored content, deterministic FormID contract, Mutagen builder with locked dependencies, verified compiler downloader, automated checks, Windows CI definition and manual game-validation checklist. The packaged build includes compiled plugins/scripts, their Papyrus source, documentation and a SHA-256 manifest.

### Validation limits

Papyrus is compiled for Skyrim with warnings treated as errors, using project-authored native API declarations. Binary structure, plugin masters, IDs, VMAD target types, script properties and note records are checked independently after Mutagen round trips. Logic tests execute Caprica's emitted assembly with simulated native game calls. Tests also exercise package integrity and preserve an existing package when validation fails.

These checks do not certify actual Skyrim execution, VM concurrency/interruption behavior, engine save/load, note readability, physical placement, meshes, or compatibility with a real mod profile. Recompile against extracted Creation Kit sources, inspect the plugins in xEdit/CK and complete the manual matrix before treating this as a game-tested release.

The full Alternate Perspective start, Establish Cover/accommodation, repeatable workload, NPC relationship/vice systems, courier and AI integrations, and all major quest routes remain unimplemented. They are tracked in IMPLEMENTATION_STATUS.md. This review repairs the current prototype; it does not turn the prototype into the full specification.
