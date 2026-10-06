# Validation and manual test record

Automated validation covers compilation, Mutagen binary round trips, independent ESP structure/VMAD inspection, and execution of Caprica's emitted assembly with mocked Skyrim natives. Python graph serialization tests the test interpreter's persisted state only; it does not validate a Skyrim save.

## Automated tests

`python3 -m unittest discover -s tests` runs 120 tests (the build runs them after compiling and building the plugins):

| File | Tests | Covers |
| --- | --- | --- |
| `test_campaign.py` | 30 | The campaign on compiled Papyrus: phases, every instruction's conditions, nights and residence, the leash, letters, enclosures, actions, alternative replies, optional plugins present and absent, menu positions, serialization |
| `test_runtime.py` | 22 | Core, Dispatch (including `Send`), Accounts and the controller |
| `test_review_regressions.py` | 22 | Fixes from earlier reviews, kept as regressions |
| `test_start.py` | 13 | The Northwatch handoff, the packet beginning the campaign once, the console path, the dispatch case, the start quest's text |
| `test_content.py` | 13 | `campaign.json` rules: numbering, letter tradecraft (opens "C.,", closes "— E.", nothing named in clear), replies that do not explain, distinct texts, the record contract |
| `test_plugins.py` | 16 | ESP structure, VMAD properties against the scripts, array slots against `campaign.json`, the Arcanaeum form list, record IDs, and a scan of the emitted assembly for the Caprica register fault |
| `test_build_tools.py` | 4 | Packaging and compiler checks |

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

A4. **Packet.** Reading the packet once gives the residence order, civilian papers, the conditional release, the case instructions, *The Madmen of the Reach*, *The Bear of Markarth*, 100 gold and the Sealed Dispatch Case. Re-reading gives nothing more. The start quest completes, and the six Riverwood instructions appear in the inventory and journal.

A5. **Case.** Drop the case in an inn room, in a house and outdoors. Each time, the box appears where the case came to rest, upright and activatable, and the strongbox appears beside it.
- Pack and drop again. The archive's papers move with it.
- Store the case in a container: it must not unpack.
- Check save/load with the case packed and unpacked.

A6. **Console path.** Without `EA_Start.esp`, the placed test box commissions once, supplies the commission and 100 gold, opens the full menu and issues the Riverwood instructions.

## Required first game pass

Record game version, Creation Kit version, enabled plugins, exact load order and SHA-256 of each installed EA file. Use a fresh test character. Do not use a valued save for prototype tests.

1. Load all six ESPs in xEdit; check errors and verify the only records are new EA QUST/BOOK/MESG/CONT/ACTI/MISC/FLST records. Check VMAD links and masters' load order. Inspect/save a copy in Creation Kit and compare any changes before accepting them.
2. **Confirm every vanilla FormID** in docs/ARCHITECTURE.md in xEdit: that it is the form named, that each Location covers the place the order describes (the inn room under the Sleeping Giant's Location; Riverwood under Whiterun Hold; the Talos shrine and Understone Keep under Markarth), and that each quest stage the campaign uses (MG01 30, MG02/MG03/MG08 200, MG04 20) means what the order assumes.
3. **Residence.** Sleep at the Sleeping Giant: each wake counts one night; sleeping elsewhere does not. The Settled letter arrives after three nights, with the case notification. Inn (5 nights), Proprietor (8), Neighbours (7 days) and Roads (10 days) refuse with their own message until met, and nothing is filed. Confirm `OnSleepStop` fires after save/load.
4. **Leash.** After the first night, travel outside Whiterun and Falkreath holds: one trust loss and a three-day delay per absence, and at most one wander letter every three days. Inside the two holds (including Riverwood, Whiterun and Falkreath towns) nothing happens.
5. **Riverwood finds.** Visit Whiterun for the Preacher. Take the Thalmor Orders from Sanyon's body at the Talos shrine on the hillside near Riverwood, both before and after the residence, and file Hillside: the orders are removed once. Check they are not needed by any vanilla quest in the profile.
6. **Release.** After fourteen days of residence, earned money and level 6, before Diplomatic Immunity begins, the release letter arrives with *The Red Eagle*. Collect it: phase 2 instructions appear and the advance can be drawn.
7. **Jenassa and Accounts.** Draw the 500-septim advance, hire Jenassa at the Drunken Huntsman and file 2007 (she must be in `CurrentHirelingFaction`). Test each claim outcome on separate saves (500 approved; 650 allowed 500; 60 gift denied; 40 meal returned, then 20 or denied), repayment, and the 14-day audit.
8. **Markarth.** Complete The Forsworn Conspiracy and No One Escapes Cidhna Mine both ways (Madanach freed, and killed: the alternative reply and trust loss). The Feast needs The Taste of Death completed and Verulus dead. Give Ogmund's amulet to Ondolemar (2011). Visit the Talos shrine and Understone Keep. The Interval letter must follow once the phase weight is reached, and phase 3 has no instructions.
9. **College.** After seven days and a magic school at 20, the College letter arrives with its two books. With At Your Own Pace and College of Winterhold - Quest Expansion installed, then without each: admission (MG01 stage 30), Saarthal, the books, the monk, the Eye, the Arcanaeum book (any of the four, removed once), Winterhold's longhouse and Frozen Hearth, and the CQE reading test (issued only with CQE). The Adviser letter arrives when MG07 begins and grants removal authority only. Declining (AYOP Tolfdir as Arch-Mage) and accepting the chair each send their own letter.
10. **Menu positions.** With more than eight instructions open, File Report shows those ready to file first; an empty position (0) does nothing. Review status counts match the journal.
11. Save/reload before and after filing, during transit, at collection and during an Accounts transaction. Test death/reload at each handoff. Check for duplicate gold, books, enclosures or objective transitions, and inspect the Papyrus log.
12. Drop/sell/store player copies and remove archive copies. Recover filed copies: paper may be reprinted, but no monetary, authority or phase effect may repeat.
13. Read every letter in the game's book interface: titles fit the inventory list, and the letters follow the tradecraft rules in the campaign doc.
14. Run without optional UI mods, then under the intended profile. Verify no unexpected Helgen, main-quest or allegiance changes.

The wider matrix in the original specification remains pending, including every curated NPC, courier interruption, major quest route, and optional integration. A pass here does not certify those absent features.
