import pickle
import unittest
from pathlib import Path

from papyrus_vm import fixture, Inventory, Menu

ASSEMBLY = Path(__file__).resolve().parents[1] / "build/Data/Scripts"


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY)

    def arrive(self):
        self.vm.day += 1
        return self.dispatch.call("CollectResponses")

    def deliver_wine(self):
        self.vm.player.items["Wine"] = 3
        self.assertTrue(self.service.call("FileReport", 1, -1))

    def advance(self):
        self.assertTrue(self.service.call("RequestSupplyAuthority"))
        self.arrive()
        self.assertTrue(self.accounts.call("IssueAdvance"))

    def test_commission_and_orders_are_idempotent(self):
        self.assertFalse(self.core.call("Commission"))
        self.service.call("CollectOrders")
        self.assertEqual(self.core.call("CountWorkload", 3), 3)
        self.assertEqual(self.vm.player.items["Orders0"], 1)

    def test_lost_order_recovery_does_not_reset_deadline(self):
        due = list(self.core.vars["assignmentdue"])
        self.vm.player.items["Orders1"] = 0
        self.vm.day += 3
        self.service.call("CollectOrders")
        self.assertEqual(self.vm.player.items["Orders1"], 1)
        self.assertEqual(due, self.core.vars["assignmentdue"])

    def test_recovery_survives_loss_of_both_copies(self):
        self.vm.player.items["Orders1"] = 0
        self.dispatch.vars["::archive_var"].items["Orders1"] = 0
        self.dispatch.call("RecoverFiledCopies")
        self.assertEqual(self.vm.player.items["Orders1"], 1)
        self.assertEqual(self.dispatch.vars["::archive_var"].items["Orders1"], 1)
        self.assertEqual(self.core.call("GetAssignmentState", 1002), 1)

    def test_unissued_response_cannot_be_recovered_early(self):
        self.deliver_wine()
        self.dispatch.call("RecoverDocument", "PromptResponses1")
        self.assertEqual(self.vm.player.items["PromptResponses1"], 0)
        self.assertEqual(self.core.call("GetAssignmentState", 1002), 3)

    def test_debug_recovery_is_gated_and_does_not_repay_settlement(self):
        self.deliver_wine()
        self.accounts.call("SubmitClaim", 0)
        self.arrive()
        tx = self.accounts.vars["claimtransaction"]
        index = self.dispatch.call("FindTransaction", tx)
        self.dispatch.vars["states"][index] = 2
        self.assertFalse(self.dispatch.call("DebugRecoverPending", tx))
        self.core.prop("DebugEnabled", True)
        self.assertTrue(self.dispatch.call("DebugRecoverPending", tx))
        self.assertEqual(self.vm.player.items["Gold"], 30)
        self.assertFalse(self.dispatch.call("DebugRecoverPending", tx))

    def test_report_requires_real_fact(self):
        self.assertFalse(self.service.call("FileReport", 0, -1))
        papers = self.vm.instance("EA_FieldPapers").prop("Core", self.core)
        papers.call("OnRead")
        self.assertTrue(self.service.call("FileReport", 0, -1))
        self.assertEqual(self.core.call("GetAssignmentState", 1001), 3)
        self.assertEqual(self.dispatch.call("CollectResponses"), 0)
        self.assertEqual(self.arrive(), 1)
        self.assertEqual(self.core.call("GetAssignmentState", 1001), 4)

    def test_supply_delivery_is_consumed_only_once(self):
        self.assertFalse(self.service.call("FileReport", 1, -1))
        self.deliver_wine()
        self.assertEqual(self.vm.player.items["Wine"], 0)
        self.assertEqual(self.dispatch.vars["::archive_var"].items["Wine"], 0)
        self.assertFalse(self.service.call("FileReport", 1, -1))
        self.arrive()
        self.assertEqual(self.dispatch.call("CollectResponses"), 0)
        self.assertEqual(self.vm.player.items["PromptResponses1"], 1)

    def test_deadline_boundary_and_single_consequence(self):
        self.core.call("RefreshDeadlines", 11.0)
        self.assertEqual(self.core.call("GetAssignmentState", 1001), 1)
        self.core.call("RefreshDeadlines", 11.01)
        self.assertEqual(self.core.call("GetAssignmentState", 1001), 2)
        trust = self.core.vars["professionaltrust"]
        self.core.call("RefreshDeadlines", 100.0)
        self.assertEqual(self.core.vars["professionaltrust"], trust)
        self.core.call("RecordFact", 1001, 1)
        self.assertTrue(self.service.call("FileReport", 0, -1))

    def test_suspension_preserves_travel_time(self):
        self.core.call("SuspendDeadlines")
        self.vm.day += 20
        self.core.call("RefreshDeadlines", self.vm.day)
        self.assertEqual(self.core.call("GetAssignmentState", 1001), 1)
        self.core.call("ResumeDeadlines")
        self.assertEqual(self.core.vars["assignmentdue"][0], 31)

    def test_extension_is_delayed_then_second_request_denied(self):
        self.assertTrue(self.service.call("RequestExtension", 0))
        self.assertFalse(self.service.call("RequestExtension", 0))
        self.assertEqual(self.core.vars["assignmentdue"][0], 11)
        self.arrive()
        self.assertEqual(self.core.vars["assignmentdue"][0], 16)
        self.assertTrue(self.service.call("RequestExtension", 0))
        self.arrive()
        self.assertEqual(self.core.vars["assignmentdue"][0], 16)

    def test_closed_assignment_is_not_reopened_by_extension(self):
        self.service.call("RequestExtension", 1)
        self.deliver_wine()
        self.arrive()
        self.assertEqual(self.core.call("GetAssignmentState", 1002), 4)

    def test_authority_is_scoped_and_expires(self):
        self.assertEqual(self.core.call("GetAuthority", 1001, 1), 1)
        self.assertEqual(self.core.call("GetAuthority", 1001, 3), 0)
        self.assertEqual(self.core.call("GetAuthority", 1002, 1), 0)
        self.assertTrue(self.core.call("GrantAuthority", 9001, 3, 2, 2.0))
        self.assertEqual(self.core.call("GetAuthority", 9002, 3), 0)
        self.vm.day = 3
        self.assertEqual(self.core.call("GetAuthority", 9001, 3), 0)
        self.assertFalse(self.core.call("GrantAuthority", 0, 1, 1, 0.0))

    def test_emergency_has_explicit_review_and_no_blanket_permission(self):
        self.assertFalse(self.core.call("RecordEmergency", 9010, 4))
        self.core.call("GrantAuthority", 9010, 4, 3, 0.0)
        self.assertTrue(self.core.call("RecordEmergency", 9010, 4))
        self.assertTrue(self.core.call("NeedsEmergencyReview", 9010, 4))
        self.core.call("ReviewEmergency", 9010, 4, False)
        self.assertFalse(self.core.call("NeedsEmergencyReview", 9010, 4))
        self.assertEqual(self.core.call("GetAuthority", 9010, 4), 0)

    def test_workload_and_invalid_identifiers(self):
        self.assertFalse(self.core.call("RegisterAssignment", 1001, 3, 20.0))
        self.assertFalse(self.core.call("RegisterAssignment", -1, 3, 20.0))
        self.assertFalse(self.core.call("RegisterAssignment", 99, 7, 20.0))
        self.assertTrue(self.core.call("RegisterAssignment", 2001, 1, 20.0))
        self.assertFalse(self.core.call("RegisterAssignment", 2002, 1, 20.0))
        self.assertFalse(self.core.call("HasFact", -1))
        self.assertFalse(self.service.call("FileReport", 3, -1))
        self.assertFalse(self.service.call("RequestExtension", -1))

    def test_dispatch_rejects_replay_instant_and_full_queue(self):
        args = (500, 1001, 1, "out", "in", self.service)
        self.assertFalse(self.dispatch.call("Queue", *args, 0.0))
        self.assertTrue(self.dispatch.call("Queue", *args, 1.0))
        self.assertFalse(self.dispatch.call("Queue", *args, 1.0))
        self.dispatch.vars["count"] = 128
        self.assertFalse(self.dispatch.call("Queue", 501, 1001, 1, "out", "in", self.service, 1.0))
        self.assertFalse(self.service.call("FileReport", 0, -1))

    def test_advance_requires_authority_and_cannot_repeat(self):
        self.assertFalse(self.accounts.call("IssueAdvance"))
        self.service.call("RequestSupplyAuthority")
        self.assertFalse(self.accounts.call("IssueAdvance"))
        self.arrive()
        self.assertTrue(self.accounts.call("IssueAdvance"))
        self.assertFalse(self.accounts.call("IssueAdvance"))
        self.assertEqual(self.vm.player.items["Gold"], 80)

    def test_approved_claim_without_advance_pays_once(self):
        self.assertFalse(self.accounts.call("SubmitClaim", 0))
        self.deliver_wine()
        self.assertTrue(self.accounts.call("SubmitClaim", 0))
        self.assertEqual(self.vm.player.items["Gold"], 0)
        self.arrive()
        self.assertEqual(self.vm.player.items["Gold"], 30)
        self.assertFalse(self.accounts.call("SubmitClaim", 0))
        self.accounts.call("ReceiveResponse", self.accounts.vars["claimtransaction"], 1002, 1)
        self.assertEqual(self.vm.player.items["Gold"], 30)

    def test_claim_offsets_advance_instead_of_paying_twice(self):
        self.advance()
        self.deliver_wine()
        self.accounts.call("SubmitClaim", 0)
        self.arrive()
        self.assertEqual(self.vm.player.items["Gold"], 80)
        self.assertEqual(self.accounts.vars["advanceoutstanding"], 50)
        self.assertEqual(self.accounts.vars["operationaldebt"], 0)
        self.assertEqual(self.accounts.call("ReturnFunds"), 50)
        self.assertEqual(self.vm.player.items["Gold"], 30)
        self.assertEqual(self.accounts.call("ReturnFunds"), 0)

    def test_partial_claim_creates_only_funded_liability(self):
        self.advance()
        self.deliver_wine()
        self.accounts.call("SubmitClaim", 1)
        self.arrive()
        self.assertEqual(self.accounts.vars["amountallowed"], 30)
        self.assertEqual(self.accounts.vars["advanceoutstanding"], 0)
        self.assertEqual(self.accounts.vars["operationaldebt"], 50)
        self.assertTrue(self.accounts.vars["financialprobation"])
        self.accounts.call("ReturnFunds")
        self.assertFalse(self.accounts.vars["financialprobation"])

    def test_denied_self_funded_claim_does_not_create_embassy_debt(self):
        self.deliver_wine()
        self.accounts.call("SubmitClaim", 2)
        self.arrive()
        self.assertEqual(self.accounts.vars["operationaldebt"], 0)
        self.assertEqual(self.accounts.vars["personalcost"], 30)
        self.assertEqual(self.vm.player.items["Gold"], 0)

    def test_returned_claim_needs_explanation_and_second_transit(self):
        self.deliver_wine()
        self.accounts.call("SubmitClaim", 3)
        self.arrive()
        self.assertTrue(self.accounts.call("NeedsExplanation"))
        self.assertEqual(self.vm.player.items["Gold"], 0)
        self.accounts.call("ExplainClaim", True)
        self.assertFalse(self.accounts.call("ExplainClaim", True))
        self.assertEqual(self.dispatch.call("CollectResponses"), 0)
        self.arrive()
        self.assertEqual(self.vm.player.items["Gold"], 15)

    def test_audit_then_valid_claim_discharges_liability(self):
        self.advance()
        self.vm.day += 15
        self.accounts.call("Audit")
        self.assertEqual(self.accounts.vars["operationaldebt"], 80)
        self.accounts.call("Audit")
        self.assertEqual(self.vm.player.items["AuditNotice"], 1)
        self.deliver_wine()
        self.accounts.call("SubmitClaim", 0)
        self.arrive()
        self.assertEqual(self.accounts.vars["operationaldebt"], 50)
        self.assertEqual(self.vm.player.items["Gold"], 80)

    def test_state_serialization_during_dispatch(self):
        self.deliver_wine()
        self.accounts.call("SubmitClaim", 0)
        self.vm, self.core, self.dispatch, self.service, self.accounts = pickle.loads(pickle.dumps((self.vm, self.core, self.dispatch, self.service, self.accounts)))
        self.assertEqual(self.dispatch.call("CollectResponses"), 0)
        self.arrive()
        self.assertEqual(self.vm.player.items["Gold"], 30)
        self.assertEqual(self.core.call("GetAssignmentState", 1002), 4)

    def test_prototype_initial_supplies_only_once_and_busy_state(self):
        p = self.vm.instance("EA_Prototype")
        for key, value in {"Core": self.core, "Dispatch": self.dispatch, "Service": self.service, "Accounts": self.accounts}.items():
            p.prop(key, value)
        for key in ("Gold", "Commission", "FieldPapers", "ArchiveBase"):
            p.prop(key, key)
        for key in ("CommissionMenu", "MainMenu", "AssignmentMenu", "AccountsMenu", "ClaimMenu", "ExplanationMenu", "FiledMessage", "UnavailableMessage", "CollectedMessage", "RepaymentMenu", "ReturnedMessage", "ReviewPendingMessage"):
            p.prop(key, Menu())
        p.call("UseBox", Inventory())
        p.call("UseBox", Inventory())
        self.assertEqual(self.vm.player.items["Gold"], 100)
        self.assertEqual(self.vm.player.items["Commission"], 1)
        p.call("GoToState", "Busy")
        p.call("UseBox", Inventory())
        self.assertEqual(self.vm.player.items["Gold"], 100)


if __name__ == "__main__":
    unittest.main()
