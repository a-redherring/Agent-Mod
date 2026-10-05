# Elenwen Intelligence Agent Mod — Build Specification Continuation 01

**Applies to:** `Elenwen_Agent_Mod_Build_Specification.md`  
**Document status:** Approved design continuation and revision  
**Purpose:** Integrate the revised cover, service-content, character-writing, Dark Brotherhood, Civil War, Dawnguard, and implementation-order decisions without replacing the established architecture  
**Working prefix:** `EA_`  
**Game:** The Elder Scrolls V: Skyrim Special Edition / Anniversary Edition

## 1. How to use this continuation

The consolidated build specification remains the canonical baseline. This document changes or expands only the subjects named below. Every baseline decision not expressly revised here remains in force, including:

- the existing plugin split;
- the physical dispatch and report loop;
- scarce direct meetings with Elenwen;
- standing, prior, and emergency authority;
- hidden professional trust and financial state;
- the curated vice roster and SFW limits;
- isolated compatibility patches;
- event-driven scripting and narrow vanilla edits;
- overdue work producing service consequences rather than broken saves;
- main-quest work being the final major quest-family implementation.

If wording conflicts, this continuation governs the following baseline sections:

- Section 6, **Alternate Perspective start**;
- Section 7, **Service and orders**;
- Section 14, **Dark Brotherhood glue**;
- Section 15, **Dawnguard and Volkihar glue**;
- Section 16, **Civil War glue**;
- Sections 20–21, **Implementation phases and test matrix**.

It also adds a new project-wide Elenwen writing standard.

## 2. Revised decision register

The following decisions are now settled.

1. **Establish Cover is an employment problem, not a costume checklist.** The player must acquire a durable, socially legible reason to travel, ask questions, enter institutions, and possess unusual goods. The structure should recall Caius Cosades's early direction in *Morrowind*: establish a respectable identity, gain practical experience, and become useful before receiving sensitive work.
2. **A cover must be supported by legitimate employment or recognized guild membership.** Clothing and accommodation support the cover but do not complete it.
3. **Routine content must be authored.** Generic firewood, flowers, ore, cheap wine, and undifferentiated fetch lists are not acceptable as the principal service loop.
4. **Procurement orders must name a specific object, edition, vintage, provenance, recipient, or intelligence purpose.** A job must communicate why this item matters.
5. **Elenwen's voice must be written from a corpus-based guide derived from her vanilla dialogue.** New writing should preserve her social polish, interrogation-by-conversation, institutional confidence, controlled contempt, and economy.
6. **Confirmed Dark Brotherhood personnel are subject to standing kill-or-capture authority.** Once the player has substantive contact with the organization, the strategic objective becomes its destruction.
7. **The player may not formally enlist with either Civil War army.** No infiltration exception is permitted.
8. **Dawnguard becomes a staged intelligence operation.** It begins with independent vampire investigations, advances to use of the Dawnguard as a source, and culminates in authorized infiltration of the Volkihar clan.
9. **`EA_MainQuest.esp`, including Diplomatic Immunity, remains the last major addition.** It is not to be pulled forward merely because its narrative hooks are attractive.

## 3. Architecture impact

No new full-size plugin is required.

| Requirement | Owning module | Notes |
|---|---|---|
| Cover employment and affiliation | `EA_Start.esp` | Uses narrow checks against vanilla or explicitly supported faction/quest state |
| Authored specialty assignments | `EA_Service.esp` | May use documents and routing supplied by `EA_Dispatch.esp` |
| Elenwen voice and correspondence standard | Project-wide | Primarily `EA_Start`, `EA_Service`, `EA_Accounts`, and quest-family modules |
| Brotherhood standing directive | `EA_DarkBrotherhood.esp` | Uses Core authorization and report APIs |
| Civil War enlistment prohibition | `EA_CivilWar.esp` | Dialogue conditions and guarded entry stages; no new war campaign |
| Vampire casework and Volkihar infiltration | `EA_Dawnguard.esp` | Serana-specific manipulation remains in `EA_Serana.esp` |
| Diplomatic Immunity and main-quest continuity | `EA_MainQuest.esp` | Still implemented after every other major quest-family module |

`EA_Core.esp` may add generic enums, assignment tags, or API calls that more than one module genuinely needs. It must not absorb cover-route content, vampire scenes, Brotherhood actors, or Civil War quest edits.

## 4. Establish Cover revision

### 4.1 Narrative model

The initial order should not ask the player merely to dress like a civilian and rent a bed. It should state, in substance:

- a person without occupation attracts questions;
- a useful cover explains movement, money, associates, and curiosity;
- the player is to acquire a recognized place in Skyrim's civilian life;
- early local work is both cover-building and a practical test of judgement;
- sensitive service will follow only after the cover can survive ordinary scrutiny.

The player is already Elenwen's trained operative. This is not remedial training. It is the local establishment phase of an experienced officer entering a new theatre.

The *Morrowind* influence is structural, not imitative dialogue. As Caius sends the player into the world to establish a plausible identity and gain experience before advancing the intelligence mission, Elenwen requires the player to become socially anchored before receiving politically sensitive work.

### 4.2 Completion requirements

`EA_Start_EstablishCover` completes only when all four conditions are true:

1. **Residence:** the player has secured the designated modest room or other approved accommodation.
2. **Civilian presentation:** the player possesses the issued papers and at least one suitable civilian outfit.
3. **Affiliation:** the player has obtained one approved employment relationship or guild membership.
4. **Proof of use:** the player has completed one piece of legitimate work through that affiliation and filed a cover-establishment report.

Visiting locations or buying clothing alone must not satisfy the assignment.

### 4.3 Approved cover routes

The first release should support a small, explicit set of routes. Do not attempt to infer every mod-added profession.

#### Route A — Mercantile or specialist employment

The player accepts work from a named merchant, alchemist, innkeeper, scholar, or importer who can plausibly retain a courier, procurer, guard, researcher, or factor.

The EA portion supplies one authored probationary commission rather than relying on a generic favor quest. Examples:

- obtain a particular imported vintage for a Solitude client;
- identify and purchase a named book from a specified seller;
- verify the quality and origin of a rare alchemical shipment;
- escort or deliver a sealed commercial packet without opening it;
- inspect a missing consignment and report whether loss, theft, or fraud is most likely.

On completion, the employer issues a physical letter or contract establishing the player's legitimate role. This is the preferred launch route because it requires little interference with vanilla guild quest lines and naturally justifies later procurement and travel.

#### Route B — College of Winterhold membership

The player may use recognized College membership as an academic or magical cover. The route completes when the relevant vanilla admission state is reached and one approved College-related piece of work is complete.

EA must not alter the College's main story or automatically advance its quests. The cover report may describe the player as an apprentice, researcher, correspondent, or procurer; it must not claim a senior rank the player has not earned.

#### Route C — Bards College membership or employment

The player may use the Bards College as a cultural, archival, courier, or patronage-facing cover. Because full vanilla membership may require substantial adventuring, the implementation may recognize either:

- completion of the College's formal admission threshold; or
- a modest custom retainer from the College for copying, acquisition, delivery, or research.

The second option should be preferred if it avoids forcing a long dungeon quest before the service loop can begin.

#### Route D — Additional supported guilds

Other routes may be added only after record inspection confirms a stable, low-conflict membership condition. Each added route must:

- plausibly explain the player's movements and questions;
- avoid contradicting the confidential Thalmor premise;
- require at least one legitimate task;
- have a clear quest-stage or faction-rank check;
- avoid granting unearned faction rank;
- include a physical proof document or report selection.

The Companions and mod-added guilds are candidates, not launch requirements.

### 4.4 Route selection and permanence

- The first Establish Cover order presents the approved categories without a game-like class-selection menu.
- The quest watches only the narrow conditions for supported routes.
- The first qualifying affiliation becomes the **primary cover** when the player files the report.
- Later guild memberships do not silently replace it.
- A change of primary cover requires a specific report and approval.
- Loss of an employer or later faction conflict may mark the cover **strained**, but it should not automatically deactivate the whole service system.

### 4.5 Simple implementation pattern

Use a conventional quest with discrete objectives and one alias or reference per custom employer. Recommended state:

- `EA_CoverResidenceReady`
- `EA_CoverPresentationReady`
- `EA_CoverRouteCandidate`
- `EA_CoverWorkComplete`
- `EA_CoverReportFiled`
- `EA_CoverPrimaryType`
- `EA_CoverEstablished`
- `EA_CoverStrained`

Affiliation checks should occur on quest-stage events, dialogue completion, location change, or explicit dispatch interaction. Do not poll all vanilla factions continuously.

The player's report should ask:

- which affiliation is being declared;
- what work was completed;
- what access the role provides;
- what scrutiny or obligations it creates;
- whether any person showed unusual interest in the player's background.

Elenwen's response may accept the cover, accept it provisionally, or require one corrective action. A correction creates work; it does not restart the character.

### 4.6 Explicit cuts

Do not build:

- a dynamic disguise or suspicion simulation;
- procedural interviews with every hold guard;
- automatic compatibility for every guild mod;
- a visible cover-strength meter;
- a requirement to become leader of a faction;
- radiant firewood, crop-picking, or ore-mining as the defining proof of employment;
- a second public Thalmor identity.

## 5. Authored specialty service content

### 5.1 Content rule

An EA assignment must answer at least three of these questions:

1. Why does Elenwen or the Embassy want this?
2. Why is this specific object, person, place, or edition required?
3. Why is the player, rather than an ordinary courier, being used?
4. What information can be learned beyond simple delivery?
5. What judgement, discretion, or report choice remains after the objective is complete?

If a job can be summarized as “bring any five common items,” it is unsuitable unless the apparent banality conceals a specific intelligence purpose that the player can discover or report.

### 5.2 Assignment families

#### A. Provenance procurement

Acquire an exact item whose origin matters.

Examples:

- a named vintage from a particular vineyard, shipper, cellar, or confiscated lot;
- a presentation bottle associated with a court, guild, or trading house;
- a specific edition or translation of a political, religious, historical, or magical work;
- a book bearing an owner's annotation, library stamp, cipher key, or missing page;
- a rare reagent from a named supplier whose trade relationships are under examination;
- ceremonial cloth, ink, seal wax, or paper produced by a particular workshop.

The item should use a fixed Base Object or an EA-specific object. Do not fill the objective from a broad leveled-list keyword such as any wine or any book.

#### B. Commercial intelligence

The visible transaction is legitimate; the report is the real work.

Examples:

- compare a manifest with the goods actually received;
- determine who financed a high-value shipment;
- ask why a supposedly scarce import is suddenly abundant;
- learn whether a merchant will violate an embargo or confidentiality request;
- confirm which courtier, priest, officer, or guild buys a particular luxury;
- trace a book's ownership through marginalia or a bookseller's records.

#### C. Archival and textual intelligence

The player retrieves or inspects a specific text rather than collecting generic books.

Examples:

- locate a named printing and determine whether passages were altered;
- compare two copies and report a missing dedication or inserted page;
- obtain a scholar's notes without removing the library's public copy;
- identify who recently requested a restricted history;
- deliver a harmless volume whose binding contains a concealed message.

#### D. Observation attached to an errand

The errand creates access to a place or person.

Examples:

- deliver a case of wine and record the guests present;
- return a borrowed book and note who uses the private collection;
- inspect a warehouse for damage and identify evidence of clandestine meetings;
- collect a tailored garment and report the insignia or measurements on another order;
- carry diplomatic stationery and identify which seals are in active use.

#### E. Recovery and denial

Retrieve a particular sensitive object or prevent its circulation.

Examples:

- recover a misdirected packet before the recipient opens it;
- buy every copy of one inflammatory pamphlet from a named printer;
- retrieve a compromised codebook disguised as a devotional text;
- replace a revealing ledger page with a harmless duplicate;
- secure a unique bottle, gift, or invitation that could identify an Embassy contact.

### 5.3 Authored job packet

Each assignment definition should contain:

- unique assignment ID;
- title visible in the journal;
- operational or cover-facing category;
- eligibility conditions;
- fixed target forms and references;
- briefing document;
- deadline and travel allowance;
- expense eligibility and advance ceiling;
- optional intelligence observations;
- at least two report outcomes where judgement matters;
- prompt, ordinary, overdue, and compromised response variants where justified;
- cooldown or one-shot status;
- follow-up assignment IDs, if any.

The system may randomly choose among eligible authored packets. It must not procedurally invent the object, motive, prose, or Elenwen response.

### 5.4 Launch content target

Before repeatable generation is expanded, build a polished pool of approximately:

- 4 cover-employment commissions;
- 6 provenance procurements;
- 5 book or archive cases;
- 5 commercial-intelligence errands;
- 4 observation or dead-drop cases;
- 3 recovery or denial cases;
- 3 deliberately mundane personal or administrative duties written with equal specificity.

Thirty strong packets are preferable to hundreds of generic combinations.

### 5.5 Item implementation policy

- Prefer fixed vanilla objects when they are not unique quest property and their provenance can be expressed honestly.
- Use EA-specific duplicates or new objects when a named vintage, marked edition, annotated book, or concealed packet is required.
- Hand-place or enable rare objects for their assignment rather than injecting them broadly into leveled lists.
- Never consume a vanilla quest item without an explicit compatibility decision.
- Mark irreplaceable EA case items as quest objects only while the case requires them.
- Provide recovery at the dispatch archive for items lost to physics, merchant reset, or interrupted delivery.

## 6. Elenwen writing and voice guide

### 6.1 Source basis and required corpus audit

The guide below is based on the characteristic patterns in Elenwen's shipped vanilla scenes: her Embassy reception, party conversation, post-Embassy recognition and threat posture, political participation, and cut or unused material associated with Helgen. It is a production guide, not a claim that every line has already been exhaustively tagged.

Before final dialogue lock, export all English Elenwen dialogue and subtitle records from the supported game build through the Creation Kit or xEdit. Create a simple corpus sheet with:

- quest and topic Editor IDs;
- scene and condition context;
- public, private, hostile, cordial, or procedural register;
- sentence length;
- question type;
- terms of address;
- contractions and hesitation;
- threat form;
- references to office, treaty, rank, hospitality, and institutional power;
- whether the line is shipped, unused, or cut.

Unused dialogue may inform characterization, especially her institutional anger and diplomatic entitlement, but must be labeled separately and must not outweigh shipped performance.

### 6.2 Core observations

#### Politeness is an instrument

At the Embassy, Elenwen uses welcome, hospitality, and personal interest to control the exchange. Her questions appear social but collect identity, motive, and status. New dialogue should often make courtesy do operational work.

She does not need to bark when a calm question can force the player to account for himself.

#### She establishes rank without explaining it

Elenwen introduces her office, assumes the legitimacy of her presence, and expects others to understand the consequences. She rarely argues from first principles. Orders and responses should sound as if the hierarchy already exists.

#### Contempt is controlled and selective

Her disdain is most effective when expressed through qualification, a pause, a comparison, or a precise observation. Avoid constant slurs, sneering adjectives, and theatrical cruelty.

#### Conversation is directed, not shared

She acknowledges an answer and returns to the point she wants addressed. A player's joke, compliment, excuse, or diversion may receive a brief response, but it does not move her away from the required information.

#### Threats are institutional before they are physical

Her power comes from the Embassy, the Dominion, the treaty, records, access, and consequences. She can imply surveillance, recall, denial, exposure, or formal complaint without promising melodramatic torture in every scene.

#### She is economical

Vanilla Elenwen does not deliver long ideological lectures. She favors short introductions, pointed questions, clean transitions, and conclusions that close the exchange. Briefings may contain detail because the work requires it, but her personal annotations should remain compressed.

#### Public warmth and private precision coexist

In public, she may be gracious and socially smooth. In confidential correspondence, decoration falls away. Familiarity with the player should appear as confidence in what he will understand, not as casual modern banter.

### 6.3 Sentence-level rules

- Prefer clear declarative sentences.
- Use one carefully chosen subordinate clause rather than chains of ornate clauses.
- Ask questions whose answer creates accountability.
- Use titles, surnames, offices, and institutional nouns when status matters.
- Use the player's given name sparingly; it should signal private familiarity, emphasis, warning, or unusual approval.
- Keep praise brief and often attach the next obligation.
- Let pauses or self-corrections indicate judgement, not uncertainty.
- Use contractions naturally but not constantly.
- Avoid contemporary corporate jargon, spy-film clichés, and pseudo-Elizabethan ornament.
- Avoid explaining feelings that can be expressed through what she records, withholds, or assigns next.

### 6.4 Register by document type

#### Operational order

- opens with the required result;
- supplies only necessary strategic context;
- defines authority and reporting expectations;
- names prohibitions precisely;
- closes without motivational rhetoric.

#### Returned report

- identifies the decisive fact first;
- distinguishes a useful outcome from a compliant method;
- praises rarely and specifically;
- converts mistakes into restrictions, corrective duties, denied expenses, or closer reporting.

#### Personal favor

- is framed as reasonable and assumes compliance;
- may be petty without becoming silly;
- reveals familiarity through expectation, not sentimentality;
- often omits a reward because the relationship itself explains the task.

#### Public dialogue

- maintains hospitality and plausible deniability;
- never exposes the player's confidential status;
- can contain a second meaning legible only to the player.

#### Private audience

- is more direct than a letter but still controlled;
- reserves open anger for genuine strategic damage, betrayal, or public embarrassment;
- ends with a decision, order, or question requiring an answer.

### 6.5 Praise, criticism, and familiarity

Use the following scale.

| Situation | Preferred response style |
|---|---|
| Routine success | Acknowledgement and next task |
| Skilled success | One precise sentence naming the good judgement |
| Exceptional success | Brief personal recognition, made powerful by rarity |
| Minor lateness | Dry notice of the delay and a practical consequence |
| Excusable deviation | Acceptance of the reason, followed by clarified limits |
| Poor judgement with useful result | Separate the value of the result from criticism of the method |
| Disobedience | State the breached instruction, consequence, and required remedy |
| Betrayal | Controlled personal and institutional finality; no rant |

### 6.6 Original calibration examples

The following are new examples for the mod, not vanilla quotations.

**Accepting the initial cover:**

> The appointment is modest, which is precisely why it may prove useful. Keep it. Learn who considers your employer beneath notice; such people are often careless.

**Prompt procurement:**

> The correct edition, delivered unopened and without an invented emergency. Good. Accounts will settle the bookseller's charge.

**A useful but late report:**

> The information remains useful. Your explanation for withholding it does not. Future observations in this matter are to be filed within two days.

**Denied extravagant claim:**

> I authorized a discreet meal, not an evening of conspicuous generosity. The Embassy will reimburse the guest's portion. Your vanity may pay for the rest.

**Rare praise:**

> You recognized the danger before I named it. That is why I sent you.

**Redirecting flattery:**

> You may admire my foresight after you have answered the question.

### 6.7 Prohibited characterization

Do not write Elenwen as:

- a constantly shouting sadist;
- a generic femme fatale;
- an affectionate quest dispenser;
- a confessional companion who explains all her motives;
- a modern office manager using contemporary performance language;
- a Dominion propagandist who turns every note into a racial lecture;
- omniscient without reports, witnesses, or intelligence sources;
- impressed by raw power to the point of surrendering authority;
- romantically conquered by compliance;
- careless enough to identify the player as her agent in public.

### 6.8 Writing review checklist

Every Elenwen text should be reviewed for these questions:

- What does she want the recipient to do or disclose?
- Does the line preserve her control of the exchange?
- Is the politeness performing a function?
- Could one sentence be removed without losing meaning?
- Is criticism tied to a concrete breach or strategic concern?
- Does praise name judgement rather than flatter power?
- Does the line reveal information she could plausibly know?
- Would the line still sound like Elenwen if the character name were removed?

## 7. Dark Brotherhood revision

### 7.1 Doctrine

The Dark Brotherhood is a hostile clandestine organization. The player is not to join it, perform its career contracts, or cultivate it as a long-term allied asset.

Once a person is reasonably confirmed as an operational Brotherhood member, the player has standing authority to:

- kill the member when immediate action is necessary or capture is impractical;
- accept surrender and transfer the captive when an authored capture route exists;
- seize operational documents and distinctive evidence;
- protect an innocent target or state witness;
- coordinate tactically with Commander Maro or another designated Imperial contact;
- take the minimum necessary action to preserve the destruction operation.

The player must report named-member dispositions, recovered evidence, collateral deaths, and any bargain made with a suspected member.

### 7.2 Contact trigger

“Contact” is not limited to joining the faction. The destruction directive may activate after any supported confirming event, including:

- surviving an identifiable Brotherhood assassination attempt;
- receiving and verifying information from Aventus Aretino;
- being abducted by Astrid;
- encountering a named member under circumstances that establish affiliation;
- recovering authenticated Brotherhood instructions or insignia.

Unverified rumor does not authorize indiscriminate killing.

On first confirmed contact, `EA_DarkBrotherhood.esp` creates:

1. an incident-report requirement;
2. standing kill-or-capture authority against confirmed members;
3. the overarching objective **Break the Black Hand**, or equivalent final title;
4. instructions to identify, expose, and destroy the Skyrim sanctuary network.

### 7.3 Kill and capture implementation

Do not create a universal nonlethal combat framework.

- **Kill** uses ordinary combat and the vanilla destruction route wherever possible.
- **Capture** is available only for specifically authored actors and scenes with a surrender, restraint, transfer, or report abstraction.
- A designated capture candidate may enter a protected bleedout/surrender package only during the relevant quest stage.
- If capture would conflict with a vanilla alias, scene, or required death, the option is omitted.
- Random assassins and sanctuary defenders do not require capture content.
- A report may distinguish killed, captured, escaped, and unconfirmed without simulating prisoners indefinitely.

This preserves the directive while avoiding compatibility with combat overhauls, essential-state churn, and persistent prisoner AI.

### 7.4 Astrid and the destruction route

The abandoned-shack confrontation is the cleanest strategic pivot.

- The player receives or already possesses authority to refuse recruitment.
- Killing Astrid should enter or forward the vanilla **Destroy the Dark Brotherhood!** route.
- If a stable authored surrender route for Astrid proves technically safe, it may be added later, but it is not a launch requirement.
- The player reports the abduction, the captives' disposition, Astrid's disposition, and any recovered information.
- Elenwen, not Maro, defines the strategic objective and judges the operation.
- Maro provides location, access, tactical coordination, and Imperial disposition of prisoners or evidence.

### 7.5 Easy implementation boundary

The first version should wrap and condition the vanilla destruction path rather than replace it:

- detect the supported contact trigger;
- issue the EA directive;
- condition any Brotherhood-joining opportunity out of the intended route;
- forward the vanilla destruction stages;
- add reports before and after sanctuary action;
- deliver Elenwen's assessment and EA reward;
- record the organization as destroyed.

Do not rebuild Brotherhood contracts, sanctuary schedules, or Penitus Oculatus command structure.

## 8. Civil War revision

### 8.1 Absolute enlistment rule

The player is not authorized to enlist with either the Imperial Legion or the Stormcloaks. This is a hard campaign rule, not a request for prior authorization and not an infiltration option.

The reasons are operational:

- a military oath would create a competing public chain of command;
- either enlistment would compromise the civilian cover;
- a conquest outcome would damage Elenwen's preferred strategic stalemate;
- military service would expose the player to orders that cannot be reconciled with confidential Embassy work.

The player may speak to either side, gather information, carry specifically authorized communications, attend negotiations, and act under the main quest's peace-council requirements. None of those actions constitute enlistment.

### 8.2 Implementation

Use the smallest reliable intervention:

- add dialogue conditions or replacement responses at the formal commitment points;
- do not disable faction headquarters or ordinary conversations;
- do not set late Civil War victory stages merely to make offers disappear;
- preserve the prerequisites and scenes needed for Season Unending;
- patch against Season Unending Neutral Stance rather than duplicating it;
- provide a development-only recovery check if an external mod forces an enlistment faction rank.

If the player reaches an enlistment threshold despite the block, EA should prevent confirmation before an oath or irreversible stage. It should not attempt to unwind an entire completed war campaign in a live save.

### 8.3 Allowed Civil War-related work

EA may author non-enlistment work such as:

- observing troop movements;
- comparing requisition records;
- identifying unofficial envoys;
- monitoring Talos rhetoric and recruitment;
- carrying a sealed diplomatic message;
- evaluating whether a local escalation threatens the desired stalemate;
- reporting on peace-conference bargaining positions.

These assignments must not make the player a soldier, officer, or battlefield conqueror for either side.

## 9. Expanded Dawnguard and Volkihar operation

### 9.1 Campaign purpose

The Dawnguard arc should feel like an intelligence case that gradually proves the existence, scale, and political importance of an organized vampire court.

The player does not stumble into Volkihar service and rationalize it afterward. The operation proceeds through:

1. preliminary vampire evidence;
2. independent investigations;
3. the Dawnguard as a source and access point;
4. discovery of evidence consistent with vampire lords or an aristocratic clan;
5. advance authorization for deep penetration if such a group is found;
6. contact with Serana and Castle Volkihar;
7. authorized infiltration;
8. reporting, containment, exploitation, and eventual removal of Harkon.

### 9.2 Stage A — Preliminary inquiry

The arc begins before formal Dawnguard involvement. Elenwen assigns a low-visibility case concerning a pattern rather than declaring that vampire lords exist.

Recommended case sequence:

#### Case 1: Disappearances with selection

The player reviews two or three fixed incidents whose victims are not random: a courier, minor official, scholar, wealthy traveler, or person with access. The task is to determine whether the pattern indicates feeding, recruitment, information theft, or ordinary banditry.

Implementation should use placed evidence, short witness dialogue, and a report choice rather than a new crime simulation.

#### Case 2: Material evidence

The player retrieves a specific object from a vampire site: an old signet, unusual vessel, genealogy, sealed invitation, architectural sketch, or correspondence using an archaic title. The evidence suggests hierarchy and long continuity but does not yet prove a vampire-lord court.

#### Case 3: Conflicting testimony

The player interviews or observes a hunter, healer, priest, court mage, or survivor. The source is useful but biased. The report asks which claims are credible and which are folklore.

#### Case 4: The organized hand

The player finds evidence that separate vampire activity shares supplies, orders, sanctuary, or patronage. This justifies opening a strategic case on a clan rather than treating each lair as an isolated infestation.

The launch build may combine Cases 2–4 into two quests if scope requires. The important progression is from anomaly to organization, not the number of journal entries.

### 9.3 Stage B — Dawnguard as an intelligence source

Once the preliminary report supports an organized threat, Elenwen directs the player to approach the Dawnguard.

The player's purpose is to:

- assess what Isran knows;
- gain access to hunter reports, captured materials, and field rumors;
- identify whether the Dawnguard has encountered unusually powerful vampires;
- use its operations to reach evidence the Embassy cannot obtain openly;
- avoid exposing the player's service relationship.

Joining or assisting the Dawnguard at this stage is an authorized source-development and access measure, not a new ultimate allegiance. The player's public explanation remains compatible with the primary civilian cover.

EA should surround the vanilla entry with a briefing and report rather than rewriting the entire faction introduction.

### 9.4 Stage C — Conditional deep-cover authority

Before the player enters the sequence likely to produce immediate clan contact, Elenwen issues a written contingency authority.

It should cover:

- accompanying a cooperative vampire source when separation would destroy access;
- entering a clan seat under assumed motives;
- making a limited verbal profession of loyalty necessary to preserve cover;
- accepting temporary faction association;
- accepting vampirism if refusal would end the mission and no safer route remains;
- concealing selected information from the Dawnguard while penetration is active;
- using emergency authority where consultation is impossible;
- filing a full incident report at the first safe opportunity.

The authority does **not** permit:

- sincere allegiance to Harkon;
- unnecessary predation on civilians;
- disclosure of the player's Elenwen connection;
- arbitrary service to Volkihar interests unrelated to cover;
- indefinite postponement of reports;
- allowing the prophecy or Harkon's strategic project to succeed.

This pre-authorization solves the vanilla pacing problem: after Serana is found, the player can accompany her and respond at Castle Volkihar without pretending there is time for a courier exchange.

### 9.5 Stage D — Serana as source and access vector

Within `EA_Dawnguard.esp`, Serana is first treated as:

- evidence of a concealed aristocratic vampire structure;
- a source with unique access;
- a person whose cooperation may be more valuable than immediate detention;
- a route to Volkihar leadership.

The more personal manipulation, vice pressure, disclosures, and bespoke timing conflicts remain in `EA_Serana.esp`.

The Dawnguard module records objective operational facts. The Serana module interprets and complicates the player's judgement around her. Neither module may let Serana replace Elenwen's authority.

### 9.6 Stage E — Volkihar infiltration

On entry to Castle Volkihar, the operation becomes active deep cover.

Required state should distinguish:

- Volkihar access obtained;
- public cover within the clan;
- vampire state, if accepted;
- Harkon's confidence or suspicion only where the vanilla quest already supplies a stable proxy;
- evidence collected;
- emergency actions awaiting report;
- Dawnguard disclosures made or withheld;
- infiltration complete;
- Harkon removed;
- post-operation cure or continuing condition.

Do not create a universal undercover suspicion meter. Use major quest stages and a small number of authored incidents.

Reports should be available at believable safe windows rather than after every scene. Where travel back to the dispatch box would conflict with vanilla pacing, allow the player to retain a sealed field report until communication becomes possible.

### 9.7 Strategic end state

The operation ends with:

- Harkon's project prevented;
- Harkon removed;
- the clan's surviving structure assessed;
- Serana and Valerica reported according to their final positions;
- vampire-state decisions recorded;
- Dawnguard exposure and continuing utility assessed;
- recovered texts, artifacts, and intelligence accounted for;
- Elenwen determining whether any continued observation is required.

The conclusion must not imply that the player became loyal to Volkihar or that Dawnguard ideology displaced the service relationship.

### 9.8 Easy implementation boundary

The first release should use:

- three or four short authored pre-contact investigations;
- fixed evidence objects and witnesses;
- reports composed from known facts;
- briefing and debrief quests around vanilla Dawnguard stages;
- a single contingency-authorization document before forced decisions;
- vanilla faction and transformation mechanics;
- no generalized vampire ecology simulation;
- no new castle politics system;
- no dynamic undercover meter;
- no attempt to make every Dawnguard side quest part of the operation.

## 10. Main quest remains last

`EA_MainQuest.esp` is the final major addition after the following are playable and stable:

1. Core and dispatch;
2. revised Establish Cover;
3. authored service backlog;
4. Accounts and vice integrations;
5. Civil War enlistment block and Season Unending support;
6. Dark Brotherhood destruction route;
7. Dawnguard pre-investigation and Volkihar infiltration;
8. Serana integration;
9. confirmed compatibility patches for those systems.

Only then should development proceed to:

- Diplomatic Immunity's pro-Thalmor route;
- Delphine and Esbern dependency-safe outcomes;
- Paarthurnax authority and outcome;
- Blades cleanup;
- end-to-end main-quest continuity.

The reason remains technical, not merely narrative: the main quest has the broadest alias, scene, protected-state, and downstream compatibility risk. By the time it is implemented, the project's reporting, authorization, writing, recovery, and testing patterns should already be proven elsewhere.

Do not use placeholder edits to `MQ201` or related quests during earlier phases unless they are confined to a disposable research plugin.

## 11. Revised implementation sequence

### Revision Phase A — Cover slice

- Implement one mercantile/specialist employment route.
- Implement one guild route using narrow vanilla state checks.
- Add the revised Establish Cover report.
- Add provisional acceptance and one corrective follow-up.
- Verify delayed Helgen behavior remains untouched.

**Exit condition:** a new player can acquire a genuine civilian affiliation, complete legitimate work, file proof, and enter normal EA service without starting Helgen.

### Revision Phase B — Authored service pool

- Convert any generic prototype duties into fixed authored packets.
- Build the first wine/provenance job and first named-book job.
- Build at least one commercial-intelligence errand with a report judgement.
- Add item recovery and replay protection.
- Apply the Elenwen voice checklist to all responses.

**Exit condition:** no launch assignment is satisfied by an arbitrary common item, and at least ten polished packets can circulate without repetition or duplication.

### Revision Phase C — Dialogue corpus and style lock

- Export the supported English Elenwen dialogue records.
- Tag shipped and unused lines separately.
- Revise the voice guide if the corpus contradicts any provisional rule.
- Create a project lexicon and prohibited-phrase list.
- Review all existing Elenwen text in one pass.

**Exit condition:** every Elenwen line has passed a context, knowledge, rank, brevity, and voice review.

### Revision Phase D — Civil War and Brotherhood

- Block both formal enlistment paths at their commitment points.
- Confirm Season Unending remains reachable in the intended neutral setup.
- Add Brotherhood contact detection and standing directive.
- Wrap the vanilla destruction route.
- Add one capture-capable authored encounter only if it is stable; otherwise ship kill and report outcomes first.

**Exit condition:** neither army can be joined, and the Brotherhood can be destroyed under Elenwen's authority without entering its career path.

### Revision Phase E — Dawnguard intelligence arc

- Build the preliminary evidence cases.
- Add the Dawnguard-source briefing and report.
- Issue conditional deep-cover authority before the forced Serana/Harkon sequence.
- Wrap Volkihar progression with safe-window reports.
- Integrate `EA_Serana.esp` after the operational route is stable.

**Exit condition:** the player progresses from uncertainty about organized vampires to authorized Volkihar penetration and Harkon's removal without a loyalty contradiction.

### Revision Phase F — Main quest, last

- Begin only after Phases A–E pass their full-profile tests.
- Inspect the final supported records in xEdit and the Creation Kit.
- Implement Diplomatic Immunity first within the module, then later Blades decisions and cleanup.

**Exit condition:** the original baseline definition of done is met with the revised cover and vampire arcs included.

## 12. Additional test matrix

### 12.1 Cover

- Establish Cover cannot complete from clothing and residence alone.
- Each supported affiliation is detected only at its intended quest stage or dialogue result.
- One legitimate task is required.
- The first filed affiliation becomes the primary cover.
- Joining a later guild does not overwrite it.
- A dead or unavailable custom employer has a recovery route.
- Helgen remains dormant throughout pre-Helgen cover establishment.
- An unsupported mod-added faction does not accidentally satisfy the quest.

### 12.2 Authored jobs

- Generic wine does not satisfy a named-vintage objective.
- A random book does not satisfy a named-edition objective.
- Quest items from unrelated vanilla quests are not consumed.
- Dropped, sold, or reset EA case items can be recovered once without duplication.
- Prompt, ordinary, overdue, and compromised outcomes select the correct response.
- Expense eligibility follows the assignment packet rather than a broad item keyword.
- Optional observations appear in the report only when actually discovered.

### 12.3 Elenwen writing

- Public dialogue never exposes the player's service status.
- Elenwen does not know unreported facts without an identified source.
- Praise remains proportionate and rare.
- Criticism identifies a concrete breach.
- Orders distinguish required result, authority, prohibition, and reporting duty.
- Generated or external dialogue cannot imitate Elenwen to grant canonical authority.

### 12.4 Dark Brotherhood

- A rumor alone does not grant kill authority.
- A confirmed assassination attempt does.
- Astrid's shack can enter the vanilla destruction route.
- The player cannot continue into the intended career-join route.
- Killing a confirmed member records a reportable disposition.
- Capture appears only for designated actors and does not persist after invalid quest stages.
- Maro cannot override Elenwen's strategic authority.
- Destruction completion produces one report and one reward sequence.

### 12.5 Civil War

- Legion enlistment is blocked before oath and faction commitment.
- Stormcloak enlistment is blocked before oath and faction commitment.
- Ordinary faction dialogue remains available.
- Season Unending remains startable and completable.
- Neutral Stance compatibility is tested both present and absent where supported.
- No EA path silently advances a hold-conquest stage.

### 12.6 Dawnguard and Volkihar

- Preliminary cases can run before formal Dawnguard contact.
- Evidence unlocks only the report conclusions actually discovered.
- The Dawnguard briefing does not declare facts not yet proven.
- Deep-cover contingency authority is issued before the forced Castle Volkihar decision.
- Refusing or accepting Harkon's offer follows the supported branch without clearing EA service state.
- Vampire transformation does not change loyalty, trust, cover, or dispatch ownership.
- Reports queue safely when immediate return to a dispatch box is implausible.
- Serana operational state and vice state do not overwrite one another.
- Harkon's removal, surviving clan assessment, and final report each occur once.
- Cure and non-cure end states remain recordable.

## 13. Updated definition of done

In addition to the baseline definition, the project is not complete unless:

- the player's civilian cover rests on actual employment or recognized affiliation;
- the opening reproduces the useful structure of *Morrowind*'s early intelligence work without copying its plot or dialogue;
- routine assignments are specific, authored, and worth reading;
- specialty wine, books, and similar procurements require the correct item and a credible reason;
- Elenwen's new writing consistently matches the project voice guide and has been checked against an exported vanilla corpus;
- Dark Brotherhood contact produces immediate standing kill-or-capture authority and a destruction objective;
- neither Civil War army can formally enlist the player;
- Dawnguard begins as an intelligence source within a prior vampire investigation;
- Volkihar entry is authorized in advance as deep cover;
- Diplomatic Immunity and the rest of the main-quest glue are implemented only after the other major systems are stable.

The intended result is a campaign in which even simple work has context, cover has social substance, and major faction choices feel like parts of one coherent service career under Elenwen.
