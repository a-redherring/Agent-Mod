"""Behavioral coverage for authored packets, circulation, judgement and Accounts, using compiled Papyrus."""
import pickle
import unittest
from pathlib import Path

from papyrus_vm import PACKETS, Inventory, Menu, fixture

ASSEMBLY = Path(__file__).resolve().parents[1] / 'build/Data/Scripts'
COUNT = len(PACKETS)
CASES = [i for i, p in enumerate(PACKETS) if 'case' in p]
PLAIN = [i for i, p in enumerate(PACKETS) if 'case' not in p]


def sound(index):
    return PACKETS[index]['case']['sound']


class AdditionTests(unittest.TestCase):
    def setUp(self):
        self.vm, self.core, self.dispatch, self.service, self.accounts = fixture(ASSEMBLY)

    def arrive(self):
        self.vm.day += 1
        return self.dispatch.call('CollectResponses')

    def state(self, index):
        return self.core.call('GetAssignmentState', 1001 + index)

    def open_packets(self):
        return [i for i in range(COUNT) if self.state(i) in (1, 2)]

    def read_case(self, index):
        papers = self.vm.instance('EA_CaseFile').prop('Core', self.core).prop('AssignmentID', 1001 + index)
        papers.call('OnRead')

    def stock(self, index):
        packet = PACKETS[index]
        if 'supply' in packet:
            self.vm.player.items[packet['key']] += packet['supply']['count']

    def file(self, index, conclusion=None):
        if index == 0:
            self.core.call('RecordFieldPapersRead')
        self.stock(index)
        if 'case' in PACKETS[index]:
            self.read_case(index)
            conclusion = sound(index) if conclusion is None else conclusion
        else:
            conclusion = -1
        self.assertTrue(self.service.call('FileReport', index, conclusion), index)

    def first_packet(self):
        for i in range(3):
            self.file(i)
        self.assertEqual(self.arrive(), 3)

    def open_until(self, index):
        """Work the circulation until the given packet has been issued."""
        while self.state(index) == 0:
            for i in self.open_packets():
                self.file(i)
            self.arrive()
            self.service.call('CollectOrders')

    def complete_all(self, late=(), wrong=()):
        """File every packet as it is issued; listed packets are filed late or misjudged."""
        maximum = 0
        for _ in range(COUNT * 2):
            if self.service.call('CountState', 4) == COUNT:
                break
            maximum = max(maximum, self.service.call('CountOpen'))
            batch = self.open_packets()
            for i in batch:
                if i not in late:
                    self.file(i, (sound(i) + 1) % 3 if i in wrong else None)
            overdue = [i for i in batch if i in late]
            if overdue:
                self.vm.day += max(self.core.call('GetDaysRemaining', 1001 + i) for i in overdue) + 0.01
                for i in overdue:
                    self.file(i, (sound(i) + 1) % 3 if i in wrong else None)
            self.arrive()
            self.service.call('CollectOrders')
        self.assertEqual(self.service.call('CountState', 4), COUNT)
        return maximum

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

    # Circulation

    def test_packets_circulate_in_order_three_at_a_time_without_repeats(self):
        self.assertEqual(self.open_packets(), [0, 1, 2])
        for i in range(3):
            self.file(i)
        self.service.call('CollectOrders')
        self.assertEqual(self.state(3), 0, 'a filed report still occupies its position')
        self.arrive()
        self.vm.day += 20
        self.service.call('CollectOrders')
        self.assertEqual(self.open_packets(), [3, 4, 5])
        for i in (3, 4, 5):
            self.assertEqual(self.core.call('GetDaysRemaining', 1001 + i), 10)
        due = list(self.core.vars['assignmentdue'])
        self.service.call('CollectOrders')
        self.assertEqual(due, self.core.vars['assignmentdue'])
        self.assertLessEqual(self.complete_all(), 3)
        self.assertEqual(self.core.vars['assignmentcount'], COUNT)
        for i in range(COUNT):
            self.assertEqual(self.vm.player.items[f'Orders{i}'], 1)
        self.service.call('CollectOrders')
        self.assertEqual(self.core.vars['assignmentcount'], COUNT)

    def test_later_packet_never_overtakes_an_earlier_one(self):
        self.file(1)
        self.file(2)
        self.arrive()
        self.service.call('CollectOrders')
        self.assertEqual(self.open_packets(), [0, 3, 4])
        self.file(4)
        self.arrive()
        self.service.call('CollectOrders')
        self.assertEqual(self.open_packets(), [0, 3, 5])

    def test_assignment_menu_lists_open_instruction_numbers_by_position(self):
        menu = Menu()
        menu.choices.extend([2, 3])
        self.assertEqual(self.service.call('ChooseInstruction', menu), 2)
        self.assertEqual(menu.shown[-1][:3], [1001, 1002, 1003])
        self.assertEqual(self.service.call('ChooseInstruction', menu), -1)
        self.file(0)
        self.arrive()
        self.service.call('CollectOrders')
        menu.choices.append(2)
        self.assertEqual(self.service.call('ChooseInstruction', menu), 3)
        self.assertEqual(menu.shown[-1][:3], [1002, 1003, 1004])
        self.setUp()
        for i in range(3):
            self.file(i)
        self.arrive()
        self.assertEqual(self.service.call('GetSlotAssignment', 0), 0)
        menu.choices.append(0)
        self.assertEqual(self.service.call('ChooseInstruction', menu), -1)

    def test_new_packet_notice_is_once_and_does_not_start_deadlines(self):
        self.file(0)
        self.arrive()
        self.service.call('CheckPacketNotice')
        self.service.call('CheckPacketNotice')
        self.assertEqual(len(self.service.vars['::packetreadymessage_var'].shown), 1)
        self.assertEqual(self.state(3), 0)
        self.service.call('CollectOrders')
        self.file(1)
        self.arrive()
        self.service.call('CheckPacketNotice')
        self.assertEqual(len(self.service.vars['::packetreadymessage_var'].shown), 2)

    # Named items

    def test_named_item_is_required_and_substitutes_are_refused(self):
        for index, substitute in ((1, 'AltoWine'), (2, 'SomeOtherBook')):
            with self.subTest(index=index):
                required = PACKETS[index]['supply']['count']
                self.vm.player.items[substitute] = 10
                self.assertFalse(self.service.call('FileReport', index, -1))
                self.assertEqual(self.service.vars['lasterror'], 10)
                self.service.call('ShowFailure')
                supply = self.service.vars['::supplyindex_var'][index]
                self.assertEqual(self.service.vars['::missingmessages_var'][supply].shown[-1][0], required)
                self.assertEqual(self.vm.player.items[substitute], 10)
                self.assertEqual(self.dispatch.vars['count'], 0)

    def test_supplies_check_quantity_consume_once_and_keep_surplus(self):
        for index in [i for i in PLAIN if 'supply' in PACKETS[i]]:
            with self.subTest(index=index):
                self.setUp()
                self.open_until(index)
                key, required = PACKETS[index]['key'], PACKETS[index]['supply']['count']
                supply = self.service.vars['::supplyindex_var'][index]
                self.vm.player.items[key] = required - 1
                self.assertFalse(self.service.call('FileReport', index, -1))
                self.service.call('ShowFailure')
                self.assertEqual(self.service.vars['::missingmessages_var'][supply].shown[-1][0], 1)
                self.vm.player.items[key] = required + 2
                self.assertTrue(self.service.call('FileReport', index, -1))
                self.assertEqual(self.vm.player.items[key], 2)
                self.assertFalse(self.service.call('FileReport', index, -1))
                self.assertEqual(self.vm.player.items[key], 2)
                self.assertEqual(self.dispatch.vars['::archive_var'].items[key], 0)
                self.arrive()
                self.assertEqual(self.state(index), 4)
                self.assertTrue(self.service.objectives[('setobjectivecompleted', 200 + index)])

    # Case papers and conclusions

    def test_case_papers_are_issued_with_the_order_and_recoverable_once(self):
        index = CASES[0]
        case = 'Case' + PACKETS[index]['key']
        self.assertEqual(self.vm.player.items[case], 0)
        self.open_until(index)
        self.assertEqual(self.vm.player.items[case], 1)
        self.assertEqual(self.dispatch.vars['::archive_var'].items[case], 1)
        self.vm.player.items[case] = 0
        self.dispatch.vars['::archive_var'].items[case] = 0
        self.service.call('CollectOrders')
        self.service.call('CollectOrders')
        self.dispatch.call('RecoverFiledCopies')
        self.assertEqual(self.vm.player.items[case], 1)
        self.assertEqual(self.dispatch.vars['::archive_var'].items[case], 1)

    def test_conclusion_requires_read_papers_and_supplies_before_it_is_asked(self):
        index = CASES[0]
        key = PACKETS[index]['key']
        self.open_until(index)
        self.stock(index)
        self.assertFalse(self.service.call('IsReadyForConclusion', index))
        self.assertFalse(self.service.call('FileReport', index, sound(index)))
        self.assertEqual(self.service.vars['lasterror'], 8)
        self.assertEqual(self.vm.player.items[key], 1)
        self.read_case(index)
        self.vm.player.items[key] = 0
        self.assertFalse(self.service.call('IsReadyForConclusion', index))
        self.stock(index)
        self.assertTrue(self.service.call('IsReadyForConclusion', index))
        for missing in (-1, 3):
            self.assertFalse(self.service.call('FileReport', index, missing))
            self.assertEqual(self.service.vars['lasterror'], 9)
        self.assertEqual(self.vm.player.items[key], 1)
        self.assertEqual(self.state(index), 1)

    def test_reading_papers_for_an_unissued_case_records_nothing(self):
        index = CASES[0]
        self.read_case(index)
        self.open_until(index)
        self.assertFalse(self.core.call('HasFact', 1001 + index))

    def test_every_case_selects_sound_or_misjudged_response(self):
        for index in CASES:
            for conclusion in range(3):
                with self.subTest(index=index, conclusion=conclusion):
                    self.setUp()
                    self.open_until(index)
                    trust = self.core.vars['professionaltrust']
                    self.file(index, conclusion)
                    self.arrive()
                    key = PACKETS[index]['key']
                    self.assertEqual(self.state(index), 4)
                    if conclusion == sound(index):
                        self.assertEqual(self.vm.player.items[f'PromptResponses{index}'], 1)
                        self.assertEqual(self.vm.player.items['Misjudged' + key], 0)
                        self.assertEqual(self.core.vars['professionaltrust'], trust + 1)
                    else:
                        self.assertEqual(self.vm.player.items['Misjudged' + key], 1)
                        self.assertEqual(self.vm.player.items[f'PromptResponses{index}'], 0)
                        self.assertEqual(self.core.vars['professionaltrust'], trust - 1)

    def test_sound_conclusion_keeps_prompt_ordinary_and_late_tone(self):
        index = CASES[0]
        for offset, expected in ((0, 'PromptResponses'), (5.01, 'Responses'), (10.01, 'LateResponses')):
            with self.subTest(offset=offset):
                self.setUp()
                self.open_until(index)
                self.vm.day += offset
                self.file(index)
                self.arrive()
                self.assertEqual(self.vm.player.items[f'{expected}{index}'], 1)

    def test_controller_asks_for_conclusion_only_when_ready_and_cancel_is_silent(self):
        index = CASES[0]
        self.open_until(index)
        position = self.open_packets().index(index)
        menu = self.service.vars['::conclusionmenus_var'][0]
        p = self.controller()
        p.vars['::mainmenu_var'].choices.append(1)
        p.vars['::assignmentmenu_var'].choices.append(position)
        p.call('UseBox', Inventory())
        self.assertEqual(len(self.service.vars['::failuremessages_var'][8].shown), 1)
        self.assertEqual(menu.shown, [])
        self.read_case(index)
        self.stock(index)
        count = self.dispatch.vars['count']
        p.vars['::mainmenu_var'].choices.append(1)
        p.vars['::assignmentmenu_var'].choices.append(position)
        menu.choices.append(3)
        p.call('UseBox', Inventory())
        self.assertEqual(len(menu.shown), 1)
        self.assertEqual(self.dispatch.vars['count'], count)
        self.assertEqual(self.vm.player.items[PACKETS[index]['key']], 1)
        self.assertEqual(len(p.vars['::filedmessage_var'].shown), 0)
        p.vars['::mainmenu_var'].choices.append(1)
        p.vars['::assignmentmenu_var'].choices.append(position)
        menu.choices.append(sound(index))
        p.call('UseBox', Inventory())
        self.assertEqual(self.state(index), 3)
        self.assertEqual(len(p.vars['::filedmessage_var'].shown), 1)

    # Register, status and replies

    def test_summary_distinguishes_ready_and_transit_without_delivering(self):
        self.file(1)
        self.service.call('ShowSummary')
        summary = self.service.vars['::summarymessage_var']
        self.assertEqual(summary.shown[-1][:7], [2, 0, 1, 0, COUNT, 0, 1])
        self.vm.day += 1
        self.service.call('ShowSummary')
        self.assertEqual(summary.shown[-1][:7], [2, 0, 1, 0, COUNT, 1, 0])
        self.assertEqual(self.state(1), 3)
        self.assertEqual(self.vm.player.items['PromptResponses1'], 0)
        self.dispatch.call('CollectResponses')
        self.vm.day = 12
        self.service.call('ShowSummary')
        self.assertEqual(summary.shown[-1][:7], [0, 2, 0, 1, COUNT, 0, 0])

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
        self.assertEqual(self.state(1), 1)
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
        self.assertEqual(self.service.vars['::missingmessages_var'][0].shown[-1][0], 2)
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
        self.assertFalse(self.service.call('FileReport', 1, -1))
        self.assertEqual(self.service.vars['lasterror'], 1)

    def test_full_series_with_every_extension_fits_dispatch_capacity(self):
        self.advance()
        while self.open_packets():
            for i in self.open_packets():
                for _ in range(2):
                    self.assertTrue(self.service.call('RequestExtension', i))
                    self.arrive()
                self.file(i)
            self.arrive()
            self.service.call('CollectOrders')
        self.accounts.call('SubmitClaim', 3)
        self.arrive()
        self.accounts.call('ExplainClaim', True)
        self.arrive()
        self.accounts.call('ReturnAmount', 0)
        self.assertTrue(self.queue_review())
        self.arrive()
        self.assertEqual(self.service.call('GetEvaluationState'), 2)
        self.assertLessEqual(self.dispatch.vars['documentcount'], 128)
        self.assertLessEqual(self.dispatch.vars['count'], 128)
        self.dispatch.call('RecoverFiledCopies')

    # Accounts

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

    # Closing assessment

    def test_closing_assessment_requires_every_packet_and_a_full_day_then_cannot_repeat(self):
        while self.open_packets():
            self.assertFalse(self.queue_review())
            for i in self.open_packets():
                self.file(i)
            self.assertFalse(self.queue_review())
            self.arrive()
            self.service.call('CollectOrders')
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
        self.assertTrue(self.service.objectives[('setobjectivecompleted', 300)])
        self.assertFalse(self.queue_review())
        self.assertEqual(self.dispatch.call('CollectResponses'), 0)
        self.assertEqual(self.vm.player.items['Gold'], gold)

    def test_evaluation_counts_late_and_misjudged_reports(self):
        for late, wrong, expected in (((), (), 0), ((1,), (), 1), ((), (CASES[0],), 1), ((1, 2), (), 2), ((1,), (CASES[-1],), 2), ((CASES[0],), (CASES[0],), 2)):
            with self.subTest(late=late, wrong=wrong):
                self.setUp()
                self.complete_all(late, wrong)
                self.assertTrue(self.queue_review())
                self.arrive()
                self.assertEqual(self.vm.player.items[f'Evaluations{expected}'], 1)

    def test_evaluation_waits_for_explanation_and_uses_final_accounts_decision(self):
        self.complete_all()
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
                self.complete_all()
                if reason == 'gift':
                    self.accounts.call('SubmitClaim', 2)
                    self.arrive()
                self.assertEqual(self.accounts.call('GetReviewConcern'), 2)
                self.assertTrue(self.queue_review())
                self.arrive()
                self.assertEqual(self.vm.player.items['Evaluations2'], 1)

    def test_controller_queues_evaluation_after_collecting_final_responses(self):
        while True:
            batch = self.open_packets()
            for i in batch:
                self.file(i)
            if self.service.call('NextUnissued') < 0:
                break
            self.arrive()
            self.service.call('CollectOrders')
        self.vm.day += 1
        p = self.controller()
        p.vars['::mainmenu_var'].choices.append(5)
        p.call('UseBox', Inventory())
        self.assertEqual(self.service.call('GetEvaluationState'), 1)
        self.assertEqual(self.dispatch.call('CountResponses', False), 1)
        self.assertEqual(self.dispatch.call('CountResponses', True), 0)
        self.assertEqual(p.vars['::collectedmessage_var'].shown[-1][0], len(batch))
        self.vm.day += 1
        p.vars['::mainmenu_var'].choices.append(5)
        p.call('UseBox', Inventory())
        self.assertEqual(self.service.call('GetEvaluationState'), 2)
        self.assertEqual(len(self.service.vars['::evaluationqueuedmessage_var'].shown), 1)

    def test_later_claim_does_not_describe_an_issued_review_as_waiting(self):
        self.complete_all()
        self.assertTrue(self.queue_review())
        self.accounts.call('SubmitClaim', 0)
        p = self.controller()
        p.vars['::mainmenu_var'].choices.append(7)
        self.service.vars['::summarymessage_var'].choices.append(1)
        p.call('UseBox', Inventory())
        self.assertEqual(p.vars['::reviewpendingmessage_var'].shown, [])
        self.assertEqual(self.service.call('GetEvaluationState'), 1)

    def test_circulation_and_review_survive_interpreter_state_serialization(self):
        self.advance()
        self.accounts.call('ReturnAmount', 25)
        index = CASES[0]
        self.open_until(index)
        self.read_case(index)
        self.vm, self.core, self.dispatch, self.service, self.accounts = pickle.loads(pickle.dumps((self.vm, self.core, self.dispatch, self.service, self.accounts)))
        self.assertEqual(self.accounts.call('GetOutstanding'), 55)
        self.stock(index)
        self.assertTrue(self.service.call('IsReadyForConclusion', index))
        self.assertTrue(self.service.call('FileReport', index, sound(index)))
        self.complete_all()
        self.assertTrue(self.queue_review())
        self.vm, self.core, self.dispatch, self.service, self.accounts = pickle.loads(pickle.dumps((self.vm, self.core, self.dispatch, self.service, self.accounts)))
        self.assertFalse(self.queue_review())
        self.arrive()
        self.assertEqual(self.vm.player.items['Evaluations2'], 1)
        self.assertEqual(self.service.call('GetEvaluationState'), 2)


if __name__ == '__main__':
    unittest.main()
