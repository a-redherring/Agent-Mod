"""Behavioral coverage for the six 0.1.2 additions using compiled Papyrus."""
import pickle
import unittest
from pathlib import Path

from papyrus_vm import Inventory, Menu, fixture

ASSEMBLY = Path(__file__).resolve().parents[1] / 'build/Data/Scripts'


class AdditionTests(unittest.TestCase):
    def setUp(self):
        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY)

    def arrive(self):
        self.vm.day += 1
        return self.dispatch.call('CollectResponses')

    def file(self, index):
        if index == 0:
            self.core.call('RecordFieldPapersRead')
        else:
            item, quantity = {1: ('Wine', 3), 2: ('Flowers', 6), 3: ('Firewood', 6), 4: ('LeatherStrips', 4), 5: ('Wheat', 6)}[index]
            self.vm.player.items[item] += quantity
        self.assertTrue(self.service.call('FileReport', index))

    def first_packet(self):
        for i in range(3):
            self.file(i)
        self.assertEqual(self.arrive(), 3)

    def all_duties(self):
        self.first_packet()
        self.service.call('CollectOrders')
        for i in range(3, 6):
            self.file(i)
        self.assertEqual(self.arrive(), 3)

    def advance(self):
        self.assertTrue(self.service.call('RequestSupplyAuthority'))
        self.arrive()
        self.assertTrue(self.accounts.call('IssueAdvance'))

    def controller(self):
        p = self.vm.instance('EA_Prototype')
        for name, value in {'Core': self.core, 'Dispatch': self.dispatch, 'Service': self.service, 'Accounts': self.accounts}.items():
            p.prop(name, value)
        for name in ('Gold', 'Commission', 'FieldPapers', 'ArchiveBase'):
            p.prop(name, name)
        for name in ('CommissionMenu', 'MainMenu', 'AssignmentMenu', 'AccountsMenu', 'ClaimMenu', 'ExplanationMenu', 'FiledMessage', 'UnavailableMessage', 'CollectedMessage', 'RepaymentMenu', 'ReturnedMessage', 'ReviewPendingMessage'):
            p.prop(name, Menu())
        return p

    def queue_review(self):
        return self.service.call('TryQueueEvaluation', self.accounts.call('GetReviewConcern'), self.accounts.call('IsReviewPending'))

    def test_second_packet_requires_acknowledgments_and_starts_on_collection(self):
        self.vm.player.items['Firewood'] = 6
        self.assertFalse(self.service.call('FileReport', 3))
        self.assertEqual(self.vm.player.items['Firewood'], 6)
        for i in range(3):
            self.file(i)
        self.service.call('CollectOrders')
        self.assertEqual(self.core.call('GetAssignmentState', 1004), 0)
        self.arrive()
        self.vm.day += 20
        self.service.call('CollectOrders')
        for i in range(3, 6):
            self.assertEqual(self.core.call('GetDaysRemaining', 1001 + i), 10)
            self.assertEqual(self.vm.player.items[f'Orders{i}'], 1)
        due = list(self.core.vars['assignmentdue'])
        self.service.call('CollectOrders')
        self.assertEqual(due, self.core.vars['assignmentdue'])
        self.assertEqual(self.core.call('CountWorkload', 3), 3)

    def test_new_supplies_check_quantity_consume_once_and_keep_surplus(self):
        self.first_packet()
        self.service.call('CollectOrders')
        for i, item, required in ((3, 'Firewood', 6), (4, 'LeatherStrips', 4), (5, 'Wheat', 6)):
            with self.subTest(item=item):
                self.vm.player.items[item] = required - 2
                self.assertFalse(self.service.call('FileReport', i))
                self.service.call('ShowFailure')
                self.assertEqual(self.service.vars['::missingmessages_var'][i].shown[-1][0], 2)
                self.vm.player.items[item] = required + 2
                self.assertTrue(self.service.call('FileReport', i))
                self.assertEqual(self.vm.player.items[item], 2)
                self.assertFalse(self.service.call('FileReport', i))
                self.assertEqual(self.vm.player.items[item], 2)
                self.assertEqual(self.dispatch.vars['::archive_var'].items[item], 0)
        self.assertEqual(self.arrive(), 3)
        self.assertEqual(self.service.call('CountState', 4), 6)
        for i in range(3, 6):
            self.assertEqual(self.vm.player.items[f'PromptResponses{i}'], 1)
            self.assertTrue(self.service.objectives[('setobjectivecompleted', 20 + i)])

    def test_summary_distinguishes_ready_and_transit_without_delivering(self):
        self.file(1)
        self.service.call('ShowSummary')
        summary = self.service.vars['::summarymessage_var']
        self.assertEqual(summary.shown[-1][:6], [2, 0, 1, 0, 0, 1])
        self.vm.day += 1
        self.service.call('ShowSummary')
        self.assertEqual(summary.shown[-1][:6], [2, 0, 1, 0, 1, 0])
        self.assertEqual(self.core.call('GetAssignmentState', 1002), 3)
        self.assertEqual(self.vm.player.items['PromptResponses1'], 0)
        self.dispatch.call('CollectResponses')
        self.vm.day = 12
        self.service.call('ShowSummary')
        self.assertEqual(summary.shown[-1][:6], [0, 2, 0, 1, 0, 0])

    def test_status_deadlines_respect_suspension_and_report_each_state(self):
        messages = self.service.vars['::statusmessages_var']
        self.service.call('ShowAssignmentStatus', 3)
        self.assertEqual(messages[0].shown[-1][0], 1004)
        self.vm.day = 3.25
        self.core.call('SuspendDeadlines')
        self.vm.day = 40
        self.service.call('ShowAssignmentStatus', 1)
        self.assertEqual(messages[1].shown[-1][:2], [1002, 7.75])
        self.core.call('ResumeDeadlines')
        self.vm.day = 48.5
        self.service.call('ShowAssignmentStatus', 1)
        self.assertEqual(messages[2].shown[-1][:2], [1002, .75])
        self.file(1)
        self.service.call('ShowAssignmentStatus', 1)
        self.assertEqual(messages[3].shown[-1][0], 1002)
        self.arrive()
        self.service.call('ShowAssignmentStatus', 1)
        self.assertEqual(messages[4].shown[-1][0], 1002)

    def test_response_tone_uses_filing_time_and_is_fixed_during_transit(self):
        for day, expected in ((1, 'PromptResponses1'), (6, 'PromptResponses1'), (6.01, 'Responses1'), (11, 'Responses1'), (11.01, 'LateResponses1')):
            with self.subTest(day=day):
                self.setUp()
                self.vm.day = day
                self.file(1)
                self.vm.day += 20
                self.dispatch.call('CollectResponses')
                self.assertEqual(self.vm.player.items[expected], 1)
                self.assertEqual(sum(self.vm.player.items[x] for x in ('Responses1', 'PromptResponses1', 'LateResponses1')), 1)

    def test_extension_does_not_erase_a_missed_deadline_or_earn_prompt_praise(self):
        self.vm.day = 12
        self.core.call('RefreshDeadlines', self.vm.day)
        self.assertTrue(self.service.call('RequestExtension', 1))
        self.arrive()
        self.assertEqual(self.core.call('GetAssignmentState', 1002), 1)
        self.file(1)
        self.arrive()
        self.assertEqual(self.vm.player.items['LateResponses1'], 1)
        self.setUp()
        self.service.call('RequestExtension', 1)
        self.arrive()
        self.file(1)
        self.arrive()
        self.assertEqual(self.vm.player.items['Responses1'], 1)

    def test_controller_shows_specific_supply_and_protocol_feedback(self):
        p = self.controller()
        p.vars['::mainmenu_var'].choices.append(1)
        p.vars['::assignmentmenu_var'].choices.append(0)
        p.call('UseBox', Inventory())
        self.assertEqual(len(self.service.vars['::failuremessages_var'][2].shown), 1)
        self.vm.player.items['Wine'] = 1
        p.vars['::mainmenu_var'].choices.append(1)
        p.vars['::assignmentmenu_var'].choices.append(1)
        p.call('UseBox', Inventory())
        self.assertEqual(self.service.vars['::missingmessages_var'][1].shown[-1][0], 2)
        self.assertEqual(self.dispatch.vars['count'], 0)
        self.assertEqual(p.vars['::unavailablemessage_var'].shown, [])

    def test_pending_and_closed_requests_get_distinct_feedback(self):
        self.service.call('RequestSupplyAuthority')
        self.assertFalse(self.service.call('RequestSupplyAuthority'))
        self.assertEqual(self.service.vars['lasterror'], 5)
        self.arrive()
        self.assertFalse(self.service.call('RequestSupplyAuthority'))
        self.assertEqual(self.service.vars['lasterror'], 6)
        self.service.call('RequestExtension', 1)
        self.assertFalse(self.service.call('RequestExtension', 1))
        self.assertEqual(self.service.vars['lasterror'], 3)
        self.arrive()
        self.service.call('RequestExtension', 1)
        self.arrive()
        self.assertFalse(self.service.call('RequestExtension', 1))
        self.assertEqual(self.service.vars['lasterror'], 4)
        self.file(1)
        self.assertFalse(self.service.call('FileReport', 1))
        self.assertEqual(self.service.vars['lasterror'], 1)

    def test_partial_repayments_bound_balance_inventory_and_invalid_amount(self):
        self.advance()
        self.assertEqual(self.accounts.call('ReturnAmount', -10), 0)
        self.assertEqual(self.accounts.call('GetOutstanding'), 80)
        self.assertEqual(self.accounts.call('ReturnAmount', 10), 10)
        self.assertEqual(self.accounts.call('ReturnAmount', 25), 25)
        self.vm.player.items['Gold'] = 7
        self.assertEqual(self.accounts.call('ReturnAmount', 25), 7)
        self.assertEqual(self.accounts.call('GetOutstanding'), 38)
        self.assertEqual(self.accounts.call('ReturnAmount', 10), 0)
        self.assertEqual(self.accounts.vars['lasterror'], 9)
        self.vm.player.items['Gold'] = 100
        self.assertEqual(self.accounts.call('ReturnAmount', 0), 38)
        self.assertEqual(self.vm.player.items['Gold'], 62)
        self.assertEqual(self.accounts.call('ReturnAmount', 25), 0)
        self.assertEqual(self.accounts.vars['lasterror'], 8)

    def test_partial_payments_conserve_money_across_every_claim_outcome(self):
        for choice, explanation, allowed in ((0, None, 30), (1, None, 30), (2, None, 0), (3, True, 15), (3, False, 0)):
            for audit in (False, True):
                with self.subTest(choice=choice, explanation=explanation, audit=audit):
                    self.setUp()
                    self.advance()
                    returned = self.accounts.call('ReturnAmount', 10)
                    if audit:
                        self.vm.day += 15
                        self.accounts.call('Audit')
                    returned += self.accounts.call('ReturnAmount', 25)
                    self.file(1)
                    self.accounts.call('SubmitClaim', choice)
                    self.arrive()
                    if explanation is not None:
                        self.accounts.call('ExplainClaim', explanation)
                        self.arrive()
                    self.assertEqual(self.vm.player.items['Gold'] - self.accounts.call('GetOutstanding'), allowed)
                    returned += self.accounts.call('ReturnAmount', 25)
                    self.assertEqual(self.vm.player.items['Gold'] - self.accounts.call('GetOutstanding'), allowed)
                    self.assertGreater(returned, 0)

    def test_repayment_menu_reports_actual_amount_and_cancel_is_silent(self):
        self.advance()
        p = self.controller()
        for choice, amount, left in ((0, 10, 70), (1, 25, 45), (2, 45, 0)):
            p.vars['::accountsmenu_var'].choices.append(2)
            p.vars['::repaymentmenu_var'].choices.append(choice)
            p.call('UseAccounts')
            self.assertEqual(p.vars['::returnedmessage_var'].shown[-1][:2], [amount, left])
        p.vars['::accountsmenu_var'].choices.append(2)
        p.vars['::repaymentmenu_var'].choices.append(3)
        p.call('UseAccounts')
        self.assertEqual(len(p.vars['::returnedmessage_var'].shown), 3)
        self.assertTrue(all(not m.shown for m in self.accounts.vars['::failuremessages_var']))

    def test_accounts_explains_missing_permission_and_claim_progress(self):
        p = self.controller()
        p.call('UseAccounts')
        self.assertEqual(len(self.accounts.vars['::failuremessages_var'][3].shown), 1)
        self.assertFalse(self.accounts.call('SubmitClaim', 0))
        self.assertEqual(self.accounts.vars['lasterror'], 4)
        self.file(1)
        self.accounts.call('SubmitClaim', 0)
        self.assertFalse(self.accounts.call('SubmitClaim', 0))
        self.assertEqual(self.accounts.vars['lasterror'], 5)
        self.arrive()
        self.assertFalse(self.accounts.call('SubmitClaim', 0))
        self.assertEqual(self.accounts.vars['lasterror'], 6)

    def test_closing_assessment_requires_all_six_and_a_full_day_then_cannot_repeat(self):
        self.first_packet()
        self.assertFalse(self.queue_review())
        self.service.call('CollectOrders')
        for i in range(3, 6):
            self.file(i)
        self.assertFalse(self.queue_review())
        self.arrive()
        self.assertTrue(self.queue_review())
        self.assertEqual(self.service.call('GetEvaluationState'), 1)
        self.dispatch.call('RecoverDocument', 'Evaluations0')
        self.assertEqual(self.vm.player.items['Evaluations0'], 0)
        tx = self.service.vars['evaluationtransaction']
        self.service.call('ReceiveResponse', tx, 1099, 10)
        self.assertEqual(self.service.call('GetEvaluationState'), 1)
        self.assertFalse(self.queue_review())
        self.assertEqual(self.dispatch.call('CollectResponses'), 0)
        gold = self.vm.player.items['Gold']
        self.arrive()
        self.assertEqual(self.service.call('GetEvaluationState'), 2)
        self.assertEqual(self.vm.player.items['Evaluations0'], 1)
        self.assertTrue(self.service.objectives[('setobjectivecompleted', 30)])
        self.assertFalse(self.queue_review())
        self.assertEqual(self.dispatch.call('CollectResponses'), 0)
        self.assertEqual(self.vm.player.items['Gold'], gold)

    def test_evaluation_reflects_single_and_repeated_late_duties(self):
        for late_count, expected in ((1, 1), (2, 2)):
            with self.subTest(late_count=late_count):
                self.setUp()
                for i in range(late_count, 3):
                    self.file(i)
                self.vm.day = 12
                for i in range(late_count):
                    self.file(i)
                self.arrive()
                self.service.call('CollectOrders')
                for i in range(3, 6):
                    self.file(i)
                self.arrive()
                self.assertTrue(self.queue_review())
                self.arrive()
                self.assertEqual(self.vm.player.items[f'Evaluations{expected}'], 1)

    def test_evaluation_waits_for_explanation_and_uses_final_accounts_decision(self):
        self.all_duties()
        self.accounts.call('SubmitClaim', 3)
        self.assertFalse(self.queue_review())
        self.arrive()
        self.assertFalse(self.queue_review())
        p = self.controller()
        p.vars['::mainmenu_var'].choices.append(7)
        self.service.vars['::summarymessage_var'].choices.append(1)
        p.call('UseBox', Inventory())
        self.assertEqual(len(p.vars['::reviewpendingmessage_var'].shown), 1)
        self.accounts.call('ExplainClaim', True)
        self.assertFalse(self.queue_review())
        self.arrive()
        self.assertEqual(self.accounts.call('GetReviewConcern'), 1)
        self.assertTrue(self.queue_review())
        self.arrive()
        self.assertEqual(self.vm.player.items['Evaluations1'], 1)

    def test_outstanding_advance_and_denied_expense_receive_reprimand(self):
        for reason in ('advance', 'gift'):
            with self.subTest(reason=reason):
                self.setUp()
                if reason == 'advance':
                    self.advance()
                self.all_duties()
                if reason == 'gift':
                    self.accounts.call('SubmitClaim', 2)
                    self.arrive()
                self.assertEqual(self.accounts.call('GetReviewConcern'), 2)
                self.assertTrue(self.queue_review())
                self.arrive()
                self.assertEqual(self.vm.player.items['Evaluations2'], 1)

    def test_audit_history_survives_repayment_but_timely_return_is_clean(self):
        self.advance()
        self.accounts.call('ReturnAmount', 0)
        self.vm.day += 15
        self.accounts.call('Audit')
        self.assertEqual(self.accounts.call('GetReviewConcern'), 0)
        self.setUp()
        self.advance()
        self.vm.day += 15
        self.accounts.call('Audit')
        self.accounts.call('ReturnAmount', 0)
        self.assertEqual(self.accounts.call('GetReviewConcern'), 2)

    def test_controller_queues_evaluation_after_collecting_final_responses(self):
        self.first_packet()
        self.service.call('CollectOrders')
        for i in range(3, 6):
            self.file(i)
        self.vm.day += 1
        p = self.controller()
        p.vars['::mainmenu_var'].choices.append(5)
        p.call('UseBox', Inventory())
        self.assertEqual(self.service.call('GetEvaluationState'), 1)
        self.assertEqual(self.dispatch.call('CountResponses', False), 1)
        self.assertEqual(self.dispatch.call('CountResponses', True), 0)
        self.assertEqual(p.vars['::collectedmessage_var'].shown[-1][0], 3)
        self.vm.day += 1
        p.vars['::mainmenu_var'].choices.append(5)
        p.call('UseBox', Inventory())
        self.assertEqual(self.service.call('GetEvaluationState'), 2)
        self.assertEqual(len(self.service.vars['::evaluationqueuedmessage_var'].shown), 1)

    def test_new_packet_notice_is_once_and_does_not_start_deadlines(self):
        self.first_packet()
        self.service.call('CheckPacketNotice')
        self.service.call('CheckPacketNotice')
        self.assertEqual(len(self.service.vars['::packetreadymessage_var'].shown), 1)
        self.assertEqual(self.core.call('GetAssignmentState', 1004), 0)

    def test_later_claim_does_not_describe_an_issued_review_as_waiting(self):
        self.all_duties()
        self.assertTrue(self.queue_review())
        self.accounts.call('SubmitClaim', 0)
        p = self.controller()
        p.vars['::mainmenu_var'].choices.append(7)
        self.service.vars['::summarymessage_var'].choices.append(1)
        p.call('UseBox', Inventory())
        self.assertEqual(p.vars['::reviewpendingmessage_var'].shown, [])
        self.assertEqual(self.service.call('GetEvaluationState'), 1)

    def test_new_packet_and_review_survive_interpreter_state_serialization(self):
        self.advance()
        self.accounts.call('ReturnAmount', 25)
        self.first_packet()
        self.service.call('CollectOrders')
        self.file(3)
        self.vm, self.core, self.dispatch, self.service, self.accounts = pickle.loads(pickle.dumps((self.vm, self.core, self.dispatch, self.service, self.accounts)))
        self.assertEqual(self.accounts.call('GetOutstanding'), 55)
        self.assertFalse(self.service.call('FileReport', 3))
        self.file(4)
        self.file(5)
        self.arrive()
        self.assertTrue(self.queue_review())
        self.vm, self.core, self.dispatch, self.service, self.accounts = pickle.loads(pickle.dumps((self.vm, self.core, self.dispatch, self.service, self.accounts)))
        self.assertFalse(self.queue_review())
        self.arrive()
        self.assertEqual(self.vm.player.items['Evaluations2'], 1)
        self.assertEqual(self.service.call('GetEvaluationState'), 2)


if __name__ == '__main__':
    unittest.main()
