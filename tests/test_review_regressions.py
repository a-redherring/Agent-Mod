"""Regressions found during the post-build source and behavior review."""
import unittest
from pathlib import Path

from papyrus_vm import OPERATION, fixture, Inventory, Menu

ASSEMBLY = Path(__file__).resolve().parents[1] / "build/Data/Scripts"


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY)

    def deliver(self):
        self.assertTrue(self.core.call("RecordFact", OPERATION, 1))
        self.assertTrue(self.core.call("FileAssignment", OPERATION))

    def advance(self):
        self.core.call("GrantAuthority", OPERATION, 5, 2, 0.0)
        self.assertTrue(self.accounts.call("IssueAdvance"))

    def paused(self):
        """A deadline assignment for the suspension tests: due on day 11, at the given index."""
        self.assertTrue(self.core.call("RegisterAssignment", 5001, 3, 11.0))
        return self.core.call("FindAssignment", 5001)

    def test_zero_transaction_completes_nothing_and_pays_nothing(self):
        self.service.call("BeginCampaign")
        self.service.call("ReceiveResponse", 0, 2001, 1)
        self.assertEqual(self.core.call("GetAssignmentState", 2001), 1)
        self.deliver()
        self.accounts.call("ReceiveResponse", 0, OPERATION, 1)
        self.assertEqual(self.vm.player.items["Gold"], 0)

    def test_letter_callback_cannot_bypass_collection(self):
        self.service.call("BeginCampaign")
        self.service.vars["nights"] = 3
        self.service.call("Evaluate")
        tx = self.service.vars["lettertransactions"][0]
        self.assertGreater(tx, 0)
        self.service.call("ReceiveResponse", tx, 2900, 0)
        self.assertFalse(self.service.vars["letterdone"][0])
        self.dispatch.call("CollectResponses")
        self.assertTrue(self.service.vars["letterdone"][0])

    def test_accounts_callback_cannot_pay_early(self):
        self.deliver()
        self.accounts.call("SubmitClaim", 0)
        self.accounts.call("ReceiveResponse", self.accounts.vars["claimtransaction"], OPERATION, 1)
        self.assertEqual(self.vm.player.items["Gold"], 0)
        self.vm.day += 1
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.vm.player.items["Gold"], 30)

    def test_advance_requires_prior_not_emergency_or_standing_authority(self):
        for mode in (1, 3):
            self.core.call("GrantAuthority", OPERATION, 5, mode, 0.0)
            self.assertFalse(self.accounts.call("IssueAdvance"))
        self.core.call("GrantAuthority", OPERATION, 5, 2, 0.0)
        self.assertTrue(self.accounts.call("IssueAdvance"))

    def test_returned_claim_does_not_prevent_audit_forever(self):
        self.advance()
        self.deliver()
        self.accounts.call("SubmitClaim", 3)
        self.vm.day += 1
        self.dispatch.call("CollectResponses")
        self.assertTrue(self.accounts.call("NeedsExplanation"))
        self.vm.day += 30
        self.accounts.call("Audit")
        self.assertEqual(self.accounts.vars["operationaldebt"], 80)
        self.assertTrue(self.accounts.call("ExplainClaim", True))
        self.vm.day += 1
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.accounts.vars["operationaldebt"], 65)
        self.assertEqual(self.vm.player.items["Gold"], 80)

    def test_uncollected_response_does_not_prevent_audit_forever(self):
        self.advance()
        self.deliver()
        self.accounts.call("SubmitClaim", 0)
        self.vm.day += 30
        self.accounts.call("Audit")
        self.assertEqual(self.accounts.vars["operationaldebt"], 80)
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.accounts.vars["operationaldebt"], 50)

    def test_nested_deadline_suspension_ends_only_after_last_resume(self):
        index = self.paused()
        self.core.call("SuspendDeadlines")
        self.vm.day += 2
        self.core.call("SuspendDeadlines")
        self.vm.day += 20
        self.core.call("ResumeDeadlines")
        self.core.call("RefreshDeadlines", self.vm.day)
        self.assertEqual(self.core.call("GetAssignmentState", 5001), 1)
        self.assertEqual(self.core.vars["assignmentdue"][index], 11)
        self.vm.day += 2
        self.core.call("ResumeDeadlines")
        self.assertEqual(self.core.vars["assignmentdue"][index], 35)

    def test_new_assignment_during_pause_keeps_only_remaining_duration(self):
        self.core.call("SuspendDeadlines")
        self.vm.day += 4
        self.core.call("RegisterAssignment", 2000, 2, self.vm.day + 10)
        self.vm.day += 6
        self.core.call("ResumeDeadlines")
        index = self.core.call("FindAssignment", 2000)
        self.assertEqual(self.core.vars["assignmentdue"][index], self.vm.day + 10)

    def test_extension_during_pause_does_not_add_elapsed_time_twice(self):
        index = self.paused()
        self.core.call("SuspendDeadlines")
        self.vm.day += 20
        self.core.call("ExtendAssignment", 5001, 5.0)
        self.core.call("ResumeDeadlines")
        self.assertEqual(self.core.vars["assignmentdue"][index], 36)

    def test_timer_has_minimum_interval_and_no_stale_notification(self):
        self.deliver()
        self.accounts.call("SubmitClaim", 0)
        self.vm.day = 1.99999
        self.dispatch.call("ScheduleNext")
        self.assertGreaterEqual((self.dispatch.timer - self.vm.day) * 24, 0.0999)
        self.vm.day = 2
        self.dispatch.call("CollectResponses")
        self.dispatch.call("OnUpdateGameTime")
        self.assertEqual(self.vm.notifications, [])

    def test_native_reference_double_uses_identity_not_inventory_contents(self):
        self.assertNotEqual(Inventory(), Inventory())

    def controller(self):
        self.core.vars["serviceactive"] = False
        p = self.vm.instance("EA_Prototype")
        for key, value in {"Core": self.core, "Dispatch": self.dispatch, "Service": self.service, "Accounts": self.accounts}.items():
            p.prop(key, value)
        for key in ("Gold", "Commission", "ArchiveBase", "BoxBase", "CaseItem"):
            p.prop(key, key)
        for key in ("CommissionMenu", "MainMenu", "AssignmentMenu", "AccountsMenu", "ClaimMenu", "ExplanationMenu", "FiledMessage", "UnavailableMessage", "CollectedMessage", "RepaymentMenu", "ReturnedMessage", "CaseMenu"):
            p.prop(key, Menu())
        return p

    def test_failed_framework_start_does_not_pay_or_leave_controller_busy(self):
        p = self.controller()
        self.accounts.can_start = False
        p.call("UseBox", Inventory())
        self.assertFalse(p.vars["supplied"])
        self.assertEqual(self.vm.player.items["Gold"], 0)
        self.assertEqual(p.call("GetState"), "")
        self.accounts.can_start = True
        p.call("UseBox", Inventory())
        self.assertEqual(self.vm.player.items["Gold"], 100)

    def test_cancel_is_a_silent_no_op(self):
        for main, submenu, cancel in ((0, "AssignmentMenu", 8), (2, "AccountsMenu", 4)):
            with self.subTest(main=main):
                p = self.controller()
                p.vars["::mainmenu_var"].choices.append(main)
                p.vars["::" + submenu.lower() + "_var"].choices.append(cancel)
                p.call("UseBox", Inventory())
                self.assertEqual(p.vars["::unavailablemessage_var"].shown, [])
                self.assertEqual(self.dispatch.vars["count"], 0)
                self.assertTrue(all(not m.shown for m in self.service.vars["::failuremessages_var"]))

    def test_non_player_activation_is_ignored(self):
        p = self.controller()
        box = self.vm.instance("EA_DispatchBox").prop("Controller", p)
        box.call("OnActivate", Inventory())
        self.assertFalse(p.running)
        self.assertFalse(p.vars["supplied"])

    def test_busy_state_really_suppresses_another_menu(self):
        p = self.controller()
        p.call("GoToState", "Busy")
        self.assertEqual(p.call("GetState"), "Busy")
        p.call("UseBox", Inventory())
        self.assertEqual(p.vars["::mainmenu_var"].shown, [])
        self.assertFalse(p.vars["supplied"])
        p.call("GoToState", "")
        p.call("UseBox", Inventory())
        self.assertEqual(len(p.vars["::mainmenu_var"].shown), 1)

    def test_response_cannot_be_replaced_with_a_more_favorable_outcome(self):
        self.deliver()
        self.accounts.call("SubmitClaim", 1)
        self.vm.day += 1
        tx = self.accounts.vars["claimtransaction"]
        index = self.dispatch.call("FindTransaction", tx)
        self.dispatch.vars["states"][index] = 2
        self.accounts.call("ReceiveResponse", tx, OPERATION, 1)
        self.assertEqual(self.vm.player.items["Gold"], 0)
        self.core.prop("DebugEnabled", True)
        self.dispatch.call("DebugRecoverPending", tx)
        self.assertEqual(self.vm.player.items["Gold"], 30)

    def test_audit_still_defers_during_real_return_transit(self):
        self.advance()
        self.vm.day += 13.5
        self.deliver()
        self.accounts.call("SubmitClaim", 0)
        self.vm.day += 0.6
        self.accounts.call("Audit")
        self.assertFalse(self.accounts.vars["audited"])
        self.vm.day += 0.5
        self.accounts.call("Audit")
        self.assertTrue(self.accounts.vars["audited"])

    def test_own_expense_repayment_is_limited_to_available_gold(self):
        self.advance()
        self.vm.player.items["Gold"] = 7
        self.assertEqual(self.accounts.call("ReturnFunds"), 7)
        self.assertEqual(self.accounts.vars["advanceoutstanding"], 73)
        self.assertEqual(self.vm.player.items["Gold"], 0)
        self.assertEqual(self.accounts.call("ReturnFunds"), 0)

    def test_declared_meal_explanation_and_reply_are_specific(self):
        self.deliver()
        self.accounts.call("SubmitClaim", 3)
        self.vm.day += 1
        self.dispatch.call("CollectResponses")
        self.accounts.call("ExplainClaim", True)
        self.assertEqual(self.dispatch.vars["::archive_var"].items["ExplanationForm"], 1)
        self.assertEqual(self.dispatch.vars["::archive_var"].items["PersonalExplanationForm"], 0)
        self.vm.day += 1
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.vm.player.items["MealPartialDecision"], 1)
        self.assertEqual(self.vm.player.items["Gold"], 15)

    def test_personal_meal_explanation_remains_denied(self):
        self.deliver()
        self.accounts.call("SubmitClaim", 3)
        self.vm.day += 1
        self.dispatch.call("CollectResponses")
        self.accounts.call("ExplainClaim", False)
        self.assertEqual(self.dispatch.vars["::archive_var"].items["PersonalExplanationForm"], 1)
        self.vm.day += 1
        self.dispatch.call("CollectResponses")
        self.assertEqual(self.vm.player.items["Gold"], 0)
        self.assertEqual(self.accounts.vars["amountallowed"], 0)

    def test_document_capacity_is_reserved_before_accepting_a_transaction(self):
        while self.dispatch.vars["documentcount"] < 127:
            self.assertTrue(self.dispatch.call("ArchiveDocument", "Filler" + str(self.dispatch.vars["documentcount"])))
        before = self.dispatch.vars["count"]
        self.assertFalse(self.dispatch.call("Queue", 500, 2001, 1, "newout", "newreply", self.service, 1.0))
        self.assertEqual(self.dispatch.vars["count"], before)
        self.assertEqual(self.dispatch.vars["::archive_var"].items["newout"], 0)
        self.assertTrue(self.dispatch.call("Queue", 501, 2001, 1, "Filler0", "newreply", self.service, 1.0))
        self.assertEqual(self.dispatch.vars["documentcount"], 128)
        self.dispatch.call("RecoverFiledCopies")
        self.assertEqual(self.vm.player.items["newreply"], 0)
        self.assertFalse(self.dispatch.call("ArchiveDocument", "overflow"))

    def test_accounting_conserves_cash_against_advance_and_debt(self):
        # Independent invariant: net money supplied minus money still owed equals
        # the allowed expense, across repayments, audits and every final outcome.
        for repayment in (0, 13, 80):
            for audit in (False, True):
                for choice, explain, allowed in ((0, None, 30), (1, None, 30), (2, None, 0), (3, True, 15), (3, False, 0)):
                    with self.subTest(repayment=repayment, audit=audit, choice=choice, explain=explain):
                        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY)
                        self.advance()
                        self.vm.player.items["Gold"] = repayment
                        returned = self.accounts.call("ReturnFunds")
                        if audit:
                            self.vm.day += 15
                            self.accounts.call("Audit")
                        self.deliver()
                        self.accounts.call("SubmitClaim", choice)
                        self.vm.day += 1
                        self.dispatch.call("CollectResponses")
                        if explain is not None:
                            self.accounts.call("ExplainClaim", explain)
                            self.vm.day += 1
                            self.dispatch.call("CollectResponses")
                        outstanding = self.accounts.vars["advanceoutstanding"] + self.accounts.vars["operationaldebt"]
                        self.assertEqual(80 - returned + self.vm.player.items["Gold"] - outstanding, allowed)
                        self.assertGreaterEqual(outstanding, 0)
