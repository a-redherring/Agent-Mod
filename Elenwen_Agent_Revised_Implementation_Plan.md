# Elenwen Agent Mod — Revised Implementation Plan

## Purpose

This document continues and revises the existing **Elenwen Agent** build specification.

The existing architecture remains valid. This plan records the newer settled decisions for the campaign opening, early service structure, Dark Brotherhood, Civil War, Dawnguard / Volkihar infiltration, Elenwen writing, and implementation order.

The goal remains to build a Skyrim SE/AE role-playing framework in which the player is already a confidential agent of Elenwen before becoming Dragonborn.

---

# 1. Canonical Game Start

## 1.1 Start location

The player begins **immediately outside Northwatch Keep**.

The transfer into Skyrim has already occurred off-screen.

Do not create:

- a custom prison transport scene;
- a boat sequence;
- an extra intake office;
- extra Northwatch guards;
- a new processing scene;
- a mandatory interrogation sequence.

The player gains control just outside Northwatch with the transfer already complete.

Northwatch functions only as the handoff point into Skyrim.

## 1.2 Character premise

This start is tailored to Cotta while leaving unnecessary details undefined.

Fixed facts:

- Cotta is a young Imperial.
- He already knows Elenwen.
- He has already entered her service before arriving in Skyrim.
- She has exercised direct influence over his training and career.
- His loyalty to Elenwen is already established.
- He has been transferred into Skyrim through Dominion channels.
- Northwatch has completed the handoff.
- Elenwen has instructed that he be released into civilian cover.
- Helgen has not yet occurred.

Leave deliberately undefined:

- Cotta's exact birthplace;
- family background;
- the exact date or circumstances of his recruitment;
- the details of previous assignments;
- why the transfer passed through Northwatch;
- whether any part of the transfer was disciplinary, protective, administrative, or operational;
- how much of the situation Elenwen deliberately engineered.

The game should imply history without explaining all of it.

---

# 2. Initial Quest: Establish Cover

## 2.1 Initial state

On game start, Cotta has:

- ordinary civilian clothing;
- modest personal equipment;
- civilian papers;
- a small amount of money;
- Elenwen's sealed packet;
- no public Thalmor faction status;
- no prestigious office;
- no permanent accommodation;
- no openly declared Embassy role.

The existing prototype commission / allowance mechanics may be reused where appropriate, but the presentation should be rewritten to fit this start.

## 2.2 Initial journal entry

The first quest journal entry should explain what happened before the player gained control.

It should establish that:

- Cotta was transferred into Skyrim under Dominion authority;
- Northwatch received him under sealed instructions;
- his belongings were held during the transfer;
- confirmation arrived from Elenwen;
- by Elenwen's order, he was released;
- his effects were returned;
- he was not ordered to report to the Embassy;
- he was given civilian papers, modest funds, and a sealed packet;
- Northwatch personnel were not given his full role.

The journal is the main exposition device.

The player should not need a custom introductory scene.

## 2.3 First objective

**Read Elenwen's sealed packet.**

Reading the packet advances the quest and adds the Establish Cover objectives.

---

# 3. Elenwen's Opening Packet

The packet should contain:

1. **Personal instructions from Elenwen**
2. **Civilian papers**
3. **A modest operating allowance**
4. **An Establishment Report form**
5. **Instructions for the secure dispatch channel**

## 3.1 Tone of Elenwen's first letter

The letter must sound as though Elenwen already knows Cotta well.

It must not read like recruitment.

It should communicate:

- calm authority;
- familiarity;
- expectation of obedience;
- confidence in Cotta's judgement;
- minimal praise;
- no sentimentality;
- no need to explain their relationship.

Core instruction:

> Do not report openly to the Embassy. Establish a civilian life in Skyrim first.

The wording should make clear that this is an assignment, not leave.

## 3.2 Establish Cover requirements

The player must:

- acquire credible legitimate employment or another believable occupation;
- secure suitable lodgings;
- establish a plausible reason to remain and travel in Skyrim;
- earn at least some money independently of Elenwen;
- avoid publicly presenting themselves as an Embassy operative;
- file the Establishment Report once the cover is credible.

Do **not** require a specific guild or employer.

The cover should be compatible with different play styles.

Possible routes can include:

- martial work;
- magical study;
- mercenary work;
- trade;
- scholarship;
- alchemy;
- hunting;
- guild membership;
- other credible civilian activity.

The implementation should recognize broad qualifying states rather than force one career.

---

# 4. Early-Game Service Structure

## 4.1 Do not begin with epic operations

After Establish Cover, Elenwen should not immediately send Cotta after dragons, assassins, or political leaders.

The first phase should establish him as a junior field operative.

Early assignments should focus on:

- verification;
- observation;
- discreet retrieval;
- document handling;
- contact checking;
- specialty procurement;
- low-level counter-subversion;
- testing judgement and reliability.

## 4.2 Replace generic gathering jobs

Do not use cheap-feeling radiant objectives such as:

- collect generic firewood;
- collect random flowers;
- collect common cheap wine.

If the player is asked to obtain an item, the item should have a reason to matter.

Examples:

- a particular vintage of wine;
- a specific book or banned text;
- a rare alchemical ingredient;
- a named piece of correspondence;
- a specific religious object;
- a document held by a particular merchant or scholar;
- a specialty material needed for an Embassy function;
- a unique or semi-unique item connected to an active case.

The coding may remain simple.

The writing and context must make the assignment feel intentional.

## 4.3 Authored job pool

Build an authored pool of roughly **20-30 early and mid-game service assignments**.

Use simple eligibility conditions and cooldowns.

Prefer authored jobs over highly procedural radiant generation.

Assignment categories:

### Intelligence verification

- confirm whether a named person is involved in Talos activity;
- verify a suspected courier route;
- check whether a merchant is knowingly helping rebels;
- inspect a site associated with suspicious meetings;
- determine whether a report from another source is accurate.

### Retrieval

- obtain a specific book;
- recover a named document;
- retrieve material from a dead drop;
- obtain a distinctive object relevant to an investigation.

### Specialty procurement

- acquire a named vintage;
- secure a rare text;
- obtain a specialist ingredient;
- purchase an unusual diplomatic gift;
- source a specific imported item.

### Contact work

- check on an informant;
- deliver sealed correspondence;
- verify whether a contact is still reliable;
- arrange or confirm a meeting without exposing the Embassy.

### Administrative duties

These should exist, but even mundane work should have authored context.

Examples:

- carry a sealed diplomatic packet;
- recover a misdirected report;
- inspect a compromised dispatch point;
- deliver confidential accounts paperwork.

---

# 5. Elenwen Writing Guide

## 5.1 Writing objective

Elenwen's correspondence and dialogue must be one of the strongest parts of the mod.

Her writing should feel:

- controlled;
- intelligent;
- formal without sounding theatrical;
- sparing with praise;
- personally familiar with Cotta;
- willing to be dismissive;
- strategically minded;
- occasionally cutting;
- rarely emotional.

She should not sound like:

- a generic evil overlord;
- a parody of the Thalmor;
- an affectionate mentor;
- a modern manager;
- a romance character.

## 5.2 Relationship tone

Cotta may be highly competent.

Elenwen should still treat competent performance as expected.

Typical approval:

- "Acceptable."
- "That will do."
- "You understood the assignment."
- "Good. There is another matter."

Typical criticism:

- factual;
- specific;
- restrained;
- more disappointed than theatrical.

Her authority should feel habitual.

She should not need to constantly remind Cotta that she outranks him.

## 5.3 Dialogue study

Before finalizing large amounts of Elenwen writing:

- collect her vanilla dialogue lines;
- group them by context;
- identify recurring syntax, vocabulary, rhythm, forms of insult, degrees of formality, and strategic framing;
- build a short internal style sheet;
- use that style sheet for authored letters and dialogue.

Generated or AI dialogue systems must never grant authority or alter canonical quest state.

---

# 6. Dark Brotherhood Plan

## 6.1 Standing policy

Before direct Brotherhood contact, Cotta should receive a standing instruction covering suspected Dark Brotherhood activity.

The policy should be approximately:

- known Brotherhood operatives may be killed or captured on sight where practical;
- Cotta should gather usable intelligence when circumstances allow;
- once credible contact with the organization is established, its destruction becomes an active strategic objective.

## 6.2 Main objective

Once the Brotherhood directly contacts or attempts to recruit Cotta:

**Destroy the Dark Brotherhood.**

The player does not become a career Brotherhood assassin.

Commander Maro may function as a liaison.

He does not become Cotta's superior.

## 6.3 Implementation preference

Keep this module simple.

Prefer:

- standing order;
- event trigger on Brotherhood contact;
- activation of the vanilla destruction route;
- report to Elenwen;
- written assessment / reward through the EA service chain.

Avoid unnecessary rewrites of the Brotherhood questline.

---

# 7. Civil War Plan

Cotta is **not permitted to enlist with either side**.

Hard rule:

- no Imperial Legion membership;
- no Stormcloak membership.

The Civil War module should:

- block formal enlistment;
- preserve the Dominion preference for continued division;
- allow relevant observation / intelligence work;
- retain Season Unending;
- use the intended neutral / stalemate path;
- avoid a hot-war conquest ending.

The player may interact with both sides as part of other quests.

That must not become formal allegiance.

---

# 8. Dawnguard / Volkihar Campaign

This arc should be more developed than simply "join Volkihar as cover."

## 8.1 Phase One — Vampire intelligence

Before Cotta joins the Dawnguard, Elenwen becomes interested in reports of unusual vampire activity.

Early vampire assignments may include:

- investigate unexplained attacks;
- inspect sites associated with vampire activity;
- question or observe witnesses;
- recover documents or objects connected to vampire groups;
- determine whether reports of unusually powerful vampires are credible;
- identify references to vampire lords or organized vampire clans.

The purpose is intelligence gathering.

Cotta should not yet know the full Volkihar picture.

## 8.2 Phase Two — Find a better source

The investigation eventually establishes that ordinary field observation is insufficient.

Elenwen authorizes Cotta to find an organization with better access to vampire intelligence.

This leads to the **Dawnguard**.

Cotta joins / cooperates with the Dawnguard primarily because:

- they possess specialist information;
- they are actively hunting vampires;
- they may lead him to higher-value targets;
- they provide access that the Embassy lacks.

Cotta's primary loyalty remains to Elenwen.

## 8.3 Phase Three — Serana and Castle Volkihar

The Dawnguard quest naturally leads to Serana.

Her discovery changes the intelligence picture.

Cotta now has:

- a direct connection to an ancient vampire;
- evidence of a powerful organized clan;
- a route to Castle Volkihar.

This should trigger a mandatory report where timing permits.

## 8.4 Phase Four — Authorized Volkihar infiltration

Elenwen authorizes infiltration of the Volkihar clan.

This is a deliberate intelligence operation.

Cotta does not genuinely transfer allegiance to Harkon.

The mission objectives may include:

- gain access;
- determine Volkihar leadership and structure;
- assess Harkon's intentions;
- identify strategic threats;
- learn the significance of Serana;
- identify internal rivalries;
- report major discoveries;
- preserve cover until the operation no longer requires it.

## 8.5 Emergency authority

Vanilla Dawnguard scenes sometimes require immediate choices.

Do not pause live scenes to send correspondence.

Use standing and emergency authority.

Important decisions are reported afterward.

---

# 9. Main Quest / Diplomatic Immunity

This remains the **last major quest-family addition**.

Do not implement it early.

Reasons:

- broad vanilla quest dependencies;
- Delphine and Esbern aliases;
- Embassy scenes;
- essential / protected status;
- Blades cleanup;
- Paarthurnax;
- Season Unending interactions;
- high compatibility risk.

The final main-quest work should include:

- Dragonborn reporting;
- Delphine infiltration framing;
- Esbern;
- pro-Thalmor Diplomatic Immunity;
- Season Unending compatibility;
- Elenwen deciding Paarthurnax;
- Blades cleanup.

Diplomatic Immunity should be among the final pieces implemented after the rest of the service framework is proven stable.

---

# 10. Revised Implementation Order

## Phase A — Start revision

Build:

- Alternate Perspective start outside Northwatch;
- initial journal recap;
- civilian equipment;
- Elenwen packet;
- Establish Cover quest;
- Establishment Report;
- secure dispatch introduction.

Exit condition:

The player can start outside Northwatch, understand the premise entirely through the journal and documents, establish a civilian life, and file the first report.

## Phase B — Elenwen style pass

Build:

- vanilla dialogue corpus / notes;
- internal Elenwen style guide;
- rewrite prototype letters into final tone;
- first Establish Cover response;
- early service correspondence.

Exit condition:

The early game reads consistently in Elenwen's voice.

## Phase C — Authored service jobs

Build:

- 20-30 authored jobs;
- eligibility rules;
- specialty procurement;
- intelligence verification;
- retrieval;
- contact checks;
- limited administrative duties.

Exit condition:

Several in-game weeks of service can occur without repetitive cheap gathering quests.

## Phase D — Accounts refinement

Keep the existing accounts prototype.

Revise examples and claims so they connect to the better authored jobs.

Exit condition:

Advances, claims, debt, audits, and reimbursements function with real service content rather than prototype errands.

## Phase E — Dark Brotherhood

Implement the standing kill / capture policy and destruction route.

Exit condition:

Brotherhood contact reliably becomes an Elenwen-directed destruction operation.

## Phase F — Civil War

Block enlistment on both sides and preserve Season Unending / stalemate.

Exit condition:

No formal Civil War allegiance can contradict the campaign premise.

## Phase G — Vampire intelligence / Dawnguard

Build:

1. initial vampire investigations;
2. search for evidence of organized vampire lords;
3. authorization to use the Dawnguard as an intelligence source;
4. Serana report;
5. authorization to infiltrate Volkihar;
6. ongoing reports and emergency-authority handling.

Exit condition:

The player reaches Castle Volkihar as part of a coherent Elenwen operation.

## Phase H — Vice / NPC integrations

Continue the existing settled roster and indirect-consequence design.

Do not expose a vice stat.

Integrate only after the core service loop is enjoyable.

## Phase I — Main Quest last

Implement:

- Delphine / Esbern;
- Diplomatic Immunity;
- Dragonborn reporting;
- Season Unending glue;
- Paarthurnax decision;
- Blades cleanup.

Exit condition:

The main quest can be completed without contradicting Cotta's loyalty or breaking the established service framework.

---

# 11. Immediate Development Priority

The next playable milestone should **not** be another accounting feature.

It should be:

## Milestone: "Arrival and First Posting"

A fresh game should allow the player to:

1. spawn outside Northwatch;
2. read the detailed journal recap;
3. open Elenwen's packet;
4. receive civilian papers and modest funds;
5. leave Northwatch behind;
6. establish a legitimate civilian position;
7. secure lodgings;
8. file the Establishment Report;
9. receive Elenwen's assessment;
10. receive the first authored intelligence assignment.

This milestone should become the real beginning of the campaign.

Once this works in-game, expand the service job pool before touching the dangerous main-quest records.

---

# 12. Design Rule Going Forward

When choosing between:

- a large technical system that simulates many possibilities; and
- a small authored system that produces the exact role-playing experience wanted;

prefer the **small authored system**.

The mod should feel deep because its writing, timing, consequences, and quest framing are strong.

It does not need to be technically elaborate to achieve that.
