# Validation and manual test record

Automated validation covers compilation, Mutagen binary round trips, independent ESP structure/VMAD inspection, and execution of Caprica's emitted assembly with mocked Skyrim natives. Python graph serialization tests the test interpreter's persisted state only; it does not validate a Skyrim save.

Game validation status: **not run**. Creation Kit/xEdit validation status: **not run**. The workspace contains neither the game nor the required dependency records.

## Phase A: the Alternate Perspective start

Run these first, with Alternate Perspective 4.x, SKSE and JContainers installed. Record the Alternate Perspective version.

A1. **Registration.** Alternate Perspective's menu lists **Elenwen's Agent** with its description. Choosing it starts `EA_StartQuest`, with no "Failed to start Intro Quest" or "You seem to be stuck" message. If either appears, the map-marker alias did not fill: inspect `NorthwatchKeepLocation` (Skyrim.esm `019285`) and its map-marker reference in xEdit.

A2. **Arrival.** The player arrives just outside Northwatch Keep, in the open and not inside geometry, with AP's starting clothes, an iron dagger and the Sealed Packet. Exactly one of each is present.
- The journal shows the recap and "Read Elenwen's sealed packet".
- The garrison does not attack while the player stays near the marker.
- Walk away beyond about 60 metres, wait 10 seconds, and check `player.getinfaction 000C0637` returns 0.
- Return later: the garrison behaves as vanilla. If attempted, Missing in Action still works.

A3. **Helgen.** Helgen remains intact and dormant: the MQ101 stage is unchanged and there is no dragon. It activates only through AP's own route (sleeping in the Helgen inn bed) and then plays normally.

A4. **Packet.** Reading the packet once gives the letter, civilian papers, instructions, blank form, 100 gold and the Sealed Dispatch Case. Re-reading gives nothing more. The objectives change to the four Establish Cover objectives.

A5. **Case.** Drop the case in an inn room, in a house and outdoors. Each time, the box appears where the case came to rest, upright and activatable, and the strongbox appears beside it.
- Pack and drop again. The archive's papers move with it.
- Store the case in a container: it must not unpack.
- Check save/load with the case packed and unpacked.

A6. **Report gates.** Immediately after opening the packet, try every occupation and every lodging. Each must be refused with its specific reason, and nothing filed. Then satisfy one route at a time on separate saves:
- join a guild;
- make three items;
- kill five animals;
- complete one quest or misc objective;
- read two skill books or learn spells.

Also sleep in a rented bed, buy a house, and use guild quarters (Companions, College, Thieves Guild; Bards must be refused). **Confirm each statistic name works in this game version** (`Weapons Made`, `Armor Made`, `Potions Mixed`, `Magic Items Made`, `Animals Killed`, `Quests Completed`, `Misc Objectives Completed`, `Skill Books Read`, `Spells Learned`, `Training Sessions`, `Hours Slept`, `Houses Owned`, `Most Gold Carried`). Check that `SolitudeBardsCollegeFaction` is the faction the player actually joins.

A7. **Assessment.** File, wait 23 and then 24 hours, and collect the assessment. Check:
- the matching occupation letter and the field papers arrive once;
- the quest completes;
- the main menu replaces the report menu;
- Collect Orders issues 1001–1003, and 1001 can be filed after reading the field papers;
- the result is the same after save/load mid-transit.

A8. **No regressions on the console path.** Without `EA_Start.esp`, the placed test box still commissions, supplies and opens the full menu.

## Required first game pass

Record game version, Creation Kit version, enabled plugins, exact load order and SHA-256 of each installed EA file. Use a fresh test character. Do not use a valued save for prototype tests.

1. Load all six ESPs in xEdit; check errors and verify the only records are new EA QUST/BOOK/MESG/CONT/ACTI records. Check VMAD links and master's load order. Inspect/save a copy in Creation Kit and compare any changes before accepting them.
2. Place one box, verify its strongbox mesh, activation and paper UI. Verify its archive appears nearby and does not respawn. Check another interior after the cell unloads; verify the original box and archive persist.
3. Open the commission once. Confirm exactly one commission, one field-paper copy and 100 gold. Reopen the box and place/activate a second test box: supplies must not repeat.
4. Read field papers both before and after collecting orders, file protocol, and attempt to repeat it. Turn in supplies with too few, exactly enough, and excess items. Only the required quantity should be consigned, once, and delivered goods must not appear in the paper archive.
5. Check responses at 0, 23 and 24 game hours. Test ordinary travel, wait/sleep, and a long menu session. Collection must use game time and work even if a notification was missed.
6. Save/reload before and after filing, during transit, at response collection, during an Accounts transaction, and after delivery. Test death/reload at each handoff. Check for duplicate gold, books, or objective transitions and inspect the Papyrus log.
7. Drop/sell/store player copies and remove archive copies. Recover filed copies. Physical paper may be reprinted, but no monetary or authority effect may repeat.
8. Test a report on the tenth day, after it, and after a long delay. An assignment becomes overdue but remains completable. Test first extension approved, second refused, further requests making no transaction, completion while an extension is in transit, and balanced nested suspension/resume hooks in a debug build. Inspect each extension paper for the correct instruction number.
9. Request advance authority. Before collection, no advance should be available. After collection while the wine duty is open, collect 80 exactly once. Authority must not affect other categories or operations.
10. Use separate test saves for each claim outcome. With an advance, a 30-septim valid claim leaves 50 outstanding and pays no extra gold. An 80-septim claim allows 30 and leaves 50 debt. A 30-septim gift claim leaves 50 outstanding plus 30 debt. Without an advance, a valid claim pays 30 once, and a denied gift creates no Embassy debt.
11. Test both meal explanations and their distinct papers, a returned claim across save/reload, insufficient gold when returning funds, 14-day audit despite an uncollected response or unanswered explanation, actual transit briefly deferring audit, repayment clearing probation, and a valid claim after audit.
12. Collect orders: exactly 1001–1003 arrive. Confirm File Report, Request Extension and Review status show those three numbers by position, and that an empty position (shown as 0) does nothing. File one report: its position stays occupied until the completion reply is collected. Collect it, verify one packet notice, wait several days, then Collect Orders: exactly the next instruction arrives, with ten days remaining. Repeat collection without resetting deadlines or duplicating orders or case papers.
13. For each named item, confirm in xEdit and in game that the FormID in docs/ARCHITECTURE.md is the object the order names, that its display name matches the order, and that it can be bought or found where the order implies. Test a shortage, the exact count and a surplus. Then test the near substitutes: Alto Wine (both base objects) and plain Wine for 1002; another volume of *The Rising Threat* for 1007; Skooma for 1011. Each must be refused with nothing taken. Check that no item is quest-reserved in the installed profile; in particular, check whether Honningbrew Mead stays obtainable before and after the Thieves Guild meadery quest.
13a. **Named places.** For each place instruction (1003, 1005, 1006, 1008, 1010, 1011), file before going: refused with the place's message, and nothing taken. Then check these each count:
- arriving after the order (including entering a building inside the named place);
- arriving before the order and staying (no);
- arriving after the report (no).

Confirm each Location covers what its order describes: the College under Winterhold, the meadery's interior under its Location, the caravan camp under the Windhelm stables.

**Leads.** For 1003, 1006 and 1010, confirm the report is refused until The Forsworn Conspiracy, First Lessons and Missing in Action respectively have begun, and accepted afterwards. Accepted also when the quest was already completed earlier, for example through an Alternate Perspective guild start for the College. Confirm EA never changes those quests' stages, and that `MS01`, `MG01` and `MS09` are those quests in this game version.
13b. Review every order and reply in the game's book interface. The in-game titles must fit the inventory list. Read each Elenwen letter against the Continuation 01, section 6.8 checklist; record lines to revise in Phase C.
14. Open Review status at active, overdue, filed and completed stages. Check decimal days and ready/in-transit counts against the journal and elapsed game time. Ensure the nine-button main menu, and the four-button positional assignment menu with its instruction numbers remain legible using the vanilla interface. Cancel every menu, including status and repayment; no transaction or failure message should follow cancellation.
15. File reports with at least five days remaining, under five days remaining, and after a missed deadline. Inspect each corresponding Elenwen letter. An approved extension after a missed deadline must not erase the late history, and leaving an early reply uncollected must not turn it into a reprimand. Check the chosen Accounts decision's remarks.
16. Repay 10, 25 and all funds; repeat with fewer septims than requested and a balance smaller than the request. Confirm the exact amount in inventory, the confirmation, and Accounts statement, then save/reload and recheck. There must be no negative balance or duplicate reimbursement when a subsequent claim settles.
17. Complete the whole series with clean records, one missed deadline, repeated lateness, a partial claim, a denied claim and unsettled funds on separate test saves. Check the correct closing assessment, one further day of transit, its journal objective and lost-copy recovery. It must not be issued twice or grant rank, authority or money. With a pending/returned meal claim, the review must wait for explanation and decision. A fully returned advance before its due date must not leave an adverse audit finding.
18. Run without optional UI mods and SKSE. Then repeat under the intended installed profile. Verify no unexpected Helgen/main-quest activation or allegiance changes; this build should have no hooks into those systems.

The wider matrix in the original specification remains pending, including every curated NPC, courier interruption, Alternate Perspective, major quest route, and optional integration. A pass here does not certify those absent features.
