# Elenwen Agent: campaign opening, from Northwatch to the College

**Status:** agreed design, 2026-10-06. Not yet built.
**Relationship to other documents:** this supersedes sections 1–4 and 11 of `Elenwen_Agent_Revised_Implementation_Plan.md`: the start, Establish Cover, the early-game service structure and the "Arrival and First Posting" milestone. The plan's writing guide, the later phases (Dark Brotherhood, Civil War, Dawnguard and Volkihar, vice, main quest last) and its design rule still apply.

## Design rules for this arc

1. **Cotta is an underling.** He is given directions, not reasons. Reports state what he did; Elenwen's replies never explain what it meant.
2. **Vanilla content only.** Every job points at something already in the game: places, people, quests, books, items. The mod reads vanilla state and never changes it. The only exceptions are the mod's own papers and the dispatch case.
3. **No petty errands.** He is not a fetch boy. Jobs are reconnaissance, reading, and operations.
4. **Flexible, not sequential.** A job's condition is checked when he files, not counted from when he was asked. Anything he already did or found counts. Standing jobs have no deadlines and can be done in any order. A relevant find reported before it was asked for is accepted: *"I don't recall asking for this. I'll take it, of course."*
5. **Reading is sent, then suggested.** Her letters enclose one or two vanilla books to read and name further titles to find himself. Enclosed books are expected; suggested ones are never enforced, only remarked on if he holds them.
6. **Open-ended play between jobs.** How he lives, earns and trains is the player's choice; Missives, bounties and anything else count. Nothing in that space is tracked as a task.
7. **She is busy.** Letters are few. Silence is part of her character.
8. **Altmer superiors.** Elenwen and every Thalmor officer outrank him by birth. Ondolemar in Markarth treats him as beneath notice.

## Her voice (reference for every letter)

The source is her shipped lines and her letter to Agent Sanyon (`notes/elenwen-research.md`). The Phase B dialogue export will refine it.

**What she actually does:**
- **Letters are administrative first.** She opens with the matter, a date or a report reference: "In response to your report dated 22nd Morning Star 201, your request for an expeditionary force is hereby denied."
- **She addresses the agent by name,** and repeats it when irritated: "Agent Sanyon," … "Sanyon, this is the seventh report…"
- **Her irritation leaks through dashes and repetition,** occasionally an exclamation: "not one of your leads - not one! -", "better missions - better agents -", "No prisoners. No documents. Nothing!"
- **She gives practical, institutional reasons:** "Our forces are stretched thin enough as it is." The Concordat, treaty obligations, "my government".
- **Courtesy carries the condescension:** "Have you? All good, I trust." / "It pains the Altmer that we must remind our younger cousins…" / "One does not gather the most important men and women of Skyrim and then serve them cheap ale and stale bread."
- **She is sarcastic rather than cruel:** "Very well, Ulfric. Enjoy your petty victory." / "A very pretty speech, but…"
- **She is curt with subordinates in a weary, ordinary way:** "I've told you before not to bother me with such trifles."
- **She closes with a conditional instruction:** "If you feel so sure of your informant, investigate this yourself. Come back with proof. Or not at all."
- **She signs formally on official orders:** "By my hand and seal, / Elenwen". To Cotta she signs only "E." (see "Letter tradecraft").
- **She uses contractions freely** (I've, I'll, don't, it's), and she writes in full sentences of varied length.

**What to avoid (machine tells):**
- every line a polished two-beat epigram ("X. Not Y.", "That is why…", "It costs me nothing.");
- one-word verdicts used as punchlines ("Noted.", "Good.", "Received.") with nothing around them;
- symmetrical mottoes and triplets written to be quoted;
- vagueness for atmosphere. She names places, people, dates and amounts;
- an omniscient, mystical tone. She knows things because people report them to her, and she says so ("I'm told…", "I understand…").

## Letter tradecraft (rules for every letter between them)

Her open orders to Sanyon were Thalmor business between Thalmor. Cotta's letters are different: civilian couriers carry them, they sit in a box in a Nord inn, and they must survive being opened by the wrong person. These rules govern them. Her voice stays; only the identifying detail goes.

1. **Initials only.** He is **"C."**; she signs **"— E."** Never "Cotta" or "Elenwen", and never "By my hand and seal". That formula belongs to her official orders, and it is exactly what an informant would recognise.
2. **No institutions in clear.** Never write "Embassy", "Thalmor", "Dominion", "Justiciar", "First Emissary" or "Concordat". Use the house terms:

   | Term | Means |
   |---|---|
   | **the house** | the Thalmor Embassy |
   | **Accounts** | the Embassy's accounts office (harmless on its own) |
   | **our friend in the Keep** | Ondolemar, in Understone Keep |
   | **our friends** | the Thalmor generally |
   | **the keep** | Northwatch |

3. **People by description, never by name**, when they are targets or sensitive:
   - **the proprietor**: Delphine
   - **the adviser**: Ancano
   - **the old man in the mine**: Madanach
   - **the skald**: Ogmund
   - **the man on the hillside**: Sanyon
   - **the Dunmer**: Jenassa

   Public figures named in ordinary gossip (a Jarl, a town) may be named.
4. **Nothing about his past.** No Northwatch, no questioning, no mention of what she holds over him. One exception: the conditional release itself, which he carries.
5. **Need to know.** She never explains a purpose, never mentions other agents, and never confirms what a report meant. A reply acknowledges, restricts or redirects.
6. **No locations of her own.** She never says where she is, where the house keeps anything, or who else reads his reports.
7. **Dates by the calendar, quantities exact.** That's administrative precision, without identifying detail.
8. **Authentication.** Every genuine letter is sealed in plain wax with no device and signed "E." A letter signed in full, or one naming the Embassy or the Thalmor outright, is not from her. This is a hook for a forged letter later.
9. **Sensitive orders say so.** *"Burn this."* is used sparingly, on the few letters that would hang him: the Markarth order, the order on the adviser. It's flavour; the mod can't force him to destroy anything, and the dispatch archive keeps the house's copies regardless.
10. **His reports follow the same rules.** They're signed "C.", use the house terms, and never name her.
11. **The exceptions are papers that are meant to be official:** the conditional release, Accounts receipts, and Sanyon's orders (which are vanilla, and were written to a Thalmor agent). They keep their formal style, and that contrast is part of the fiction.
12. **The journal is exempt.** It is his own thoughts, not a document anyone can intercept, so it may name Northwatch, Elenwen and the rest.

**For the content tests:** letters must open "C.," and close "— E."; must not contain the names and institutions above in clear; and must not contain "By my hand and seal". The old bans on "!" and very short length are dropped.

## 1. Premise

- Cotta is a young Imperial, taken from Imperial territory and transferred north to **Northwatch Keep** under Dominion authority. Skyrim is his first posting, so he doesn't know the land, its people or its war.
- At Northwatch, **Elenwen conducted his final questioning herself**, as she prefers to (Rulindil's letter: "I know you prefer to be present for the final questioning"). She gave him something to believe and let him out. This is her documented method: it is how she made Ulfric an asset (*Thalmor Dossier: Ulfric Stormcloak*). Ulfric became "Asset (uncooperative)". Cotta is the method working.
- **Why he is devoted:** for weeks she was the only person who decided anything about him, and she chose to release him. Whether that bond was earned or engineered is never answered.
- **The hold:** his release is conditional and revocable. Neither he nor the player is ever told why he was held.

## 2. Start (Alternate Perspective)

- **Registration:** a JSON entry, "Elenwen's Agent". The start quest moves him outside Northwatch at once. The garrison's reversible faction courtesy lasts until he leaves the area. Helgen and AP's own records are untouched (already built and tested in the simulator).
- **Journal recap:** the transfer, the sealed instructions, his belongings held and returned, released by Elenwen's order, not to report to the Embassy. One line on the question: *"I don't know whose order put me in Northwatch. I know whose order got me out."*
- **The packet:** her letter, civilian papers, a conditional-release copy stamped "revocable", a small allowance, and the portable dispatch case.

## 3. Riverwood: the sleeper (about two weeks)

**Order:**
> C.,
>
> By the time this reaches you, the keep will have returned your belongings and put you outside its gate. Do not mistake that for liberty.
>
> You are to go to Riverwood, in Whiterun Hold, and take a room at the Sleeping Giant Inn. Keep it. Earn your living however a freelancer earns his: cut wood, hire out your sword, I really don't mind which, provided none of it brings you to the attention of a Jarl's steward. You are not to travel beyond Whiterun and Falkreath without my leave.
>
> You will hear from me when I have a use for you. Until then, I would much prefer not to hear from you at all.
>
> — E.

**The unstated reason:** Delphine. The Thalmor dossier has her as "Active (Capture or Kill)", with "no location on her", and "extremely alert to our surveillance". A trained watcher would be spotted. A bored Imperial who knows nothing would not. **His ignorance is the cover.** Elenwen never names her.

**Silently tracked:** nights he wakes at the Sleeping Giant (vanilla sleep events and the inn's Location), his own earnings, player level, and leaving Whiterun or Falkreath holds.

**Letters:** two at most.
- **When he's settled:** *"I'm told you've taken a room at the Sleeping Giant, and that you pay for it on time. Good. Keep it that way. — E."*
- **If he wanders:** *"C., I understand you were in Windhelm on the 14th. I don't recall giving you leave to go to Windhelm. Perhaps you'll be good enough to explain what took you there. No, on reflection, don't. Return to Riverwood and stay there. — E."*

Wandering costs trust and delays release; nothing worse, because he obeys anyway.

**Recon** (standing jobs, all issued with the residence order, no deadlines, any order):

| # | Order | Vanilla content | Report condition, checked when filed |
|---|---|---|---|
| 1 | Note who comes to the inn twice | The Sleeping Giant has no repeat guests | Enough nights at the inn |
| 2 | The proprietor's hours and company | Delphine; Orgnar: "That's her business" | Enough nights at the inn |
| 3 | Which neighbours pray to the Ninth | Gerdur and Hod (Stormcloak, Ralof's family); Alvor (Imperial-leaning, Hadvar's uncle) | Time in residence |
| 4 | The man who preaches Talos in Whiterun: do the guards stop him? | Heimskr at the Wind District shrine | Has been to Whiterun at any point |
| 5 | Which soldiers use the roads, in what colours | Vanilla Imperial and Stormcloak patrol encounters | Time and travel |
| 6 | An agent stopped reporting near Lake Ilinalta: find out why | *Shrine of Talos: Ilinalta Foothills*. Agent Sanyon dead among four worshippers, carrying *Thalmor Orders* in which Elenwen refused him men: "Come back with proof. Or not at all." | Delivers the orders, whenever he found them. If he arrives with them before the order exists, they are accepted as an unsolicited find |

**Reading:**
- **Enclosed** with the residence order: *The Madmen of the Reach* and *The Bear of Markarth*, two vanilla books handed over by the mod. *"Two books accompany this letter. Read them. The Reach will not explain itself to you, and I haven't the time to do it for it."* Being asked about them is fiction; nothing is tested.
- **Suggested:** *The City of Stone* (a sellsword's guide to Markarth), plus any other title on the Reach. Elenwen remarks on them if he holds them; they are never required. Whiterun copies of the enclosed titles exist too (Dragonsreach and Jorrvaskr), so a player who loses his can find them again.

Reply to job 6:
> C.,
>
> Your report concerning the man on the hillside has been received, together with a letter of mine I am not in the habit of having returned to me. It appears his informant was reliable after all. That doesn't change the fact that he went to that hillside alone, which I don't recall advising. The shrine will be attended to. You will say nothing about any of this in Riverwood.
>
> — E.

**Release:** about 14 days at the inn, plus his own earnings and a level of 5–8. Recon need not be finished: anything unfiled stays open and can be reported later, from anywhere. If the main quest has already reached Delphine's reveal, that becomes a separate branch for a later phase.
> C.,
>
> Riverwood has served its purpose, and so, for the moment, have you.
>
> There is a Dunmer who drinks at the Drunken Huntsman in Whiterun who will sell her sword to anyone with the coin. Hire her. Accounts will advance her fee, and I trust you won't mistake it for an allowance. When that's done, go to Markarth. My instructions for Markarth accompany this letter, along with something on the Reach you haven't read yet.
>
> — E.

## 4. Jenassa

- **Hire her:** a Dunmer, deniable and not Thalmor. Accounts advances her 500-septim fee; unspent money is returned and claims are filed as already built. Hiring is recognised from her vanilla follower status.
- **Afterwards:** *"You may keep the Dunmer on, if you find her company agreeable. You'll pay for it yourself, naturally. — E."* This seeds the vice roster without stating it.

## 5. Markarth: "keep the Reach burning"

Elenwen's real policy, from the Ulfric dossier, is an indecisive war: no clean victory for either side. Markarth is Imperial-held under Jarl Igmund.

**Reading before he goes** (in the release letter): enclosed, a further Reach title not yet read. Suggested, anything on the Silver-Blood family or Cidhna Mine he can find.

> C.,
>
> The Reach has been unusually quiet of late, and I find I don't care for it. Our friend in the Keep writes diligent, thorough reports that tell me nothing at all.
>
> You will go to Markarth as what you appear to be, a sellsword in want of work. You'll find the city has no shortage of people at one another's throats. See that they stay there. How you manage it is your own affair; I shall judge you by the state of Markarth when you leave it.
>
> Our friend in the Keep is not to know you are mine. He would only want to help.
>
> Burn this.
>
> — E.

| Goal | Vanilla quest and choice | Detected by (read only) |
|---|---|---|
| Learn who runs the city | *The Forsworn Conspiracy* (begins at the market murder) | Quest stages |
| Free Madanach | *No One Escapes Cidhna Mine*: Forsworn option | Quest complete, Madanach alive |
| Shelter the Namira coven: she wants the names | *The Taste of Death*: Eola's side | Quest complete, Verulus dead |
| Ogmund's amulet goes to **Ondolemar** | Ondolemar's vanilla request to prove the skald Ogmund's Talos worship | Ondolemar's request completed. Her reply: *"I understand our friend in the Keep has his skald at last. He'll be insufferable about it for weeks. Still, it costs the house nothing, and it keeps him occupied."* |
| Leave the Talos shrine standing; report it to her only | The shrine below Markarth | Visit and report |
| Thongvor Silver-Blood's ambition (optional) | His vanilla Stormcloak sympathies | Report |
| Calcelmo's translations (optional; foreshadows the College) | The Jarl's Altmer Dwemer scholar | Visit and report |

- **Arrest:** his case is confiscated with his belongings. If he escapes with the Forsworn, Kaie returns his gear, and the letters are waiting.
- **Replies:**
  - **Freed Madanach:** *"I'm told the old man in the mine is loose in the Reach and the Jarl can talk of nothing else. Good. That is very much what I sent you there to do."*
  - **Killed Madanach:** *"The Jarl is grateful, I hear. He has pardoned you, and the Silver-Bloods have given you a ring. How very nice for you. I did not send you to Markarth to be thanked by Nords."* That costs trust, not the operation.
- **Exit:** the Reach is "burning", meaning Madanach freed or at least two other goals met.
- **Note:** freeing Madanach and joining the coven are morally heavy, player-chosen paths. Elenwen only judges results.

## 6. Interval

A deliberate gap with **no assignments**: *"I have nothing for you at present. Use the time. Your magic is an embarrassment and your history isn't much better, and I'd like both improved before I next have need of you. — E."* Open play, with no tracked tasks. It ends after a set time and once he can pass a basic magic test.

## 7. The College of Winterhold

Inspected: **At Your Own Pace 2.1.0** (College) and **College of Winterhold - Quest Expansion 1.16**. Both are ESL plugins, and neither has Thalmor content. Both override `MG01`, with the same stage numbers.

- **Order:**
> C.,
>
> You will go to Winterhold and present yourself to the College as a prospective student. Our friends keep an adviser there, whose standing among the masters I would like to understand rather better than his own reports allow. Learn what weight he carries, and who listens to him.
>
> You are a student and nothing more. You will not tell the adviser who sent you. He has no need to know, and I suspect he wouldn't take it well.
>
> — E.
- **Reading:** the order encloses one or two vanilla books on the College's subjects: the Dwemer, the Snow Elves and Saarthal, the Psijics. Later letters suggest further topics as the questline reaches them.
- **A book for her, if possible:** *"The College keeps a library (the Arcanaeum, I believe they call it) with a number of volumes the house has never managed to acquire by honest means. Should one of them leave the building without the librarian noticing, I'd be glad to have it. I would rather not hear that you were caught."* This is optional and flexible: any title from a short list of Arcanaeum books, stolen from Urag and delivered through the case at any time. Being caught is his problem. A delivered book earns *"The book arrived safely. I trust the Orc hasn't noticed yet."*
- **Winterhold itself,** a standing recon job: *"While you're there, learn what the town thinks of the College, and of its Jarl. I don't imagine it will take you long."* In vanilla, the town blames the College for the Great Collapse, and Jarl Korir is a Stormcloak loyalist. Condition: time spent in Winterhold's town Location. Reply: *"Thank you for your report on Winterhold. It is very much as I expected: a ruin with a Jarl in it. You needn't trouble yourself with the town again."*
- **Admission check:** College faction membership, or `MG01` at stage 30 or later. `MG01` runs from the start of every game, so "has begun" is meaningless.
- **Reports at College beats**, read from vanilla stages, with one report and one reply each:
  - admission;
  - Quest Expansion lessons (optional, through `GetFormFromFile`). After Urag's lesson: *"I'm told the librarian has been teaching you to weigh your sources. An Orc, teaching method. Skyrim never stops surprising me."*;
  - *Under Saarthal*;
  - *Hitting the Books*;
  - *Good Intentions* (Ancano takes him to the Psijic monk; a mandatory report);
  - *Containment*;
  - *The Eye of Magnus*.
- **Ancano:** after *Containment*, Elenwen disowns him and orders him **eliminated**:
> C.,
>
> I have read your report twice. Whatever the adviser believes he is doing at the College, he is not doing it on my authority, and I won't have the house's name attached to it.
>
> You are authorised to see that he does not leave Winterhold. I trust I needn't explain what that means.
>
> Afterwards there will be a great deal of talk, and none of it will be yours.
>
> Burn this.
>
> — E.
 Removal authority is granted through Core's authority system. Vanilla *The Eye of Magnus* then carries it out. Her reply afterwards: *"The adviser is dead, I'm told, and the College is calling it an accident of his own making. That is precisely what the house will call it, too."*
- **Arch-Mage:** she orders him to **decline**; At Your Own Pace lets Tolfdir take the chair. Declined: *"You turned down the Arch-Mage's chair. Good. Everyone watches an Arch-Mage, and you are no use to me watched."* Accepted: *"So you're Arch-Mage. I didn't ask for that, and I'll be very interested to learn how you mean to remain useful to me now that every fool in the College is watching you."*
- **Pacing:** At Your Own Pace's pauses between chapters are where her letters land. If a later beat arrives before an earlier report is filed, the reports fold together.

## 8. Delivery and reporting

- **During Riverwood:** orders and replies appear in the dispatch case in his room, delivered on waking. **Enclosed books are added with the letter.**
- **After release:** new orders come by vanilla courier. Reports and deliveries go through the case, wherever he lodges. Replies take one day.
- **Unsolicited finds:** if he files something relevant that wasn't asked for (Sanyon's orders before the order exists, a Reach book before Markarth), it's accepted and acknowledged.
- **Every report is an instruction with a hidden condition:** nights at a place, a visit after the order, an item held or delivered, a vanilla quest stage or outcome, or time. Until the condition is met, filing is refused with a plain reason.

## 9. What already exists, and what changes

**Reused:**
- the Alternate Perspective start and Northwatch handoff;
- the portable dispatch case;
- Core, Dispatch and Accounts, including the authority system;
- the packet circulation and visit, item and lead checks;
- the record contract.

**Replaced:**
- the current 12-instruction job pool;
- the five-occupation Establishment Report;
- the "first lead third" ordering.

Their records are retired under the existing contract.

**Writing changes:** the content tests follow "Letter tradecraft". They require "C.," and "— E.", reject names and institutions in clear and "By my hand and seal", and no longer ban "!" or limit length.

**New mechanics:**
- sleep-triggered delivery and residence tracking at a named Location;
- the hold leash;
- enclosed books (vanilla books handed over with a letter) and suggested reading (books held, remarked on and never required);
- conditions checked when filed, with no "since the order" requirement, and unsolicited reports;
- the Arcanaeum book delivery and the Winterhold residence recon;
- vanilla-quest **stage and outcome** checks (beyond "has begun");
- the Jenassa follower check;
- the College beat reports;
- the Ancano removal grant;
- the Arch-Mage outcome check.

**To confirm in game, or with `Skyrim.esm`:**
- the *Thalmor Orders* item ID;
- whether the massacre site has a Location record;
- the IDs for *The Bear of Markarth* and the Talos shrine below Markarth;
- the IDs for Ogmund's amulet and Ondolemar's request quest;
- the Arcanaeum book list, choosing titles found only there;
- the Winterhold town Location, and whether the College lies inside it;
- the Madanach, Verulus and Jenassa actor references;
- the main-quest stage at which Delphine reveals herself;
- AP, At Your Own Pace and Quest Expansion behaviour in a real load order.

## Build deviations (0.4.0)

The 0.4.0 build differs from the text above in these points:
- **Riverwood reading.** The residence order encloses *The Madmen of the Reach* and *The Bear of Markarth*, and suggests *The City of Stone*.
- **Release.** The release letter encloses *The Red Eagle*.
- **Delivery.** Orders and letters arrive in the dispatch case, not by the vanilla courier.
- **Unsolicited finds.** There is no separate unsolicited report. Each phase's instructions are issued when the phase begins, and conditions are checked when the report is filed, so a find made before it was asked for is recognised then.
- **Remark letters** on suggested reading were dropped.
