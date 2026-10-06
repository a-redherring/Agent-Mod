import pickle
import unittest
from pathlib import Path

from papyrus_vm import OPERATION, Inventory, Menu, fixture

ASSEMBLY = Path(__file__).resolve().parents[1] / "build/Data/Scripts"


class RuntimeTests(unittest.TestCase):
    """Core, Dispatch and Accounts. The Accounts operation is opened and filed directly through Core."""

    def setUp(self):
        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY)

    def arrive(self):
        self.vm.day += 1
        return self.dispatch.call("CollectResponses")

    def file_operation(self):
        self.assertTrue(self.core.call("RecordFact", OPERATION, 1))
        self.assertTrue(self.core.call("FileAssignment", OPERATION))

    def advance(self):
        self.assertTrue(self.core.call("GrantAuthority", OPERATION, 5, 2, 0.0))
        self.assertTrue(self.accounts.call("IssueAdvance"))

    def test_commission_is_idempotent(self):
        self.assertFalse(self.core.call("Commission"))
        self.assertTrue(self.core.call("IsInService"))

    def test_recovery_survives_loss_of_both_copies(self):
        self.assertTrue(self.dispatch.call("ArchiveDocument", "Paper"))
        self.vm.player.items["Paper"] = 0
        self.dispatch.vars["::archive_var"].items["Paper"] = 0
        self.dispatch.call("RecoverFiledCopies")
        self.assertEqual(self.vm.player.items["Paper"], 1)
        self.assertEqual(self.dispatch.vars["::archive_var"].items["Paper"], 1)
        self.dispatch.call("RecoverFiledCopies")
        self.assertEqual(self.vm.player.items["Paper"], 1)

    def test_unissued_response_cannot_be_recovered_early(self):
        self.file_operation()
        self.accounts.call("SubmitClaim", 0)
        self.dispatch.call("RecoverDocument", "Decisions0")
        self.assertEqual(self.vm.player.items["Decisions0"], 0)

    def test_debug_recovery_is_gated_and_does_not_repay_settlement(self):
        self.file_operation()
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

    def test_file_requires_a_recorded_fact(self):
        self.assertFalse(self.core.call("FileAssignment", OPERATION))
        self.assertEqual(self.core.call("GetAssignmentState", OPERATION), 1)
        self.file_operation()
        self.assertEqual(self.core.call("GetAssignmentState", OPERATION), 3)
        self.assertFalse(self.core.call("FileAssignment", OPERATION))

    def test_deadline_boundary_and_single_consequence(self):
        self.assertTrue(self.core.call("RegisterAssignment", 5001, 3, 11.0))
        self.core.call("RefreshDeadlines", 11.0)
        self.assertEqual(self.core.call("GetAssignmentState", 5001), 1)
        self.core.call("RefreshDeadlines", 11.01)
        self.assertEqual(self.core.call("GetAssignmentState", 5001), 2)
        trust = self.core.vars["professionaltrust"]
        self.core.call("RefreshDeadlines", 100.0)
        self.assertEqual(self.core.vars["professionaltrust"], trust)
        self.assertEqual(self.core.call("GetAssignmentState", OPERATION), 1, "campaign assignments have no deadline")

    def test_suspension_preserves_travel_time(self):
        self.core.call("RegisterAssignment", 5001, 3, 11.0)
        index = self.core.call("FindAssignment", 5001)
        self.core.call("SuspendDeadlines")
        self.vm.day += 20
        self.core.call("RefreshDeadlines", self.vm.day)
        self.assertEqual(self.core.call("GetAssignmentState", 5001), 1)
        self.core.call("ResumeDeadlines")
        self.assertEqual(self.core.vars["assignmentdue"][index], 31)

    def test_authority_is_scoped_and_expires(self):
        self.assertTrue(self.core.call("GrantAuthority", OPERATION, 1, 1, 0.0))
        self.assertEqual(self.core.call("GetAuthority", OPERATION, 1), 1)
        self.assertEqual(self.core.call("GetAuthority", OPERATION, 3), 0)
        self.assertEqual(self.core.call("GetAuthority", 9999, 1), 0)
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
        self.assertFalse(self.core.call("RegisterAssignment", OPERATION, 4, 0.0))
        self.assertFalse(self.core.call("RegisterAssignment", -1, 3, 20.0))
        self.assertFalse(self.core.call("RegisterAssignment", 99, 7, 20.0))
        self.assertTrue(self.core.call("RegisterAssignment", 2001, 1, 20.0))
        self.assertFalse(self.core.call("RegisterAssignment", 2002, 1, 20.0))
        for n in range(31):
            self.assertTrue(self.core.call("RegisterAssignment", 6000 + n, 4, 0.0))
        self.assertFalse(self.core.call("RegisterAssignment", 6031, 4, 0.0), "thirty-two open campaign assignments at most")
        self.assertFalse(self.core.call("HasFact", -1))

    def test_dispatch_rejects_replay_instant_and_full_queue(self):
        args = (500, 2001, 1, "out", "in", self.service)
        self.assertFalse(self.dispatch.call("Queue", *args, 0.0))
        self.assertTrue(self.dispatch.call("Queue", *args, 1.0))
        self.assertFalse(self.dispatch.call("Queue", *args, 1.0))
        self.dispatch.vars["count"] = 128
        self.assertFalse(self.dispatch.call("Queue", 501, 2001, 1, "out", "in", self.service, 1.0))
        self.assertFalse(self.dispatch.call("Send", 502, 2900, "letter", self.service))

    def test_sent_letter_is_ready_at_once_and_collected_once(self):
        self.assertTrue(self.dispatch.call("Send", 700, 2899, "Note", self.service))
        self.assertFalse(self.dispatch.call("Send", 700, 2899, "Note", self.service))
        self.assertEqual(self.vm.notifications[-1], "Something has been left in the dispatch case.")
        self.assertEqual(self.dispatch.call("CountResponses", True), 1)
        self.assertEqual(self.dispatch.call("CollectResponses"), 1)
        self.assertEqual(self.vm.player.items["Note"], 1)
        self.assertEqual(self.dispatch.call("CollectResponses"), 0)

    def test_advance_requires_authority_and_cannot_repeat(self):
        self.assertFalse(self.accounts.call("IssueAdvance"))
        self.advance()
        self.assertFalse(self.accounts.call("IssueAdvance"))
        self.assertEqual(self.vm.player.items["Gold"], 80)

    def test_approved_claim_without_advance_pays_once(self):
        self.assertFalse(self.accounts.call("SubmitClaim", 0))
        self.file_operation()
        self.assertTrue(self.accounts.call("SubmitClaim", 0))
        self.assertEqual(self.vm.player.items["Gold"], 0)
        self.arrive()
        self.assertEqual(self.vm.player.items["Gold"], 30)
        self.assertFalse(self.accounts.call("SubmitClaim", 0))
        self.accounts.call("ReceiveResponse", self.accounts.vars["claimtransaction"], OPERATION, 1)
        self.assertEqual(self.vm.player.items["Gold"], 30)

    def test_claim_offsets_advance_instead_of_paying_twice(self):
        self.advance()
        self.file_operation()
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
        self.file_operation()
        self.accounts.call("SubmitClaim", 1)
        self.arrive()
        self.assertEqual(self.accounts.vars["amountallowed"], 30)
        self.assertEqual(self.accounts.vars["advanceoutstanding"], 0)
        self.assertEqual(self.accounts.vars["operationaldebt"], 50)
        self.assertTrue(self.accounts.vars["financialprobation"])
        self.accounts.call("ReturnFunds")
        self.assertFalse(self.accounts.vars["financialprobation"])

    def test_denied_self_funded_claim_does_not_create_embassy_debt(self):
        self.file_operation()
        self.accounts.call("SubmitClaim", 2)
        self.arrive()
        self.assertEqual(self.accounts.vars["operationaldebt"], 0)
        self.assertEqual(self.accounts.vars["personalcost"], 30)
        self.assertEqual(self.vm.player.items["Gold"], 0)

    def test_returned_claim_needs_explanation_and_second_transit(self):
        self.file_operation()
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
        self.file_operation()
        self.accounts.call("SubmitClaim", 0)
        self.arrive()
        self.assertEqual(self.accounts.vars["operationaldebt"], 50)
        self.assertEqual(self.vm.player.items["Gold"], 80)

    def test_amounts_come_from_the_plugin_not_the_script(self):
        self.accounts.prop("AdvanceAmount", 500).prop("ClaimAmounts", [500, 650, 60, 40]).prop("AllowedAmount", 500)
        self.advance()
        self.assertEqual(self.vm.player.items["Gold"], 500)
        self.file_operation()
        self.accounts.call("SubmitClaim", 1)
        self.arrive()
        self.assertEqual(self.accounts.vars["amountallowed"], 500)
        self.assertEqual(self.accounts.vars["personalcost"], 150)
        self.assertEqual(self.accounts.vars["operationaldebt"], 0)

    def test_state_serialization_during_dispatch(self):
        self.file_operation()
        self.accounts.call("SubmitClaim", 0)
        self.vm, self.core, self.dispatch, self.service, self.accounts = pickle.loads(pickle.dumps((self.vm, self.core, self.dispatch, self.service, self.accounts)))
        self.assertEqual(self.dispatch.call("CollectResponses"), 0)
        self.arrive()
        self.assertEqual(self.vm.player.items["Gold"], 30)

    def test_prototype_initial_supplies_only_once_and_busy_state(self):
        self.core.vars["serviceactive"] = False
        p = controller(self)
        p.call("UseBox", Inventory())
        p.call("UseBox", Inventory())
        self.assertEqual(self.vm.player.items["Gold"], 100)
        self.assertEqual(self.vm.player.items["Commission"], 1)
        self.assertTrue(self.core.call("HasEstablishedCover"))
        self.assertEqual(self.service.call("GetPhase"), 1, "the console path also begins the campaign")
        p.call("GoToState", "Busy")
        p.call("UseBox", Inventory())
        self.assertEqual(self.vm.player.items["Gold"], 100)


def controller(test):
    p = test.vm.instance("EA_Prototype")
    for key, value in {"Core": test.core, "Dispatch": test.dispatch, "Service": test.service, "Accounts": test.accounts}.items():
        p.prop(key, value)
    for key in ("Gold", "Commission", "ArchiveBase", "BoxBase", "CaseItem"):
        p.prop(key, key)
    for key in ("CommissionMenu", "MainMenu", "AssignmentMenu", "AccountsMenu", "ClaimMenu", "ExplanationMenu", "FiledMessage",
                "UnavailableMessage", "CollectedMessage", "RepaymentMenu", "ReturnedMessage", "CaseMenu"):
        p.prop(key, Menu())
    return p


if __name__ == "__main__":
    unittest.main()
