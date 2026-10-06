"""Phase A opening (revised plan section 11): Northwatch handoff, packet, Establish Cover, assessment, case."""
import json
import pickle
import unittest
from pathlib import Path

from papyrus_vm import Alias, Inventory, Menu, fixture

ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY = ROOT / "build/Data/Scripts"
START = json.loads((ROOT / "content/start.json").read_text())
GUILDS = ["Companions", "College", "Thieves", "Bards"]
# Statistics that satisfy each occupation, in the opening's menu order.
EVIDENCE = [None, {"Weapons Made": 3}, {"Animals Killed": 5}, {"Quests Completed": 1}, {"Skill Books Read": 2}]


class StartTests(unittest.TestCase):
    def setUp(self):
        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY, collect_orders=False)
        # The opening commissions the service itself; the fixture's prototype commission is undone.
        self.core.vars["serviceactive"] = False
        self.player = self.vm.player
        self.arrival = Inventory()
        o = self.opening = self.vm.instance("EA_Opening").prop("Core", self.core).prop("Dispatch", self.dispatch)
        o.aliases[1] = Alias(self.arrival)
        o.prop("NorthwatchFaction", "Northwatch").prop("GuildFactions", GUILDS)
        for name in ("SealedPacket", "ArrivalLetter", "CivilianPapers", "DispatchInstructions", "ReportForm", "FieldPapers", "DispatchCase", "Gold", "Dagger"):
            o.prop(name, name)
        o.prop("Reports", [f"Report{i}" for i in range(5)]).prop("Responses", [f"Response{i}" for i in range(5)])
        for name in ("OccupationMenu", "LodgingMenu", "AttestationMenu", "FiledMessage", "ClosedMessage", "IncomeMessage"):
            o.prop(name, Menu())
        o.prop("EvidenceMessages", [Menu() for _ in range(5)]).prop("LodgingMessages", [Menu() for _ in range(3)])

    def menu(self, name):
        return self.opening.vars["::" + name.lower() + "_var"]

    def arrive_and_open(self):
        self.opening.call("Fragment_10")
        self.opening.call("OpenPacket")

    def earn(self, occupation=1, lodging=0):
        for stat, value in (EVIDENCE[occupation] or {}).items():
            self.vm.stats[stat] += value
        if occupation == 0:
            self.player.factions.add("Companions")
        if lodging == 0:
            self.vm.stats["Hours Slept"] += 8
        elif lodging == 1:
            self.vm.stats["Houses Owned"] += 1
        self.vm.stats["Most Gold Carried"] += 250

    def file(self, occupation=1, lodging=0, attest=0):
        for name in ("OccupationMenu", "LodgingMenu", "AttestationMenu"):
            self.menu(name).choices.clear()
        self.menu("OccupationMenu").choices.append(occupation)
        self.menu("LodgingMenu").choices.append(lodging)
        self.menu("AttestationMenu").choices.append(attest)
        return self.opening.call("FileCoverReport")

    def controller(self):
        p = self.vm.instance("EA_Prototype")
        for key, value in {"Core": self.core, "Dispatch": self.dispatch, "Service": self.service, "Accounts": self.accounts}.items():
            p.prop(key, value)
        for key in ("Gold", "Commission", "FieldPapers", "ArchiveBase", "BoxBase", "CaseItem"):
            p.prop(key, key)
        for key in ("CommissionMenu", "MainMenu", "AssignmentMenu", "AccountsMenu", "ClaimMenu", "ExplanationMenu", "FiledMessage", "UnavailableMessage", "CollectedMessage", "RepaymentMenu", "ReturnedMessage", "ReviewPendingMessage", "OpeningMenu", "CaseMenu"):
            p.prop(key, Menu())
        return p

    def test_handoff_places_the_player_at_northwatch_with_a_temporary_courtesy(self):
        self.opening.call("Fragment_10")
        self.assertIs(self.player.at, self.arrival)
        self.assertIn("Northwatch", self.player.factions)
        self.assertEqual(self.player.items["SealedPacket"], 1)
        self.assertEqual(self.player.items["Dagger"], 1)
        self.assertTrue(self.opening.objectives[("setobjectivedisplayed", 10)])
        self.opening.call("Fragment_10")
        self.assertEqual(self.player.items["SealedPacket"], 1, "the start-up stage issues once")
        self.opening.call("OnUpdate")
        self.assertIn("Northwatch", self.player.factions, "still at the keep")
        self.player.at = None
        self.opening.update = None
        self.opening.call("OnUpdate")
        self.assertNotIn("Northwatch", self.player.factions)
        self.assertIsNone(self.opening.update, "no further polling once the player has left")
        self.player.at = self.arrival
        self.opening.call("OnUpdate")
        self.assertNotIn("Northwatch", self.player.factions, "a later return finds Northwatch as vanilla left it")

    def test_packet_resumes_service_and_issues_its_contents_once(self):
        self.opening.call("OpenPacket")
        self.assertFalse(self.core.call("IsInService"), "no packet before the handoff")
        self.arrive_and_open()
        self.opening.call("OpenPacket")
        self.assertTrue(self.core.call("IsInService"))
        self.assertIs(self.core.call("GetOpening"), self.opening)
        self.assertFalse(self.core.call("HasEstablishedCover"))
        for item in ("ArrivalLetter", "CivilianPapers", "DispatchInstructions", "ReportForm", "DispatchCase"):
            self.assertEqual(self.player.items[item], 1, item)
        self.assertEqual(self.player.items["Gold"], 100)
        self.assertEqual(self.player.items["FieldPapers"], 0, "procedure papers follow acceptance")
        self.assertEqual(self.core.call("GetAssignmentState", 900), 1)
        self.assertEqual(self.opening.stages, [20])
        for objective in (20, 21, 22, 23):
            self.assertTrue(self.opening.objectives[("setobjectivedisplayed", objective)])

    def test_every_occupation_needs_evidence_gathered_after_arrival(self):
        for occupation in range(5):
            with self.subTest(occupation=occupation):
                self.setUp()
                # Evidence from before the packet was opened does not count.
                for stat, value in (EVIDENCE[occupation] or {}).items():
                    self.vm.stats[stat] += value * 10
                self.arrive_and_open()
                self.vm.stats["Hours Slept"] += 8
                self.vm.stats["Most Gold Carried"] += 250
                self.assertFalse(self.file(occupation))
                self.assertEqual(len(self.menu("EvidenceMessages")[occupation].shown), 1)
                self.assertEqual(self.dispatch.vars["count"], 0)
                self.earn(occupation)
                self.assertTrue(self.file(occupation))
                self.assertEqual(self.dispatch.vars["::archive_var"].items[f"Report{occupation}"], 1)

    def test_lodgings_income_and_attestation_are_each_required(self):
        self.arrive_and_open()
        self.vm.stats["Weapons Made"] += 3
        for lodging in range(3):
            with self.subTest(lodging=lodging):
                self.assertFalse(self.file(1, lodging))
                self.assertEqual(len(self.menu("LodgingMessages")[lodging].shown), 1)
        self.vm.stats["Hours Slept"] += 8
        self.assertFalse(self.file(1, 0))
        self.assertEqual(len(self.menu("IncomeMessage").shown), 1)
        self.vm.stats["Most Gold Carried"] += 250
        self.assertFalse(self.file(1, 0, attest=1))
        self.assertEqual(self.dispatch.vars["count"], 0)
        self.assertEqual(self.core.call("GetAssignmentState", 900), 1)

    def test_guild_quarters_require_a_guild_that_houses_its_members(self):
        self.arrive_and_open()
        self.vm.stats["Most Gold Carried"] += 250
        self.player.factions.add("Bards")
        self.assertFalse(self.file(0, 2))
        self.assertEqual(len(self.menu("LodgingMessages")[2].shown), 1)
        self.player.factions.add("College")
        self.assertTrue(self.file(0, 2))

    def test_cancelled_menus_file_nothing(self):
        self.arrive_and_open()
        self.earn()
        for occupation, lodging in ((5, 0), (1, 3)):
            self.assertFalse(self.file(occupation, lodging))
        self.assertEqual(self.dispatch.vars["count"], 0)
        self.assertTrue(all(not m.shown for m in self.menu("EvidenceMessages") + self.menu("LodgingMessages")))

    def test_accepted_report_establishes_cover_once_after_a_full_day(self):
        self.arrive_and_open()
        self.dispatch.prop("Archive", Inventory())
        self.earn(3)
        self.assertTrue(self.file(3))
        self.assertEqual(self.opening.stages, [20, 30])
        self.assertEqual(len(self.menu("FiledMessage").shown), 1)
        self.assertFalse(self.file(3))
        self.assertEqual(len(self.menu("ClosedMessage").shown), 1)
        self.assertEqual(self.dispatch.call("CollectResponses"), 0)
        self.assertFalse(self.core.call("HasEstablishedCover"))
        self.vm.day += 1
        self.assertEqual(self.dispatch.call("CollectResponses"), 1)
        self.assertTrue(self.core.call("HasEstablishedCover"))
        self.assertEqual(self.player.items["Response3"], 1)
        self.assertEqual(self.player.items["FieldPapers"], 1)
        self.assertEqual(self.core.call("GetAssignmentState", 900), 4)
        self.assertEqual(self.opening.stages, [20, 30, 40])
        tx = self.opening.vars["reporttransaction"]
        self.opening.call("ReceiveResponse", tx, 900, 1)
        self.assertEqual(self.player.items["FieldPapers"], 1)
        self.assertEqual(self.opening.stages, [20, 30, 40])

    def test_controller_offers_only_the_report_until_cover_is_accepted_then_service_begins(self):
        self.arrive_and_open()
        p = self.controller()
        p.vars["::openingmenu_var"].choices.append(0)
        self.earn()
        self.menu("OccupationMenu").choices.append(1)
        self.menu("LodgingMenu").choices.append(0)
        self.menu("AttestationMenu").choices.append(0)
        p.call("UseBox", Inventory())
        self.assertEqual(p.vars["::mainmenu_var"].shown, [])
        self.assertEqual(p.vars["::commissionmenu_var"].shown, [])
        self.assertEqual(self.player.items["Commission"], 0, "the console path's supplies are not issued")
        self.assertEqual(self.player.items["Gold"], 100)
        self.assertEqual(self.core.call("GetAssignmentState", 900), 3)
        self.vm.day += 1
        p.vars["::openingmenu_var"].choices.append(1)
        p.call("UseBox", Inventory())
        self.assertTrue(self.core.call("HasEstablishedCover"))
        p.vars["::mainmenu_var"].choices.append(0)
        p.call("UseBox", Inventory())
        self.assertEqual(len(p.vars["::mainmenu_var"].shown), 1)
        self.assertEqual(self.core.call("GetAssignmentState", 1001), 1)
        papers = self.vm.instance("EA_FieldPapers").prop("Core", self.core)
        papers.call("OnRead")
        self.assertTrue(self.service.call("FileReport", 0), "the first instruction can be completed")

    def test_console_path_without_the_opening_still_presumes_cover(self):
        p = self.controller()
        p.call("UseBox", Inventory())
        self.assertTrue(self.core.call("HasEstablishedCover"))
        self.assertEqual(self.player.items["Commission"], 1)
        self.assertEqual(len(p.vars["::mainmenu_var"].shown), 1)
        self.assertEqual(p.vars["::openingmenu_var"].shown, [])

    def test_case_unpacks_where_it_is_set_down_and_packs_with_its_archive(self):
        self.arrive_and_open()
        p = self.controller()
        archive = Inventory()
        self.dispatch.prop("Archive", archive)
        case = self.vm.instance("EA_DispatchCase").prop("Controller", p)
        dropped = Inventory()
        case_ref = dropped
        # The case script runs on the dropped reference; the test calls the controller as it would.
        case.call("OnContainerChanged", Inventory(), self.player)
        self.assertEqual(self.vm.activations, [])
        p.call("Unpack", case_ref)
        self.assertTrue(dropped.deleted)
        self.assertFalse(dropped.enabled)
        box = archive.at
        self.assertEqual(box.base, "BoxBase")
        self.assertTrue(archive.enabled)
        p.vars["::casemenu_var"].choices.extend([0, 2])
        p.call("UseCase", box)
        self.assertEqual(self.vm.activations, [(archive, self.player)])
        self.player.items["DispatchCase"] = 0
        p.call("UseCase", box)
        self.assertTrue(box.deleted)
        self.assertFalse(archive.enabled)
        self.assertEqual(self.player.items["CaseItem"], 1)

    def test_dropping_the_case_from_inventory_unpacks_it(self):
        p = self.controller()
        p.running = True
        self.dispatch.prop("Archive", Inventory())
        case = self.vm.instance("EA_DispatchCase").prop("Controller", p)
        # A dropped item's script runs on its new world reference; the double stands in for it.
        case.call("OnContainerChanged", None, self.player)
        self.assertEqual(self.dispatch.vars["::archive_var"].at.base, "BoxBase")
        self.assertTrue(case.ref.deleted)
        before = self.dispatch.vars["::archive_var"].at
        case.call("OnContainerChanged", Inventory(), self.player)
        self.assertIs(self.dispatch.vars["::archive_var"].at, before, "stored in a container, the case stays packed")

    def test_opening_state_survives_interpreter_serialization(self):
        self.arrive_and_open()
        self.dispatch.prop("Archive", Inventory())
        self.earn(4)
        self.assertTrue(self.file(4))
        self.vm, self.core, self.dispatch, self.opening = pickle.loads(pickle.dumps((self.vm, self.core, self.dispatch, self.opening)))
        self.vm.day += 1
        self.assertEqual(self.dispatch.call("CollectResponses"), 1)
        self.assertTrue(self.core.call("HasEstablishedCover"))


class StartContentTests(unittest.TestCase):
    def test_registration_names_the_start_quest(self):
        entry, = START["alternatePerspective"]
        self.assertEqual(entry["mod"], "EA_Start.esp")
        self.assertEqual(int(entry["id"], 16), int(START["quest"]["id"], 16))
        self.assertLessEqual(entry["description"].count("."), 2, "AP asks for one or two sentences")
        built = json.loads((ROOT / "build/Data/SKSE/AlternatePerspective/ElenwenAgent.json").read_text())
        self.assertEqual(built, START["alternatePerspective"])

    def test_journal_recap_covers_the_plan(self):
        recap = START["quest"]["stages"][0]["log"]
        for fact in ("Dominion authority", "Northwatch", "sealed instructions", "belongings", "Elenwen", "released",
                     "effects were returned", "not ordered to report to the Embassy", "civilian papers", "sealed packet",
                     "not told what I am"):
            self.assertIn(fact, recap)
        self.assertTrue(START["quest"]["stages"][0]["startUp"])
        self.assertTrue(START["quest"]["stages"][-1]["complete"])

    def test_opening_letter_is_an_assignment_from_someone_who_knows_him(self):
        letter = next(d for d in START["documents"] if d["editorID"] == "EA_ArrivalLetter")["text"]
        self.assertIn("Do not come to the Embassy", letter)
        self.assertIn("This is an assignment, not leave.", letter)
        self.assertTrue(letter.endswith("\n\nElenwen"))
        for recruiting in ("welcome", "join", "recruit", "offer", "!"):
            self.assertNotIn(recruiting, letter.lower())

    def test_one_report_and_one_assessment_per_occupation(self):
        reports = [d for d in START["documents"] if d["editorID"].startswith("EA_EstablishmentReport")]
        replies = [d for d in START["documents"] if d["editorID"].startswith("EA_EstablishmentResponse")]
        menu = next(m for m in START["messages"] if m["editorID"] == "EA_OccupationMenu")
        self.assertEqual(len(reports), 5)
        self.assertEqual(len(replies), 5)
        self.assertEqual(len(menu["buttons"]), 6)
        for reply in replies:
            self.assertTrue(reply["text"].endswith("\n\nElenwen"))
            self.assertLessEqual(len(reply["text"]), 300)


if __name__ == "__main__":
    unittest.main()
