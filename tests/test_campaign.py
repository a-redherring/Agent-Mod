"""The campaign, run on compiled Papyrus against content/campaign.json: Riverwood, Markarth, the College."""
import pickle
import unittest
from pathlib import Path

from papyrus_vm import CAMPAIGN, Global, Menu, Place, VanillaQuest, fixture

ASSEMBLY = Path(__file__).resolve().parents[1] / "build/Data/Scripts"
INDEX = {i["key"]: n for n, i in enumerate(CAMPAIGN["instructions"])}
LETTER = {l["key"]: n for n, l in enumerate(CAMPAIGN["letters"])}
CQE = "College Of Winterhold - Quest Expansion.esp"
AYOP = "At Your Own Pace - College of Winterhold.esp"


def form(key, kind):
    """The vanilla ID a condition of the given instruction or letter uses."""
    source = next((i for i in CAMPAIGN["instructions"] if i["key"] == key), None) or next(l for l in CAMPAIGN["letters"] if l["key"] == key)
    return next(c for c in source["conditions"] if c["kind"] == kind)


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY)
        self.world = self.vm.world
        self.player = self.vm.player
        self.inn = self.world.place(CAMPAIGN["places"]["inn"])
        self.whiterun_hold = self.world.place(CAMPAIGN["places"]["bounds"][0])
        self.inn.parent = self.whiterun_hold
        self.service.call("BeginCampaign")

    # Helpers

    def state(self, key):
        return self.core.call("GetAssignmentState", 2001 + INDEX[key])

    def file(self, key):
        return self.service.call("FileReport", INDEX[key])

    def collect(self, days=1):
        self.vm.day += days
        return self.dispatch.call("CollectResponses")

    def sleep_at_inn(self, nights=1):
        for _ in range(nights):
            self.player.location = self.inn
            self.service.call("OnWake")
            self.vm.day += 1

    def arrive(self, place):
        self.service.call("RecordVisit", place)

    def letter_sent(self, key):
        return self.service.vars["lettersent"][LETTER[key]]

    def release(self):
        """Live out the residence and collect the release letter."""
        self.sleep_at_inn(15)
        self.vm.stats["Most Gold Carried"] += 500
        self.player.level = 6
        self.service.call("OnWake")
        self.assertTrue(self.letter_sent("Release"))
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.service.call("GetPhase"), 2)

    def finish(self, key):
        self.assertTrue(self.file(key), key)
        self.collect()
        self.assertEqual(self.state(key), 4, key)

    def to_college(self):
        self.release()
        self.world.quest(form("Market", "questCompleted")["form"]).completed = True
        self.arrive(self.world.place(form("Market", "visited")["form"]))
        self.world.quest(form("OldMan", "questCompleted")["form"]).completed = True
        self.finish("Market")
        self.finish("OldMan")
        self.assertTrue(self.letter_sent("Interval"))
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.service.call("GetPhase"), 3)
        self.player.skills["Destruction"] = 25
        self.vm.day += 7
        self.service.call("Evaluate")
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.service.call("GetPhase"), 4)

    # Riverwood

    def test_campaign_begins_once_with_every_residence_order(self):
        for i in CAMPAIGN["instructions"]:
            expected = 1 if i["phase"] == 1 else 0
            self.assertEqual(self.player.items[i["order"]["editorID"]], expected, i["key"])
        self.service.call("BeginCampaign")
        self.assertEqual(self.player.items[CAMPAIGN["instructions"][0]["order"]["editorID"]], 1)
        self.assertEqual(self.service.call("GetPhase"), 1)

    def test_nights_count_only_at_the_inn(self):
        self.player.location = Place("Elsewhere")
        self.service.call("OnWake")
        self.assertEqual(self.service.vars["nights"], 0)
        self.assertEqual(self.service.vars["residencestart"], 0.0)
        self.player.location = Place("Upstairs", parent=self.inn)
        self.service.call("OnWake")
        self.assertEqual(self.service.vars["nights"], 1)
        self.assertGreater(self.service.vars["residencestart"], 0)

    def test_recon_is_refused_with_a_reason_until_its_condition_holds(self):
        self.sleep_at_inn(4)
        self.assertFalse(self.file("Inn"))
        self.service.call("ShowFailure")
        self.assertEqual(len(self.service.vars["::notyetmessages_var"][INDEX["Inn"]].shown), 1)
        self.assertEqual(self.dispatch.vars["count"], 1, "only the settled note is in the case")
        self.sleep_at_inn(1)
        self.assertTrue(self.file("Inn"))
        self.assertFalse(self.file("Inn"))
        self.collect()
        self.assertEqual(self.player.items[CAMPAIGN["instructions"][INDEX["Inn"]]["reply"]["editorID"]], 1)

    def test_recon_jobs_can_be_done_in_any_order(self):
        self.arrive(self.world.place(form("Preacher", "visited")["form"]))
        self.player.items[form("Hillside", "deliver")["form"]] += 1
        self.assertTrue(self.file("Hillside"))
        self.assertTrue(self.file("Preacher"))
        self.assertFalse(self.file("Neighbours"))
        self.collect()
        self.assertEqual(self.state("Hillside"), 4)
        self.assertEqual(self.state("Preacher"), 4)

    def test_sanyons_orders_count_whenever_found_and_are_delivered_once(self):
        orders = form("Hillside", "deliver")["form"]
        self.player.items[orders] = 1  # found on the walk from Northwatch, before Riverwood
        self.assertTrue(self.file("Hillside"))
        self.assertEqual(self.player.items[orders], 0)
        self.assertFalse(self.file("Hillside"))
        self.collect()
        self.assertEqual(self.player.items[CAMPAIGN["instructions"][INDEX["Hillside"]]["reply"]["editorID"]], 1)

    def test_settled_note_follows_three_nights(self):
        self.sleep_at_inn(2)
        self.assertFalse(self.letter_sent("Settled"))
        self.sleep_at_inn(1)
        self.assertTrue(self.letter_sent("Settled"))
        self.assertEqual(self.vm.notifications[-1], "Something has been left in the dispatch case.")

    def test_wandering_costs_trust_and_time_and_writes_at_most_every_three_days(self):
        self.sleep_at_inn(1)
        trust = self.core.vars["professionaltrust"]
        windhelm = Place("Windhelm")
        self.arrive(windhelm)
        self.arrive(Place("Windhelm market"))
        self.assertEqual(self.core.vars["professionaltrust"], trust - 1, "one absence, one penalty")
        self.assertEqual(self.service.vars["delaydays"], 3.0)
        self.assertEqual(self.player.items[CAMPAIGN["wander"]["editorID"]], 0)
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.player.items[CAMPAIGN["wander"]["editorID"]], 1)
        self.arrive(Place("Riverwood", parent=self.whiterun_hold))
        self.arrive(windhelm)
        self.assertEqual(self.service.vars["delaydays"], 6.0)
        self.assertEqual(self.dispatch.call("CollectResponses"), 0, "no second letter within three days")

    def test_travel_before_reaching_the_inn_is_free(self):
        self.arrive(Place("Solitude"))
        self.assertEqual(self.service.vars["delaydays"], 0.0)

    def test_release_needs_time_earnings_level_and_no_delphine(self):
        self.sleep_at_inn(15)
        self.service.call("OnWake")
        self.assertFalse(self.letter_sent("Release"), "no earnings or level yet")
        self.vm.stats["Most Gold Carried"] += 500
        self.player.level = 6
        mq106 = self.world.quest(form("Release", "questNotBegun")["form"])
        mq106.running = True
        self.service.call("OnWake")
        self.assertFalse(self.letter_sent("Release"), "Delphine has revealed herself; a later phase decides")
        mq106.running = False
        self.service.call("OnWake")
        self.assertTrue(self.letter_sent("Release"))

    def test_wandering_delays_release(self):
        self.sleep_at_inn(1)
        self.arrive(Place("Windhelm"))
        self.arrive(Place("Riverwood", parent=self.whiterun_hold))
        self.sleep_at_inn(14)
        self.vm.stats["Most Gold Carried"] += 500
        self.player.level = 6
        self.service.call("OnWake")
        self.assertFalse(self.letter_sent("Release"))
        self.sleep_at_inn(3)
        self.assertTrue(self.letter_sent("Release"))

    # Release, the Dunmer and Markarth

    def test_release_grants_the_advance_issues_markarth_and_encloses_a_book(self):
        self.release()
        self.assertEqual(self.core.call("GetAuthority", CAMPAIGN["operations"]["advance"], 5), 2)
        for book in CAMPAIGN["letters"][LETTER["Release"]]["enclosures"]:
            self.assertEqual(self.player.items[book], 1)
        for key in ("Dunmer", "Market", "OldMan", "Feast", "Skald", "Shrine", "Translator"):
            self.assertEqual(self.state(key), 1, key)
        self.assertTrue(self.letter_sent("Reach"))
        self.assertEqual(self.state("Inn"), 1, "unfiled recon stays open and can be reported later")

    def test_dunmer_is_hired_when_she_is_a_current_hireling(self):
        self.release()
        self.assertFalse(self.file("Dunmer"))
        jenassa = self.world.actor(form("Dunmer", "actorInFaction")["form"])
        jenassa.factions.add(form("Dunmer", "actorInFaction")["other"])
        self.finish("Dunmer")

    def test_madanach_freed_or_killed_selects_the_reply_trust_and_weight(self):
        for killed in (False, True):
            with self.subTest(killed=killed):
                self.setUp()
                self.release()
                self.world.quest(form("OldMan", "questCompleted")["form"]).completed = True
                madanach = self.world.actor(CAMPAIGN["instructions"][INDEX["OldMan"]]["alt"]["form"])
                madanach.dead = killed
                trust = self.core.vars["professionaltrust"]
                self.finish("OldMan")
                ins = CAMPAIGN["instructions"][INDEX["OldMan"]]
                self.assertEqual(self.player.items[ins["altReply"]["editorID"]], 1 if killed else 0)
                self.assertEqual(self.player.items[ins["reply"]["editorID"]], 0 if killed else 1)
                self.assertEqual(self.core.vars["professionaltrust"], trust + 1 + (ins["altTrust"] if killed else 0))
                if killed:
                    self.assertEqual(self.service.vars["phaseweight"], ins["altWeight"])
                    self.assertFalse(self.letter_sent("Interval"))
                else:
                    # Freeing him alone ends the operation; the interval letter arrives in the same collection.
                    self.assertTrue(self.letter_sent("Interval"))
                    self.assertEqual(self.service.call("GetPhase"), 3)

    def test_skald_counts_once_ondolemar_holds_the_amulet(self):
        self.release()
        condition = form("Skald", "actorHolds")
        self.assertFalse(self.file("Skald"))
        self.world.actor(condition["form"]).items[condition["other"]] = 1
        self.finish("Skald")

    def test_two_lesser_markarth_goals_end_the_operation(self):
        self.release()
        self.arrive(self.world.place(form("Shrine", "visited")["form"]))
        self.finish("Shrine")
        self.assertFalse(self.letter_sent("Interval"))
        self.arrive(self.world.place(form("Translator", "visited")["form"]))
        self.finish("Translator")
        self.assertTrue(self.letter_sent("Interval"))

    def test_namira_needs_the_quest_complete_and_the_priest_dead(self):
        self.release()
        self.world.quest(form("Feast", "questCompleted")["form"]).completed = True
        self.assertFalse(self.file("Feast"), "the priest walked away alive")
        self.world.actor(form("Feast", "actorDead")["form"]).dead = True
        self.finish("Feast")

    # Interval and College

    def test_interval_waits_for_time_and_some_magic(self):
        self.release()
        self.world.quest(form("OldMan", "questCompleted")["form"]).completed = True
        self.finish("OldMan")
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.service.call("GetPhase"), 3)
        self.vm.day += 7
        self.service.call("Evaluate")
        self.assertFalse(self.letter_sent("College"), "magic still an embarrassment")
        self.player.skills["Restoration"] = 20
        self.service.call("Evaluate")
        self.assertTrue(self.letter_sent("College"))

    def test_college_letter_encloses_its_reading_and_issues_the_college_orders(self):
        self.to_college()
        for book in CAMPAIGN["letters"][LETTER["College"]]["enclosures"]:
            self.assertEqual(self.player.items[book], 1)
        for key in ("Admission", "Saarthal", "Books", "Monk", "Eye", "Library", "Town"):
            self.assertEqual(self.state(key), 1, key)
        self.assertEqual(self.state("Lesson"), 0, "the Quest Expansion lesson needs that plugin")

    def test_admission_reads_first_lessons_stage_thirty(self):
        self.to_college()
        self.assertFalse(self.file("Admission"))
        self.world.quest(form("Admission", "stageDone")["form"]).done.add(30)
        self.finish("Admission")

    def test_adviser_letter_grants_removal_authority_when_the_staff_quest_begins(self):
        self.to_college()
        self.assertFalse(self.letter_sent("Adviser"))
        self.world.quest(form("Adviser", "questBegun")["form"]).running = True
        self.service.call("Evaluate")
        self.assertTrue(self.letter_sent("Adviser"))
        self.assertEqual(self.core.call("GetAuthority", CAMPAIGN["operations"]["removal"], 3), 0, "granted when read, not when sent")
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.core.call("GetAuthority", CAMPAIGN["operations"]["removal"], 3), 2)

    def test_arch_mage_declined_or_accepted_sends_the_matching_letter(self):
        for declined in (True, False):
            with self.subTest(declined=declined):
                self.setUp()
                self.to_college()
                self.world.quest(form("Declined", "stageDone")["form"]).done.add(200)
                if declined:
                    self.vm.plugins[(AYOP, 0x813)] = Global(1)
                else:
                    self.player.factions.add(form("Accepted", "playerInFaction")["form"])
                self.service.call("Evaluate")
                self.assertEqual(self.letter_sent("Declined"), declined)
                self.assertEqual(self.letter_sent("Accepted"), not declined)

    def test_arch_mage_decline_needs_at_your_own_pace(self):
        self.to_college()
        self.world.quest(form("Declined", "stageDone")["form"]).done.add(200)
        self.service.call("Evaluate")
        self.assertFalse(self.letter_sent("Declined"), "without the mod there is no way to decline")

    def test_arcanaeum_accepts_any_listed_book_and_takes_only_one(self):
        self.to_college()
        books = CAMPAIGN["arcanaeum"]["books"]
        self.player.items["SomeOtherBook"] = 1
        self.assertFalse(self.file("Library"))
        self.player.items[books[2]] = 2
        self.finish("Library")
        self.assertEqual(self.player.items[books[2]], 1)

    def test_quest_expansion_lesson_appears_only_with_the_plugin_and_reads_its_outcome(self):
        for refused in (False, True):
            with self.subTest(refused=refused):
                self.setUp()
                lesson = VanillaQuest("Cow_Reading", stage=30 if refused else 20, done={30} if refused else {20})
                self.vm.plugins[(CQE, 0x870)] = lesson
                self.to_college()
                self.assertEqual(self.state("Lesson"), 1)
                self.finish("Lesson")
                ins = CAMPAIGN["instructions"][INDEX["Lesson"]]
                self.assertEqual(self.player.items[ins["altReply"]["editorID"]], 1 if refused else 0)

    def test_winterhold_needs_both_the_longhouse_and_the_inn(self):
        self.to_college()
        places = [c["form"] for c in CAMPAIGN["instructions"][INDEX["Town"]]["conditions"]]
        self.arrive(self.world.place(places[0]))
        self.assertFalse(self.file("Town"))
        self.arrive(self.world.place(places[1]))
        self.finish("Town")

    # Robustness

    def test_letters_apply_their_effects_once(self):
        self.release()
        authority = self.core.call("GetAuthority", CAMPAIGN["operations"]["advance"], 5)
        tx = self.service.vars["lettertransactions"][LETTER["Release"]]
        self.service.call("ReceiveLetter", LETTER["Release"], tx)
        self.assertEqual(self.service.call("GetPhase"), 2)
        self.assertEqual(self.player.items[CAMPAIGN["letters"][LETTER["Release"]]["enclosures"][0]], 1)
        self.assertEqual(self.core.call("GetAuthority", CAMPAIGN["operations"]["advance"], 5), authority)

    def test_controller_lists_up_to_eight_open_instructions_ready_ones_first(self):
        menu = Menu()
        menu.choices.extend([5, 8, 0])
        self.assertEqual(self.service.call("ChooseInstruction", menu), 5)
        self.assertEqual(menu.shown[-1][:6], [2001, 2002, 2003, 2004, 2005, 2006])
        self.assertEqual(menu.shown[-1][6:8], [0, 0])
        self.assertEqual(self.service.call("ChooseInstruction", menu), -1)
        self.player.items[form("Hillside", "deliver")["form"]] = 1
        self.assertEqual(self.service.call("ChooseInstruction", menu), INDEX["Hillside"])
        self.assertEqual(menu.shown[-1][0], 2001 + INDEX["Hillside"], "a report that can be filed is listed first")

    def test_every_ready_report_stays_reachable_with_many_open(self):
        self.to_college()
        self.player.items[CAMPAIGN["arcanaeum"]["books"][0]] = 1
        open_count = sum(1 for i in range(len(CAMPAIGN["instructions"])) if self.core.call("GetAssignmentState", 2001 + i) in (1, 2, 3))
        self.assertGreater(open_count, 8)
        ready = [self.service.call("GetSlotIndex", k) for k in range(8)]
        self.assertIn(INDEX["Library"], ready, "a ready report is within the eight positions")
        positions = [k for k in ready if k >= 0]
        checks = [self.service.call("CheckAll", self.service.vars["::condstart_var"][k], self.service.vars["::condcount_var"][k]) for k in positions]
        self.assertEqual(checks, sorted(checks, reverse=True), "every ready report comes before every unready one")

    def test_campaign_survives_interpreter_serialization(self):
        self.sleep_at_inn(5)
        self.vm, self.core, self.dispatch, self.service, self.accounts = pickle.loads(pickle.dumps((self.vm, self.core, self.dispatch, self.service, self.accounts)))
        self.assertTrue(self.service.call("FileReport", INDEX["Inn"]))
        self.vm.day += 1
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.core.call("GetAssignmentState", 2001 + INDEX["Inn"]), 4)

    def test_service_player_alias_forwards_sleep_and_travel(self):
        alias = self.vm.instance("EA_ServicePlayer").prop("Service", self.service)
        alias.call("OnInit")
        self.player.location = self.inn
        alias.call("OnSleepStop", False)
        self.assertEqual(self.service.vars["nights"], 1)
        alias.call("OnLocationChange", None, self.world.place(form("Preacher", "visited")["form"]))
        self.assertTrue(self.file("Preacher"))


if __name__ == "__main__":
    unittest.main()
