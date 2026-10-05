# Elenwen Agent — Skyrim SE/AE technical prototype

**Version 0.1.2-prototype. This is an installable development build, not the completed mod described in [the specification](Elenwen_Agent_Mod_Build_Specification.md). It has been compiled and tested outside Skyrim; it has not been run in the game.**

The repository began with the design specification only. This implementation builds its first paper-based service loop using real ESP records and compiled Papyrus scripts. No Skyrim installation, Creation Kit, Alternate Perspective plugin, Sinister Serana plugin, or installed load order was available for record inspection or playtesting.

## Included

- A physical secure dispatch activator and a persistent, non-respawning document archive.
- A confidential commission, private field papers, and a one-time 100-septim allowance.
- Six finite instructions in two packets. The first covers field protocol, three Alto wines, and six blue mountain flowers. The second adds six firewood, four leather strips, and six wheat. Supplies are actually removed from inventory when filed.
- Seventy readable orders, reports, requests, decisions, assessments, and receipts. Extensions identify their assignment; meal explanations preserve the chosen declaration. Responses take one game day and must be collected physically.
- Ten-day deadlines, overdue state with one trust consequence, and a five-day extension followed by refusal of a second extension.
- Core authorization scoped to operation and decision category, including emergency review functions for later modules.
- A single wine-procurement accounts case: authorized 80-septim advance, declared claims, all four outcomes, explanations, return of funds, a 14-day audit, and liability/probation. Recognized costs settle the advance before any reimbursement.
- A dispatch status register with active/overdue/filed/completed counts, ready/in-transit replies, and per-instruction remaining days. Specific feedback explains missing supplies, permissions, pending requests, and settled claims.
- Elenwen replies differently to prompt, ordinary, and previously overdue work; Accounts letters address the chosen expense. A delayed closing assessment follows both packets and any pending claim decision.
- Partial repayments of up to 10 or 25 septims, or all affordable outstanding funds, with confirmation of the actual payment and remaining balance.
- Replay protection for commissioning, orders, deliveries, responses, advances, and claim payments; recovery of lost paper copies.

All public text is SFW. Hidden trust and creditworthiness are not displayed. Core requires only `Skyrim.esm`; no SKSE or optional mod is needed for this prototype. No vanilla records are overridden. These ESPs are intentionally **not ESL-flagged**.

## Install and try it

1. Use a separate Skyrim Special Edition / Anniversary Edition **test profile and fresh save**. LE and VR are not supported targets. SE/AE runtime compatibility has not been playtested.
2. Install `dist/ElenwenAgent-0.1.2-prototype.zip` through MO2 or Vortex. The ZIP root is the Data directory. For manual installation, copy its ESPs and `Scripts` directory into the test installation's Data folder.
3. Enable this order after the game's official masters:

   ```text
   EA_Core.esp
   EA_Dispatch.esp
   EA_Service.esp
   EA_Accounts.esp
   EA_Prototype.esp
   ```

4. Stand in a convenient safe interior. Open the game console and run:

   ```text
   help "EA_SecureDispatch" 4
   player.placeatme <the ACTI FormID returned above> 1
   ```

   Replace the placeholder with the actual eight-digit FormID. The local ID is `000800` in `EA_Prototype.esp`; its load-order prefix varies. Place **one** box.

5. Activate it, open the commission, and choose **Collect Orders**. Read the field papers in your inventory; reading them before collecting orders also counts. A second strongbox beside the dispatch box contains archived correspondence. Delivered supplies are consigned immediately and cannot be taken back from this paper archive.
6. File the protocol acknowledgment. Obtain three bottles of standard Alto wine and six blue mountain flowers for the other reports. Return after 24 game hours and choose **Check Responses**.
7. To test Accounts, request supply authority **before filing the wine delivery**, wait a day, collect the authorization, then collect the advance under **Accounts**. After delivering wine, submit one of the declared claim forms. Each claim/explanation needs its own return dispatch.

8. After collecting all three first-packet acknowledgments, choose **Collect Orders** again to open the second packet. Its ten-day deadlines begin on collection. Deliver six firewood, four leather strips, and six wheat, then collect their responses.
9. Use **Review status** to inspect the register and individual instructions. Under **Accounts → Return outstanding funds**, choose a partial payment or all affordable outstanding funds.
10. After all six completion responses and any pending Accounts decision have been collected, a closing review is sent automatically. Wait another full game day and collect Elenwen's assessment. A returned meal claim must first be explained and settled. The assessment reflects the record when the review was sent; later actions do not rewrite it.

Supply cost forms are the player's **declarations**; this build does not track vendor transactions. Only one claim is allowed for instruction 1002. Use separate fresh test saves to exercise the four different outcomes. The six assignments do not regenerate. The second packet has no separate advance, claim, or completion reward; its orders explicitly authorize use of the initial allowance.

After fourteen days, Accounts audits an unreturned advance even if its response is left uncollected or its explanation unanswered. Actual return transit defers the audit until the response arrives. A valid later claim can still discharge recognized costs against the audited liability.

**Recover filed copies** restores missing documents, including archive copies, without repeating their quest or monetary effects. Reprints may coexist with originals dropped elsewhere; all EA papers have zero resale value.

Do not remove these plugins from a save you intend to keep. There is no supported upgrade or uninstall migration yet, including from 0.1.0 or 0.1.1 to 0.1.2. Runtime arrays changed in this revision. Use a fresh test save for this revision. To discard a test, disable the package and use a save from before installation, or start a new game.

## Not yet implemented

The bespoke Alternate Perspective start, actual civilian accommodation and Establish Cover assignment, repeatable service backlog, curated NPC relationship locks and behavioral hooks, courier integrations, Mantella integration, and all main-quest / Dawnguard / Dark Brotherhood / Civil War / Serana routes remain unfinished. `EA_Prototype.esp` is a development entry point, not `EA_Start.esp`.

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

Source layout: `Data/Source/Scripts` holds Papyrus; `content/documents.json` holds authored papers; `tools/PluginBuilder` builds plugin records; `tests` verifies the compiled logic and binaries. See [architecture and API](docs/ARCHITECTURE.md) for state conventions and limitations.
