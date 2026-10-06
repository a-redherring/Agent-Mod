"""The Alternate Perspective start: Northwatch handoff, sealed packet, the campaign begins, the dispatch case."""
import json
import pickle
import unittest
from pathlib import Path

from papyrus_vm import CAMPAIGN, Alias, Inventory, Menu, fixture

ROOT = Path(__file__).resolve().parents[1]
ASSEMBLY = ROOT / "build/Data/Scripts"
START = json.loads((ROOT / "content/start.json").read_text())
PAPERS = ["ArrivalLetter", "CivilianPapers", "ConditionalRelease", "DispatchInstructions"]
BOOKS = ["Book" + b for b in CAMPAIGN["packetBooks"]]


class StartTests(unittest.TestCase):
    def setUp(self):
        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY)
        # The opening commissions the service itself; the fixture's prototype commission is undone.
        self.core.vars["serviceactive"] = False
        self.player = self.vm.player
        self.arrival = Inventory()
        o = self.opening = self.vm.instance("EA_Opening").prop("Core", self.core).prop("Dispatch", self.dispatch).prop("Service", self.service)
        o.aliases[1] = Alias(self.arrival)
        o.prop("NorthwatchFaction", "Northwatch").prop("PacketPapers", PAPERS).prop("PacketBooks", BOOKS)
        for name in ("SealedPacket", "DispatchCase", "Gold", "Dagger"):
            o.prop(name, name)
        o.prop("Allowance", 100)

    def arrive_and_open(self):
        self.opening.call("Fragment_10")
        self.opening.call("OpenPacket")

    def controller(self):
        p = self.vm.instance("EA_Prototype")
        for key, value in {"Core": self.core, "Dispatch": self.dispatch, "Service": self.service, "Accounts": self.accounts}.items():
            p.prop(key, value)
        for key in ("Gold", "Commission", "ArchiveBase", "BoxBase", "CaseItem"):
            p.prop(key, key)
        for key in ("CommissionMenu", "MainMenu", "AssignmentMenu", "AccountsMenu", "ClaimMenu", "ExplanationMenu", "FiledMessage", "UnavailableMessage", "CollectedMessage", "RepaymentMenu", "ReturnedMessage", "CaseMenu"):
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

    def test_packet_resumes_service_and_begins_the_campaign_once(self):
        self.opening.call("OpenPacket")
        self.assertFalse(self.core.call("IsInService"), "no packet before the handoff")
        self.arrive_and_open()
        self.opening.call("OpenPacket")
        self.assertTrue(self.core.call("IsInService"))
        self.assertTrue(self.core.call("HasEstablishedCover"), "civilian papers are his cover")
        for item in PAPERS + BOOKS + ["DispatchCase"]:
            self.assertEqual(self.player.items[item], 1, item)
        self.assertEqual(self.player.items["Gold"], 100)
        self.assertEqual(self.player.items["Commission"], 0, "the console path's supplies are not issued")
        self.assertEqual(self.service.call("GetPhase"), 1)
        self.assertEqual(self.core.call("GetAssignmentState", 2001), 1, "the first Riverwood instruction is open")
        self.assertEqual(self.opening.stages, [20])
        self.assertTrue(self.opening.objectives[("setobjectivecompleted", 10)])

    def test_campaign_waits_for_the_packet(self):
        self.opening.call("Fragment_10")
        self.service.call("BeginCampaign")
        self.assertEqual(self.service.call("GetPhase"), 0, "not commissioned until the packet is opened")
        self.assertEqual(self.core.call("GetAssignmentState", 2001), 0)

    def test_controller_after_the_packet_goes_straight_to_the_case(self):
        self.arrive_and_open()
        p = self.controller()
        p.vars["::mainmenu_var"].choices.append(5)
        p.call("UseBox", Inventory())
        self.assertEqual(p.vars["::commissionmenu_var"].shown, [])
        self.assertEqual(len(p.vars["::mainmenu_var"].shown), 1)
        self.assertEqual(self.player.items["Commission"], 0)
        self.assertEqual(self.player.items["Gold"], 100)
        self.assertEqual(self.service.call("GetPhase"), 1)

    def test_console_path_without_the_opening_commissions_and_begins(self):
        p = self.controller()
        p.call("UseBox", Inventory())
        self.assertEqual(len(p.vars["::commissionmenu_var"].shown), 1)
        self.assertTrue(self.core.call("HasEstablishedCover"))
        self.assertEqual(self.player.items["Commission"], 1)
        self.assertEqual(self.player.items["Gold"], 100)
        self.assertEqual(len(p.vars["::mainmenu_var"].shown), 1)
        self.assertEqual(self.service.call("GetPhase"), 1)
        self.assertEqual(self.dispatch.vars["::archive_var"].items["Commission"], 0, "the fixture's archive was already set")

    def test_declined_commission_does_nothing(self):
        p = self.controller()
        p.vars["::commissionmenu_var"].choices.append(1)
        p.call("UseBox", Inventory())
        self.assertFalse(self.core.call("IsInService"))
        self.assertEqual(self.player.items["Gold"], 0)
        self.assertEqual(p.vars["::mainmenu_var"].shown, [])
        self.assertEqual(self.service.call("GetPhase"), 0)

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
        self.vm, self.core, self.service, self.opening = pickle.loads(pickle.dumps((self.vm, self.core, self.service, self.opening)))
        self.opening.call("OpenPacket")
        self.assertEqual(self.vm.player.items["Gold"], 100, "the packet stays opened")
        self.assertEqual(self.service.call("GetPhase"), 1)


class StartContentTests(unittest.TestCase):
    def test_registration_names_the_start_quest(self):
        entry, = START["alternatePerspective"]
        self.assertEqual(entry["mod"], "EA_Start.esp")
        self.assertEqual(int(entry["id"], 16), int(START["quest"]["id"], 16))
        self.assertLessEqual(entry["description"].count("."), 2, "AP asks for one or two sentences")
        built = json.loads((ROOT / "build/Data/SKSE/AlternatePerspective/ElenwenAgent.json").read_text())
        self.assertEqual(built, START["alternatePerspective"])

    def test_journal_recap_covers_the_premise(self):
        recap = START["quest"]["stages"][0]["log"]
        for fact in ("Imperial territory", "Dominion authority", "Northwatch", "Elenwen questioned me herself",
                     "conditional, and revocable", "belongings were returned", "civilian papers", "sealed packet",
                     "not ordered to report to the Embassy", "not told what I am"):
            self.assertIn(fact, recap)
        self.assertTrue(START["quest"]["stages"][0]["startUp"])
        self.assertTrue(START["quest"]["stages"][-1]["complete"])
        self.assertIn("Riverwood", START["quest"]["stages"][-1]["log"])

    def test_residence_order_follows_tradecraft(self):
        letter = next(d for d in START["documents"] if d["editorID"] == "EA_ArrivalLetter")["text"]
        self.assertTrue(letter.startswith("C.,\n\n"))
        self.assertTrue(letter.endswith("\n\n\u2014 E."))
        for clear in ("Elenwen", "Embassy", "Thalmor", "Northwatch", "Cotta", "Delphine"):
            self.assertNotIn(clear, letter)
        for fact in ("Riverwood", "Sleeping Giant", "Whiterun and Falkreath", "Two books"):
            self.assertIn(fact, letter)
        self.assertEqual(len(CAMPAIGN["packetBooks"]), 2, "the letter says two books accompany it")
        for recruiting in ("welcome", "recruit", "!"):
            self.assertNotIn(recruiting, letter.lower())

    def test_only_the_release_is_signed_formally(self):
        release = next(d for d in START["documents"] if d["editorID"] == "EA_ConditionalRelease")["text"]
        self.assertTrue(release.endswith("By my hand and seal,\n\nElenwen\nFirst Emissary"), release[-60:])
        for doc in START["documents"]:
            if doc["editorID"] != "EA_ConditionalRelease":
                self.assertNotIn("By my hand and seal", doc["text"])


if __name__ == "__main__":
    unittest.main()
