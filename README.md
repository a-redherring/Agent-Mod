# Elenwen Agent — Skyrim SE/AE technical prototype

**Version 0.3.0-prototype. This is an installable development build, not the completed mod described in [the specification](Elenwen_Agent_Mod_Build_Specification.md), its [Continuation 01](Elenwen_Agent_Mod_Build_Specification_Continuation_01.md) and the [Revised Implementation Plan](Elenwen_Agent_Revised_Implementation_Plan.md), which now sets the build order. It has been compiled and tested outside Skyrim; it has not been run in the game.**

The repository began with the design specification only. This implementation builds its first paper-based service loop using real ESP records and compiled Papyrus scripts. No Skyrim installation, Creation Kit, Alternate Perspective plugin, Sinister Serana plugin, or installed load order was available for record inspection or playtesting.

## Included

- **An Alternate Perspective start, "Elenwen's Agent"** (revised plan, Phase A). The player begins just outside Northwatch Keep with the transfer already complete. The journal explains what happened; there is no custom scene. Northwatch's garrison leaves the player alone until they leave the keep, after which its own quest is unaffected.
- **Elenwen's sealed packet**: her letter, civilian papers, dispatch-case instructions, a blank Establishment Report form, a 100-septim allowance and the dispatch case itself.
- **Establish Cover**, with no fixed career. The Establishment Report is accepted only when the game's own records support it:
  - an occupation, either guild membership or work done since arrival (crafting, hunting, completed jobs, or study);
  - lodgings, either a room slept in, a house owned, or guild quarters;
  - money earned that was not issued.

  Elenwen's assessment follows a day later, with the field papers, and service begins.
- **A portable dispatch case.** Set down outside the inventory, it opens into the secure dispatch box; it can be packed up again. Filed correspondence travels with it and can be opened from the box.
- A physical secure dispatch activator and a persistent, non-respawning document archive.
- A confidential commission, private field papers, and a one-time 100-septim allowance.
- Twelve authored instructions (1001–1012), issued in a fixed order with at most three open at once. The officer is an **underling**: orders give directions, not reasons, and Elenwen's replies acknowledge, restrict or criticise but never explain what was found. An instruction rests on one or more of:
  - **a named place**, which counts only when the player arrives there after the order was issued (Markarth, Honningbrew Meadery, Winterhold, Whiterun, the stables outside Windhelm);
  - **a named item**, a specific vanilla base object: Solitude spiced wine, *The Rise and Fall of the Blades*, Honningbrew Mead, *The Rising Threat, Vol. I*, *The Book of the Dragonborn*, jazbay grapes, moon sugar or a roll of paper;
  - **a lead into a vanilla quest of Thalmor interest.** The report waits until that quest has begun, however the player pursued it, and the instruction never advances it. The leads are the trouble in Markarth's market (*The Forsworn Conspiracy*, with the Embassy's representative in Understone Keep), admission to the College of Winterhold (*First Lessons*, with the Thalmor adviser), and the Gray-Mane family asking after a prisoner (*Missing in Action*). The first lead is the third instruction.
- 133 readable orders, reports, requests, decisions, assessments and receipts. Extensions identify their assignment; meal explanations preserve the chosen declaration. Responses take one game day and must be collected physically.
- Ten-day deadlines, overdue state with one trust consequence, and a five-day extension followed by refusal of a second extension.
- Core authorization scoped to operation and decision category, including emergency review functions for later modules.
- A single accounts case for the spiced wine purchase (instruction 1002): authorized 80-septim advance, declared claims, all four outcomes, explanations, return of funds, a 14-day audit, and liability/probation. Recognized costs settle the advance before any reimbursement.
- A dispatch status register with active/overdue/filed/completed counts, ready/in-transit replies, and per-instruction remaining days. Specific feedback explains missing items, unread case papers, permissions, pending requests, and settled claims.
- Elenwen replies differently to prompt, ordinary, and previously overdue work, Her letters follow the voice guide in Continuation 01, section 6. Accounts letters address the chosen expense. A delayed closing assessment follows the last instruction and any pending claim decision; late and misjudged reports both count against it.
- Partial repayments of up to 10 or 25 septims, or all affordable outstanding funds, with confirmation of the actual payment and remaining balance.
- Replay protection for commissioning, orders, deliveries, responses, advances, and claim payments; recovery of lost paper copies.

All public text is SFW. Hidden trust and creditworthiness are not displayed. Every plugin masters only `Skyrim.esm` and other EA plugins, and none overrides a vanilla record. The start option appears only with Alternate Perspective, which itself needs SKSE and JContainers; the EA scripts use no SKSE functions. These ESPs are intentionally **not ESL-flagged**.

## Install and try it

1. Use a separate Skyrim Special Edition / Anniversary Edition **test profile and fresh save**. LE and VR are not supported targets. SE/AE runtime compatibility has not been playtested.
2. Install `dist/ElenwenAgent-0.3.0-prototype.zip` through MO2 or Vortex. The ZIP root is the Data directory. For manual installation, copy its ESPs and `Scripts` directory into the test installation's Data folder.
3. For the intended start, also install [Alternate Perspective](https://www.nexusmods.com/skyrimspecialedition/mods/50307) 4.x with its requirements (SKSE and JContainers). The package's `SKSE/AlternatePerspective/ElenwenAgent.json` registers the start; `EA_Start.esp` does not list Alternate Perspective as a master. Enable this order after the game's official masters and Alternate Perspective:

   ```text
   EA_Core.esp
   EA_Dispatch.esp
   EA_Service.esp
   EA_Accounts.esp
   EA_Prototype.esp
   EA_Start.esp
   ```

4. Start a new game and, at Alternate Perspective's start menu, choose **Elenwen's Agent**. You arrive outside Northwatch Keep. Read the journal, then read the **Sealed Packet** in your inventory.
   - Drop the **Sealed Dispatch Case** wherever you intend to live; after a moment it becomes the dispatch box.
   - Make a civilian life: join a guild, or make things, hunt, finish paid work or study. Take lodgings and earn more money than you arrived with.
   - At the box, choose **File Establishment Report**. A declaration the game cannot support is refused with a reason, and nothing is filed.
   - After a full day, **Check Responses** for Elenwen's assessment and the field papers. The full menu then opens.

   *Without Alternate Perspective* (prototype testing): open the console in a safe interior, run `help "EA_SecureDispatch" 4`, then `player.placeatme <the ACTI FormID returned> 1`. The local ID is `000800` in `EA_Prototype.esp`. Opening the commission there presumes an existing cover and skips the start.

5. Once the cover is accepted, choose **Collect Orders**. Three instructions arrive: 1001 (field protocol), 1002 (Solitude spiced wine) and 1003 (*The Rise and Fall of the Blades*). Read the field papers in your inventory; reading them before collecting orders also counts. Filed correspondence is in the strongbox beside the dispatch box, or under **Case and archive → Open filed correspondence**. Delivered items are consigned immediately and cannot be taken back from this paper archive.
6. **File Report** and **Request Extension** list the open instructions by position (first, second, third) with their numbers; the number is printed on each order. File the protocol acknowledgment. Obtain three bottles of Solitude spiced wine and one copy of *The Rise and Fall of the Blades* for the other two. Alto or other wine, or another book, is refused without anything being taken. Return after 24 game hours and choose **Check Responses**.
7. To test Accounts, request supply authority **before filing the wine delivery**, wait a day, collect the authorization, then collect the advance under **Accounts**. After delivering the wine, submit one of the declared claim forms. Each claim/explanation needs its own return dispatch.
8. Each collected completion response frees a position. Choose **Collect Orders** again to receive the next instruction; its ten-day deadline begins on collection. Some instructions name a place to go; a report filed before you have been there is refused with nothing taken. Three of them lead into vanilla quests, and their reports wait until you have actually got involved.
9. Use **Review status** to inspect the register and individual open instructions. Under **Accounts → Return outstanding funds**, choose a partial payment or all affordable outstanding funds.
10. After all twelve completion responses and any pending Accounts decision have been collected, a closing review is sent automatically. Wait another full game day and collect Elenwen's assessment. A returned meal claim must first be explained and settled. The assessment reflects the record when the review was sent; later actions do not rewrite it.

Supply cost forms are the player's **declarations**; this build does not track vendor transactions. Only one claim is allowed for instruction 1002. Use separate fresh test saves to exercise the four different outcomes. The twelve instructions do not regenerate, and only instruction 1002 has an advance or claim. Instruction 1007 is a personal request and says so. The item references and their in-game names, prices and availability have not been checked in the game; see [manual game validation](docs/TESTING.md).

After fourteen days, Accounts audits an unreturned advance even if its response is left uncollected or its explanation unanswered. Actual return transit defers the audit until the response arrives. A valid later claim can still discharge recognized costs against the audited liability.

**Case and archive → Recover filed copies** restores missing documents, including archive copies, without repeating their quest or monetary effects. Reprints may coexist with originals dropped elsewhere; all EA papers have zero resale value.

Do not remove these plugins from a save you intend to keep. There is no supported upgrade or uninstall migration yet, including from any earlier build to 0.3.0. Core and controller state changed again in this revision. Use a fresh test save for this revision. To discard a test, disable the package and use a save from before installation, or start a new game.

## Not yet implemented

Hand-placed world objects for the start, the Elenwen dialogue corpus and style pass (revised plan, Phase B), the observation, dead-drop and world-placed recovery cases that need hand-placed objects, random selection among eligible packets, compromised-cover reply variants, the Elenwen dialogue corpus (Revision Phase C), repeatable service backlog, curated NPC relationship locks and behavioral hooks, courier integrations, Mantella integration, and all main-quest / Dawnguard / Dark Brotherhood / Civil War / Serana routes remain unfinished. `EA_Prototype.esp` is a development entry point, not `EA_Start.esp`.

No compatibility patch or empty placeholder ESP has been manufactured. The specification requires inspecting installed records first. See [implementation status and conflict work](docs/IMPLEMENTATION_STATUS.md) and [manual game validation](docs/TESTING.md).

## Build from source

Required: Python 3.12+, .NET SDK 10, 7-Zip, and [Caprica v0.3.0](https://github.com/Orvid/Caprica/releases/tag/v0.3.0). This version supports the Skyrim compilation target. [Mutagen](https://github.com/Mutagen-Modding/Mutagen) writes and reads the ESP records; its NuGet version and transitive dependencies are locked in the project.

On Windows, from the repository root:

```powershell
python tools/fetch_compiler.py
python tools/build.py --caprica .tools/caprica/Caprica.exe --restore
```

On Linux with Wine installed:

```bash
python3 tools/fetch_compiler.py
python3 tools/build.py --caprica .tools/caprica/Caprica.exe \
  --wine /usr/lib/wine/wine64 --wine-prefix "$PWD/.tools/wine" --restore
```

Network access is needed for the initial compiler and NuGet downloads. Wine needs local IPC support. `tools/fetch_compiler.py` checks the upstream archive and extracted executable against pinned SHA-256 values; the build independently verifies the supplied executable. Do not change those hashes merely to bypass a failed check. Build/version pins are in `content/build-config.json`.

By default, compilation uses the small **project-authored API declaration files** in `tools/papyrus-api`. They are build inputs only and are never shipped as PEX files. For authoritative engine API validation, extract the Creation Kit's Skyrim SE source archive and supply its source directory:

```powershell
python tools/build.py --caprica .tools/caprica/Caprica.exe --restore --papyrus-import "D:\Skyrim Special Edition\Data\Source\Scripts"
```

This switches to the supplied base scripts instead of the declarations. A successful build compiles Papyrus with warnings treated as errors, round-trips all ESPs through Mutagen, runs independent plugin inspections and compiled-assembly logic tests, and produces the ZIP plus a SHA-256 manifest in `dist/`. The ZIP is verified before it replaces an existing package. The Windows CI workflow repeats that build; it has not yet been observed running on GitHub. See [the review report](docs/REVIEW.md) for fixes and remaining validation limits.

The test interpreter executes Caprica's emitted assembly with simulated game natives. It does **not** establish Skyrim save compatibility, VM scheduling, physical placement, mesh appearance, or UI correctness. Those checks still require the game and Creation Kit.

Source layout: `Data/Source/Scripts` holds Papyrus; `content/packets.json` holds the authored instructions, their papers, named places, items and leads; `content/documents.json` holds the other papers; `tools/PluginBuilder` builds plugin records; `tests` verifies the compiled logic and binaries. See [architecture and API](docs/ARCHITECTURE.md) for state conventions and limitations.
