# Elenwen Agent — Skyrim SE/AE technical prototype

**Version 0.4.0-prototype. This is an installable development build, not the completed mod described in [the specification](Elenwen_Agent_Mod_Build_Specification.md), its [Continuation 01](Elenwen_Agent_Mod_Build_Specification_Continuation_01.md) and the [Revised Implementation Plan](Elenwen_Agent_Revised_Implementation_Plan.md). The story it follows is set out in [the campaign opening](Elenwen_Agent_Campaign_Opening.md). It has been compiled and tested outside Skyrim; it has not been run in the game.**

The repository began with the design specification only. This implementation builds its first paper-based service loop using real ESP records and compiled Papyrus scripts. No Skyrim installation, Creation Kit, Alternate Perspective plugin, Sinister Serana plugin, or installed load order was available for record inspection or playtesting.

## Included

- **An Alternate Perspective start, "Elenwen's Agent".** Cotta was taken from Imperial territory and held at Northwatch Keep. Elenwen questioned him herself and then released him, conditionally. He begins outside the keep. The journal tells the rest; there is no custom scene. Northwatch's garrison leaves him alone until he leaves the keep, and its own quest is unaffected.
- **Her sealed packet** holds:
  - her residence order;
  - civilian papers and the conditional release;
  - the dispatch-case instructions;
  - two books to read, *The Madmen of the Reach* and *The Bear of Markarth*;
  - a 100-septim allowance;
  - the dispatch case itself.

  Opening the packet commissions the service and begins the campaign.
- **A campaign in four phases**, carried by 21 instructions (2001–2021) and 8 letters. Each instruction stays open until it is reported, with no deadline. A report is accepted only when the game's own records support it. Otherwise it is refused with a reason, and nothing is filed. Every instruction rests on vanilla content.
  1. **Riverwood.** He is told to live at the Sleeping Giant Inn and to freelance for his living. His recon jobs are:
     - the inn's guests and its proprietor;
     - which neighbours pray to Talos;
     - the street preacher in Whiterun;
     - soldiers on the roads;
     - the dead agent on the hillside. Sanyon's orders count whenever they are found.

     Nights slept at the inn, days in residence and places visited are counted. Leaving Whiterun and Falkreath holds delays his release and costs trust. There is no recall.
  2. **Markarth.** Once his residence has served its purpose, the release letter sends him to hire Jenassa (Accounts advances her fee) and to keep the Reach burning:
     - *The Forsworn Conspiracy* and Madanach's fate;
     - the Namira coven;
     - Ogmund's amulet for Ondolemar;
     - the Talos shrine, reported only to her;
     - Calcelmo.
  3. **An interval** with no assignments, while he brushes up his magic.
  4. **The College of Winterhold.** He reports at each College beat, steals an Arcanaeum book, and investigates Winterhold. A letter gives him authority to remove the adviser, and he declines the Arch-Mage's chair. Some conditions use *At Your Own Pace - College of Winterhold* and *College of Winterhold - Quest Expansion*. Both are optional and are looked up at run time, never as masters.
- **Her letters follow a tradecraft.** They are addressed to "C." and signed "— E."; they name no institutions, and they refer to targets by description ("the proprietor", "the old man in the mine"). Some arrive with vanilla books to read. She writes rarely; she is a busy mer.
- **A portable dispatch case.** Set down outside the inventory, it opens into the dispatch box; it can be packed up again. Filed correspondence travels with it.
- **Accounts** advances Jenassa's fee and settles one declared claim, with its four outcomes, explanations, the return of funds, a 14-day audit and liability.
- Replay protection for commissioning, reports, letters, advances and claim payments, and recovery of lost paper copies.

All public text is SFW. Hidden trust and creditworthiness are not displayed. Every plugin masters only `Skyrim.esm` and other EA plugins, and none overrides a vanilla record. The start option appears only with Alternate Perspective, which itself needs SKSE and JContainers; the EA scripts use no SKSE functions. These ESPs are intentionally **not ESL-flagged**.

**The vanilla FormIDs the campaign uses come from published references and have not been checked against `Skyrim.esm`.** These are its quests, actors, factions, books, items and locations. See [manual game validation](docs/TESTING.md).

## Install and try it

1. Use a separate Skyrim Special Edition / Anniversary Edition **test profile and fresh save**. LE and VR are not supported targets. SE/AE runtime compatibility has not been playtested.
2. Install `dist/ElenwenAgent-0.4.0-prototype.zip` through MO2 or Vortex. The ZIP root is the Data directory.
3. Install [Alternate Perspective](https://www.nexusmods.com/skyrimspecialedition/mods/50307) 4.x with its requirements (SKSE and JContainers). The package's `SKSE/AlternatePerspective/ElenwenAgent.json` registers the start; `EA_Start.esp` does not list Alternate Perspective as a master. Enable this order after the game's official masters and Alternate Perspective:

   ```text
   EA_Core.esp
   EA_Dispatch.esp
   EA_Service.esp
   EA_Accounts.esp
   EA_Prototype.esp
   EA_Start.esp
   ```

4. Start a new game and choose **Elenwen's Agent** at Alternate Perspective's start menu. Read the journal, then read the **Sealed Packet** in your inventory.
5. Go to Riverwood and take a room at the Sleeping Giant. Drop the **Sealed Dispatch Case** there; after a moment it becomes the dispatch box. Its menu has:
   - **File Report**, which lists up to eight open instructions, ready ones first;
   - **Check Correspondence**, where replies arrive a full day after filing;
   - **Accounts**;
   - **Review status**;
   - **Case and archive**, to open filed correspondence or pack the case up.
6. Live there, freelance and sleep at the inn. The instructions are open from the start and are reported when their conditions are met. The release letter follows after about two weeks of residence, some earnings and some experience.

*Without Alternate Perspective* (prototype testing):
1. Open the console in a safe interior and run `help "EA_SecureDispatch" 4`.
2. Run `player.placeatme <the ACTI FormID returned> 1`. The local ID is `000800` in `EA_Prototype.esp`.
3. Open the commission there. This skips the start and begins the campaign.

Do not remove these plugins from a save you intend to keep. There is no supported upgrade or uninstall migration, including from any earlier build to 0.4.0. Use a fresh test save for this revision.

## Not yet implemented

Hand-placed world objects, the vanilla courier (letters arrive in the dispatch case instead), compromised-cover reply variants, the Elenwen dialogue corpus (Revision Phase C), anything after the College, curated NPC relationship locks and behavioral hooks, courier integrations, Mantella integration, and all main-quest / Dawnguard / Dark Brotherhood / Civil War / Serana routes remain unfinished. `EA_Prototype.esp` is a development entry point, not `EA_Start.esp`.

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

Source layout: `Data/Source/Scripts` holds Papyrus; `content/campaign.json` holds the instructions, letters and their conditions; `content/documents.json` holds the other papers; `tools/PluginBuilder` builds plugin records; `tests` verifies the compiled logic and binaries. See [architecture and API](docs/ARCHITECTURE.md) for state conventions and limitations.
