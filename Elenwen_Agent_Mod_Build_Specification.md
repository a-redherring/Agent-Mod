# Elenwen Intelligence Agent Mod Build Specification

**Working prefix:** `EA_`  
**Game:** The Elder Scrolls V: Skyrim Special Edition / Anniversary Edition  
**Document status:** Consolidated design baseline  
**Purpose:** Implementation specification for the bespoke Elenwen intelligence-agent mod and its compatibility layer

## 1. Project goal

Build a modular role-playing framework in which the player begins as a covert field officer already recruited by Elenwen, operates under a civilian identity, receives orders and funds through physical documents, and later becomes the Dragonborn without abandoning that prior allegiance.

The mod must make the character feel employed rather than merely faction-tagged. The central play loop is:

1. collect orders and correspondence;
2. maintain a civilian cover;
3. conduct investigations, errands, and major operations;
4. make time-sensitive decisions within granted authority;
5. file reports and expense claims;
6. receive approvals, criticism, reimbursement decisions, and new work;
7. reconcile Skyrim's major quest lines with continued loyalty to Elenwen.

Five systems define the project:

- **Service:** Elenwen employs the player and maintains a persistent workload.
- **Authority:** politically significant actions require the appropriate level of permission.
- **Vice:** the player repeatedly makes irrational but non-explicit choices around a fixed roster of women.
- **Accounts:** advances, claims, denials, and debt make those choices materially visible.
- **Quest glue:** vanilla quest assumptions are corrected when they conflict with the covert-officer premise.

## 2. Design rules

### 2.1 Narrative rules

- The player's loyalty to Elenwen is absolute and cannot be displaced by romance, Serana, another faction, or a generated conversation.
- The player is a confidential asset and field officer, not a publicly uniformed Thalmor member.
- Direct audiences with Elenwen are scarce and consequential. Target roughly five to seven major meetings across the important story arcs.
- Most service activity is conducted through orders, dispatches, forms, reports, receipts, and physical evidence.
- The player begins without a private office or prestigious institutional position.
- The character's later Dragonborn identity is an additional complication, not a replacement backstory.

### 2.2 Mechanical rules

- Do not expose a generic loyalty meter, vice meter, temptation meter, or category list to the player.
- Use explicit quest state and authored rules for plot authority. Generated dialogue must never invent orders, approve operations, or change canonical mission state.
- Avoid blocking a live vanilla scene while the player waits for permission. Pre-authorized operations and emergency authority must cover decisions that cannot reasonably be deferred.
- Missed deadlines normally create an overdue assignment and a service consequence, not an immediate hard quest failure.
- Compatibility logic belongs in optional patches, not in `EA_Core.esp`.
- Prefer event-driven scripts and narrow quest aliases. Avoid constant polling and broad edits to vanilla records.

### 2.3 Presentation rules

- The interface should feel paper-, book-, and document-driven.
- Orders and responses must exist as readable in-world documents even when a menu or activator is used to sort them.
- Reports are selected or generated from known facts and form choices; the player is not required to type free-form prose.
- Tradecraft may be assisted by subtle magic, but magic must not erase travel, secrecy, delay, or communication risk.

## 3. Plugin architecture

Use one stable core, a small number of system modules, isolated quest-family modules, and only the compatibility patches actually required by the installed list.

| Plugin | Required masters | Responsibility |
|---|---|---|
| `EA_Core.esp` | Official game masters | Shared state, keywords, FormLists, assignment IDs, trust, authority, common scripts, and public API |
| `EA_Start.esp` | `EA_Core`, Alternate Perspective | Bespoke pre-Helgen start, cover identity, commission, papers, initial funds, and Establish Cover assignment |
| `EA_Dispatch.esp` | `EA_Core` | Incoming and outgoing physical correspondence, dispatch box, document routing, and response collection |
| `EA_Service.esp` | `EA_Core`, `EA_Dispatch` | Orders, routine intelligence work, duties, favours, workload, deadlines, extensions, and reports |
| `EA_Accounts.esp` | `EA_Core`, `EA_Dispatch` | Advances, receipts, expense claims, reimbursement decisions, debt, audits, and financial probation |
| `EA_Vice.esp` | `EA_Core` | Curated roster, relationship restrictions, behavioural hooks, and indirect time/money/judgement consequences |
| `EA_MainQuest.esp` | `EA_Core`, official game masters | Diplomatic Immunity, Delphine, Esbern, Paarthurnax, Blades cleanup, and main-quest continuity |
| `EA_DarkBrotherhood.esp` | `EA_Core`, official game masters | Elenwen-directed destruction of the Dark Brotherhood and Commander Maro liaison framing |
| `EA_Dawnguard.esp` | `EA_Core`, Dawnguard | Volkihar deep cover, emergency authority, reports, and loyal-agent framing |
| `EA_CivilWar.esp` | `EA_Core`, official game masters | Blocks formal enlistment, preserves Season Unending, and maintains a neutral stalemate |
| `EA_Serana.esp` | `EA_Core`, `EA_Vice`, `EA_Dawnguard`, Sinister Serana | Serana-specific manipulation, vice hooks, timing conflicts, disclosures, and compatibility glue |

### 3.1 Core boundaries

`EA_Core.esp` contains only infrastructure shared by multiple modules:

- hidden service status;
- Elenwen professional trust;
- common factions, keywords, globals, FormLists, and assignment identifiers;
- authorization state and permission checks;
- shared report and assignment data structures;
- common script functions and mod events;
- hooks used by all optional modules.

It must not require Mantella, Sinister Serana, Sidequests of Skyrim, Witness, It's On Me, Legacy of the Dragonborn, or a particular UI replacer.

### 3.2 Module granularity

Do not create separate plugins for individual vice targets, reimbursement categories, letters, favours, or assassination targets. Keep independent vanilla quest families separate because they touch different records and need to be testable or removable independently.

Small compatibility plugins should be ESL-flagged ESPs where technically safe. Do not compact or flag a plugin merely to save a slot if doing so would destabilize quests, scripts, references, or patch maintenance.

## 4. Dependency policy

### 4.1 Hard dependencies

Only make a mod a hard master when its records or runtime behavior are indispensable to that module.

- `EA_Start.esp`: Alternate Perspective.
- `EA_Serana.esp`: Sinister Serana and the EA modules shown in the architecture table.
- Official DLC dependencies apply to the relevant quest module.
- `EA_Core.esp` should remain independent of all optional role-playing and presentation mods.

### 4.2 Supported external stack

The intended full build includes or may include:

- **Frameworks:** SKSE, Address Library, Fuz Ro D-oh, and only the Papyrus/SPID/KID-style dependencies actually required by selected mods.
- **Foundation:** Legacy of the Dragonborn.
- **Alternate start:** Alternate Perspective.
- **Gameplay:** Mysticism, Adamant, Hand to Hand, Blade & Blunt, Arena, Encounter Zones Unlocked, Starfrost, Apothecary, Gourmet, Candlehearth, Scion, and Sorcerer.
- **Progression:** Apprentice, Trainers Galore, relevant trainer support, Sleep to Level Up, and Level Up Menu.
- **Travel and time:** Carriage and Ferry Travel Overhaul, Travel Stops, and Time Flies.
- **Mail and social support:** Courier Delivery System, Better Courier, It's On Me, Sidequests of Skyrim, Immersive Rejections, Witness, Riffling Is a Crime, and Mantella restricted to the vice roster.
- **Dialogue and NPC expansion:** Immersive Dialogue Expansion – Thalmor, selected Courtalogue/Jarlologue and Anbeegod/FDE expansions, Harkon dialogue expansion, and Sinister Serana.
- **Quest expansion:** selected vanilla quest expansions, including Forsworn Conspiracy Quest Expansion, Blood and Silver, East Empire Expansion, and Season Unending Neutral Stance.
- **Presentation:** Dear Diary, Quest Journal Overhaul, Dynamic Book Framework or an appropriate journal UI, Wayfinder, and a modern paper or low-icon map.

Take Notes and Note Crafting are optional player conveniences, not dependencies.

## 5. Load-order expectations

The precise order must be resolved against the final installed plugins in xEdit, but the intended hierarchy is:

1. Official masters and Creation Club content.
2. SKSE frameworks and shared utilities.
3. UI and paper-presentation mods.
4. Legacy of the Dragonborn and other large foundations.
5. Alternate Perspective.
6. Simonrim gameplay modules.
7. Progression modules.
8. Travel and time modules.
9. Courier, social, consequence, and vice-support mods.
10. Dialogue and NPC expansions.
11. Quest and faction expansions, including Season Unending Neutral Stance.
12. EA framework modules in this order:
    - `EA_Core.esp`
    - `EA_Start.esp`
    - `EA_Dispatch.esp`
    - `EA_Service.esp`
    - `EA_Accounts.esp`
    - `EA_Vice.esp`
13. EA quest modules:
    - `EA_MainQuest.esp`
    - `EA_DarkBrotherhood.esp`
    - `EA_Dawnguard.esp`
    - `EA_CivilWar.esp`
    - `EA_Serana.esp`
14. EA compatibility patches.
15. Final conflict-resolution or Synthesis output.
16. DynDOLOD and Occlusion output.

EA quest modules intentionally load after the dialogue and quest mods whose behavior they reconcile. A compatibility patch must load after every plugin it patches.

## 6. Alternate Perspective start

`EA_Start.esp` supplies a bespoke Alternate Perspective start.

### 6.1 Initial state

The player begins with:

- a local civilian cover identity in Skyrim;
- an already-established confidential service relationship with Elenwen;
- no public Thalmor faction membership;
- a rented room or similarly modest accommodation;
- a physical Commission or credential;
- field papers appropriate to the cover;
- modest operating funds and basic supplies;
- introductory instructions and reporting expectations;
- an active **Establish Cover** assignment;
- no office and no privileged public status.

### 6.2 Helgen and Dragonborn activation

- Helgen has not happened at game start.
- The normal Helgen and Dragonborn sequence remains dormant until the player deliberately enters the vanilla plot through Alternate Perspective.
- Becoming Dragonborn must not clear service variables, invalidate Elenwen's authority, or rewrite the character as a newly recruited agent.
- The narrative premise is a field officer who later happens to become Dragonborn.

### 6.3 Start validation

Test at minimum:

- new game selection and initial teleport;
- Commission, papers, funds, and orders present exactly once;
- no premature Helgen or main-quest stages;
- normal Alternate Perspective activation of Helgen;
- main quest starts without duplicate aliases, couriers, or documents;
- removal of `EA_Start.esp` is not advertised as safe after a game has begun.

## 7. Service and orders

`EA_Service.esp` is the largest day-to-day content module.

### 7.1 Assignment classes

- **Major operations:** story-linked intelligence work and high-consequence missions.
- **Routine intelligence:** observation, verification, contact work, retrieval, and low-level investigation.
- **Duties and favours:** administrative, diplomatic, logistical, and personal tasks assigned by Elenwen.

Examples of deliberately mundane work include:

- collect wine;
- deliver correspondence;
- retrieve a book;
- obtain clothing or material;
- inspect a site or object;
- pick up an order;
- acquire ingredients;
- check on an individual;
- carry diplomatic paperwork;
- perform a petty personal favour.

Some duties provide no reward beyond having complied.

### 7.2 Workload model

The system should be capable of maintaining approximately:

- one major operation;
- two or three routine intelligence assignments;
- three to six duties or favours;

at the same time. These are capacity targets, not quotas that must always be filled. Assignment generation must respect quest state, location, cooldowns, and conflicts.

### 7.3 Deadlines and extensions

- Most deadlines are generous enough to permit ordinary travel without map fast travel.
- On expiry, an assignment becomes **overdue** rather than instantly failing.
- Consequences may include criticism, reduced trust, a lower reward, a denied expense, a follow-up order, or eventual withdrawal of the assignment.
- The player may request an extension through dispatch.
- Extension results may be approved, denied, conditionally approved, or returned with a demand for explanation.
- Main-quest emergencies and scenes outside player control must not silently punish the player for impossible deadlines.

### 7.4 Reporting

Reports should be assembled from objectives, discovered facts, disposition choices, and short authored form options. The report system should support:

- completion reports;
- interim reports;
- incident reports;
- authorization requests;
- extension requests;
- expense submissions;
- explanations requested by Accounts or Elenwen.

The report's selections may affect trust, later dialogue, reimbursement, and follow-up orders. Free-text authoring is outside scope.

## 8. Dispatch and mail

`EA_Dispatch.esp` provides the physical communications layer.

### 8.1 Incoming delivery

- EA creates and controls the content and quest state of its documents.
- Courier Delivery System and Better Courier handle actual courier presentation where suitable.
- Sensitive or operational material may be held for collection instead of being delivered openly.
- Every delivered order must be recoverable if the courier package is interrupted or the document is dropped.

### 8.2 Secure outgoing box

Provide a bespoke secure Thalmor dispatch box or equivalent physical activator. Its principal actions are:

- **Collect Orders**
- **File Report**
- **Request Extension**
- **Request Authorization**
- **Submit Expense Claim**
- **Return Unused Advance**
- **Send Sensitive Material**
- **Check Responses**

The activator may open a concise menu, but completed actions should create, remove, stamp, or archive physical documents so the paper fiction remains intact.

### 8.3 Communication constraints

- No instant magical messaging.
- No remote scrying conversations.
- No mind reading or telepathic orders.
- Responses require believable delivery or collection time.
- Critical vanilla quest scenes must use prior or emergency authority rather than pretending an NPC will wait for correspondence.

## 9. Authorization system

Authorization is tracked per operation or decision class, not as a single universal permission flag.

### 9.1 Standing authority

Covers:

- ordinary investigation;
- routine tradecraft;
- normal use of cover resources;
- expected minor risks;
- actions explicitly included in a current operational brief.

### 9.2 Prior authorization

Required, where advance consultation is realistic, for:

- politically important killings;
- formal faction commitments;
- major disclosures of protected information;
- irreversible actions with diplomatic or strategic consequences;
- expenditure or exposure beyond the current brief.

### 9.3 Emergency authority

Covers unforeseen choices that require immediate action. It does not erase accountability: the player must report afterward, and Elenwen may approve, criticize, limit, or penalize the action.

Harkon's offer is the model case. The player does not suspend the Dawnguard scene to send a letter. The Volkihar operation grants enough standing and emergency authority to respond, followed by a mandatory report.

## 10. Accounts and reimbursements

`EA_Accounts.esp` models operational funding, not consumer banking.

### 10.1 Ledger fields

Each relevant entry should be capable of recording:

- date;
- payee or recipient;
- amount;
- item or service;
- operation or case identifier;
- source advance, if any;
- amount claimed;
- reimbursement result;
- amount reimbursed;
- outstanding operational debt;
- running balance or liability.

### 10.2 Claim outcomes

- **Approved**
- **Partially approved**
- **Denied**
- **Returned for explanation**

Outcomes should use authored rules and context. A purchase connected to an active operation may be valid; an extravagant meal, gift, or detour disguised as operational spending may be reduced, rejected, or questioned.

### 10.3 Advances and liability

Support:

- operation-specific advances;
- repayment of unused advances;
- denied claims becoming personal liability;
- periodic audits;
- garnishment from later payments where appropriate;
- reduced willingness to issue future advances;
- financial probation;
- an internal operational-creditworthiness state.

Creditworthiness answers whether the Embassy will risk advancing more money to this operative. It is not a general credit score.

## 11. Vice system

`EA_Vice.esp` keeps the vice narratively central while remaining mechanically unobtrusive and fully SFW.

### 11.1 Final curated roster

- Elenwen
- Faralda
- Brelyna
- Karliah
- Aranea Ienith
- Jenassa
- Niranye
- Elisif
- Serana

Irileth, Anuriel, and Gabriella are not in the settled roster and must not be restored without a deliberate design change.

### 11.2 Hard rules

- No visible vice statistic, category, quest objective, or diagnostic journal entry.
- No successful romance or marriage with a curated target.
- Friendship, professional interaction, follower use, and NPC-specific quest content remain available.
- Elenwen loyalty is never weakened or replaced.
- All content remains SFW.
- The system must not label NPCs or the player with explicit meta-language about the vice.

### 11.3 Emergent behaviors

The vice appears through patterns such as:

- overspending and dubious claims;
- gifts and paying for meals;
- unnecessary favours and travel;
- lingering and lost time;
- assignment delays;
- preferential treatment;
- poor professional judgement;
- inappropriate disclosure attempts;
- taking on too much work;
- embarrassment when receipts reach Elenwen.

### 11.4 External support

- **Mantella:** enabled only for the curated roster; provides memory and context-sensitive conversation but no mission authority.
- **Immersive Rejections:** supports rejection behavior; EA supplies permanent relationship restrictions where the external mod does not.
- **It's On Me:** provides meals and paying-for-dinner interactions.
- **Sidequests of Skyrim:** supplies mundane NPC favours for ordinary targets.
- **Time Flies:** makes shopping, gifting, eating, reading, and related behavior consume meaningful game time.
- **Witness:** supplies social consequences when bad judgement becomes crime, gossip, reporting, or blackmail.
- **Riffling Is a Crime:** reinforces consequences for invasive behavior.
- **NPC dialogue expansions:** deepen individual targets without moving plot authority outside EA.

ORomance is explicitly excluded. It was considered earlier but was superseded by Mantella, authored dialogue, Immersive Rejections, and bespoke EA hooks.

### 11.5 Per-target guidance

Ordinary targets may notice repeated generosity, availability, or preferential treatment, but they should not speak as if aware of a game system. Elenwen's personal requests are authored in `EA_Service.esp`, not generated by Sidequests. Serana receives a dedicated module because her behavior is more deliberate and tightly connected to Dawnguard.

## 12. Sinister Serana integration

`EA_Serana.esp` loads after the Dawnguard and Sinister Serana changes it must reconcile.

Serana may:

- recognize the player's susceptibility;
- test it and remember what works;
- request increasingly inconvenient favours;
- selectively withhold or reveal information;
- interfere with Elenwen's timetable;
- induce questionable spending;
- encourage disclosures she should not receive;
- exploit the player's willingness when it advances her interests.

She may not:

- replace Elenwen as the player's ultimate loyalty;
- generate binding mission orders;
- alter authorization state through Mantella dialogue;
- turn the Volkihar deep-cover assignment into sincere allegiance to Harkon;
- bypass the permanent relationship restrictions.

Sidequests of Skyrim should not be the primary Serana content source. Her bespoke hooks and Sinister Serana dialogue should carry the interaction so she does not fall back to conspicuous generic silent dialogue.

## 13. Main quest glue

`EA_MainQuest.esp` isolates dangerous edits to vanilla main-quest records.

### 13.1 Diplomatic Immunity

Provide a pro-Thalmor route that still produces the information needed to advance the main quest.

The route must avoid:

- forcing the player to murder Elenwen's personnel;
- gratuitous Embassy theft;
- dialogue or objectives that assume the player has ceased working for Elenwen;
- breaking Delphine's downstream quest stages.

### 13.2 Delphine and Esbern

- Keep each protected while required by main-quest aliases or scenes.
- Allow Elenwen to authorize later removal when the relevant dependencies can safely be cleared.
- Delphine and Esbern are independent decisions; authorization for one does not imply authorization for the other.
- Remove essential or protected status only after checking active aliases and dependent quests.
- Provide cleanup and fallback stages so Blades content does not remain permanently stuck.

### 13.3 Paarthurnax and the Blades

- Paarthurnax's disposition is decided by Elenwen, not by Delphine.
- Preserve the main quest's required dragon and peace-council functions before permitting irreversible outcomes.
- Clean up objectives, aliases, essential flags, and faction reactions after any sanctioned removal.

## 14. Dark Brotherhood glue

`EA_DarkBrotherhood.esp` implements the settled route:

- the Dark Brotherhood is ultimately destroyed;
- the strategic decision and framing come from Elenwen;
- the player does not become a career Brotherhood assassin;
- Commander Maro may serve as an operational liaison but is not the player's commanding officer;
- reports and rewards return through the EA service chain;
- the module remains isolated from main-quest edits for easier conflict resolution and testing.

## 15. Dawnguard and Volkihar glue

`EA_Dawnguard.esp` frames joining Volkihar as an authorized deep-cover operation.

- The player never genuinely transfers allegiance to Harkon.
- The operational brief grants the standing and emergency authority needed for immediate scene decisions.
- Major actions are reported afterward.
- Serana remains strategically important but subordinate to the Elenwen-loyal premise.
- Harkon may eventually be removed without the story pretending that the player spontaneously changed ideology.
- Vampire-state or faction changes required by the vanilla quest must not overwrite EA loyalty or service state.

## 16. Civil War glue

`EA_CivilWar.esp` should be deliberately small.

- Block formal enlistment in either the Imperial Legion or Stormcloaks.
- The player is not authorized to conquer Skyrim or resolve the war for either side.
- Retain Season Unending and its neutral or stalemate outcome.
- Preserve Elenwen's strategic interest in an unresolved conflict.
- Exclude Betrayal at Hrothgar.
- Exclude a hot-war conquest ending.
- Patch Season Unending Neutral Stance rather than replacing it.

## 17. Paper and UI workflow

The presentation layer should support the following experience:

1. A courier notice or dispatch-box prompt indicates material is available.
2. The player collects a sealed order, reads it, and accepts or acknowledges it.
3. The quest journal tracks objectives without exposing hidden trust, vice, or accounting logic.
4. The player returns to the dispatch box and selects a report or request type.
5. A generated document records the known facts and the player's authored choices.
6. After believable transit time, a stamped response, authorization, reimbursement decision, or follow-up order becomes available.
7. Important documents remain readable or are archived in a controlled container.

Dear Diary, Quest Journal Overhaul, an appropriate book or journal framework, Wayfinder, and a restrained paper map may supply presentation. EA must remain functional if a cosmetic UI component is absent unless that component is explicitly made a module master.

Permitted magical tradecraft includes subtle Illusion, detection and countermagic, lock or utility magic, defensive staves, scroll support, and eventually one limited Mark/Recall capability. These tools supplement physical tradecraft; they do not create magical correspondence or universal fast travel.

## 18. Compatibility patches

Create a patch only after record inspection proves it necessary. Likely patch names include:

- `EA_LotD_Patch.esp`
- `EA_SinisterSerana_Patch.esp`
- `EA_Witness_Patch.esp`
- `EA_Sidequests_Patch.esp`
- `EA_ItsOnMe_Patch.esp`
- `EA_SUNS_Patch.esp`
- `EA_IDEThalmor_Patch.esp`
- quest-expansion-specific patches where conflicts are confirmed.

Each patch should document:

- its masters;
- records intentionally forwarded or overridden;
- script or event integration, if any;
- required load position;
- whether it is safe to add to an existing save;
- uninstall limitations.

Do not create an `EA_ORomance_Patch.esp`; ORomance is not part of the final design.

## 19. State and scripting model

### 19.1 Required persistent state

At minimum, track:

- service active/inactive state;
- cover established and cover-compromise flags;
- Elenwen professional trust;
- active, overdue, completed, withdrawn, and failed assignments;
- authorization grants by operation and category;
- emergency actions awaiting review;
- report and response status;
- advances, claims, debt, probation, and creditworthiness;
- curated-target eligibility and relationship locks;
- major quest-glue decisions and cleanup completion.

### 19.2 Integration boundary

Expose narrow Core functions or mod events for:

- registering an assignment;
- querying authorization;
- recording a reportable incident;
- recording an expense;
- submitting a claim;
- adjusting professional trust;
- checking whether an NPC is on the vice roster;
- notifying modules that a dispatch response is ready.

External dialogue or AI systems may request flavor context but may not directly set plot stages, grant authority, reimburse claims, alter loyalty, or unlock a curated relationship.

### 19.3 Reliability requirements

- Avoid update loops when story-manager events or explicit interactions suffice.
- Make courier and dispatch content idempotent so an interrupted delivery does not duplicate an order or advance.
- Preserve document and assignment identifiers across updates.
- Log important state transitions in a debug build.
- Provide development-only recovery controls for stuck dispatches, aliases, and reports; do not expose them as normal role-playing UI.

## 20. Implementation phases

### Phase 0: conflict map and technical prototype

- Freeze the initial supported mod list and versions for development.
- Inspect all touched quests, aliases, scenes, factions, dialogue, and NPC records in xEdit and the Creation Kit.
- Create a conflict matrix for Alternate Perspective, the main quest, Dawnguard, Season Unending, Sinister Serana, and dialogue expansions.
- Prototype one document, one dispatch transaction, one authorization check, and one report round trip.

**Exit condition:** a clean test plugin demonstrates the paper loop without editing a major vanilla quest.

### Phase 1: Core and dispatch

- Implement shared state, IDs, trust, authorization types, and integration API.
- Implement the secure dispatch box and document archive.
- Implement reliable incoming/outgoing queues and delayed responses.
- Add debug logging and recovery tools.

**Exit condition:** orders, reports, requests, and responses survive save/load and interrupted delivery without duplication.

### Phase 2: Alternate Perspective start

- Build the civilian-cover start.
- Supply Commission, field papers, funds, accommodation, and Establish Cover.
- Validate delayed Helgen and transition into the vanilla main quest.

**Exit condition:** a new character can operate before Helgen and later become Dragonborn without service-state loss.

### Phase 3: Service and authorization

- Implement assignment templates, workload rules, deadlines, overdue state, and extensions.
- Add mundane Elenwen duties and routine intelligence assignments.
- Implement standing, prior, and emergency authority workflows.
- Add generated completion, interim, and incident reports.

**Exit condition:** the day-to-day employment loop is playable for multiple in-game weeks without a major quest module.

### Phase 4: Accounts

- Add advances, ledger entries, claims, explanations, and four reimbursement outcomes.
- Add debt, audits, garnishment, probation, and creditworthiness consequences.
- Connect service rewards and selected external spending events through optional patches.

**Exit condition:** a complete advance-to-audit cycle is testable, including denied and partially approved claims.

### Phase 5: Vice and ordinary integrations

- Enforce the final roster and permanent relationship restrictions.
- Add indirect behavioral and accounting hooks.
- Build optional integrations for It's On Me, Sidequests, Time Flies, Witness, Riffling Is a Crime, and roster-limited Mantella.
- Author Elenwen-specific favours in Service.

**Exit condition:** the vice is legible through play consequences while no visible vice mechanic or successful curated romance exists.

### Phase 6: Quest glue

Implement and test one quest family at a time:

1. Civil War and Season Unending.
2. Dark Brotherhood.
3. Dawnguard and Volkihar.
4. Serana integration.
5. Main quest, Diplomatic Immunity, Delphine, Esbern, Paarthurnax, and Blades cleanup.

Main-quest work comes last because it has the broadest dependency and alias risk.

**Exit condition:** each module can be enabled in the intended full profile and complete its affected quest family without stuck scenes, broken aliases, or contradictory allegiance.

### Phase 7: compatibility and release hardening

- Build only the confirmed compatibility patches.
- Perform full xEdit conflict review.
- Test new game, long-play, save/load, death/reload, courier interruption, overdue assignments, and major quest transitions.
- Run script-latency and Papyrus-log review.
- Document masters, load order, supported versions, upgrade path, and uninstall limitations.

**Exit condition:** a clean full-profile playthrough reaches the end of the main quest, Dawnguard, the Dark Brotherhood destruction route, and Season Unending with coherent EA state.

## 21. Test matrix

Every release candidate should cover:

- EA start selected and vanilla Alternate Perspective start selected;
- Helgen dormant and Helgen activated;
- courier succeeds, is delayed, and is interrupted;
- dispatch box used with no pending items, one item, and multiple items;
- report filed before, on, and after a deadline;
- extension approved and denied;
- prior authorization granted and denied;
- emergency action reported afterward;
- expense approved, partially approved, denied, and returned for explanation;
- unused advance returned and retained too long;
- financial probation entered and cleared;
- every curated target remains non-romanceable while ordinary interaction still works;
- Mantella absent, installed, and unavailable at runtime;
- Sinister Serana present with `EA_Serana.esp`;
- Diplomatic Immunity completed by the pro-Thalmor route;
- Delphine and Esbern decisions made independently after required quest use;
- Paarthurnax outcome and Blades cleanup;
- Dark Brotherhood destroyed without joining its career path;
- Volkihar joined as deep cover and Harkon later removed;
- formal Civil War enlistment blocked and Season Unending completed;
- Legacy of the Dragonborn and selected dialogue/quest expansions enabled;
- save/load at every major handoff and scene boundary.

## 22. Explicit non-goals and cuts

The following are outside the settled design:

- ORomance or an ORomance compatibility patch;
- OStim-dependent content;
- visible vice, temptation, attraction, or loyalty meters;
- vice categories or a journal entry explaining the pattern;
- successful romance or marriage with curated targets;
- NSFW content;
- Irileth, Anuriel, or Gabriella in the current vice roster;
- generic Mantella access for the entire world;
- AI-generated mission authority or plot decisions;
- public Thalmor membership at game start;
- an office or prestigious institutional position at game start;
- immediate Helgen or Dragonborn activation;
- frequent casual meetings with Elenwen;
- free-text report writing as a required mechanic;
- a cipher minigame;
- magical instant messaging, remote scrying, mind reading, or telepathic orders;
- ordinary banking, savings accounts, interest, consumer loans, stock trading, or a general wealth simulator;
- Share Your Meal and Real Eat Package;
- The Gift of Charity as part of the settled vice stack;
- Experience, SkillGroups, Time to Train, or Git Gud in the settled progression stack;
- formal allegiance to either Civil War side;
- Betrayal at Hrothgar or a hot-war conquest ending;
- a career Dark Brotherhood route;
- genuine allegiance to Harkon;
- individual plugins for each target, favour, letter, claim type, or assassination;
- making every supported external mod a master of `EA_Core.esp`;
- removing travel, paperwork, delay, or operational accountability through magic.

## 23. Definition of done

The project is complete when a player can begin before Helgen as Elenwen's covert civilian agent, establish cover, maintain a believable backlog of orders, communicate through physical dispatch, request and exercise appropriate authority, account for operational money, suffer understated vice-related consequences, and complete the supported major quest lines without contradicting their continued loyalty to Elenwen.

The finished mod should feel less like a faction badge and more like a demanding intelligence-service career conducted through Skyrim's existing world.
