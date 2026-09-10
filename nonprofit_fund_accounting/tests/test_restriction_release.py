# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
from odoo.tests import tagged

from .common import FundAccountingCommon


@tagged("post_install", "-at_install")
class TestRestrictionRelease(FundAccountingCommon):
    def _release(self, **kw):
        vals = {
            "fund_from_id": self.fund_drp.id,
            "fund_to_id": self.fund_ur.id,
            "amount": 500.0,
            "journal_id": self.misc_journal.id,
        }
        vals.update(kw)
        return self.env["nonprofit.restriction.release"].create(vals)

    def test_post_creates_balanced_entry(self):
        release = self._release()
        release.action_post()

        self.assertEqual(release.state, "posted")
        move = release.move_id
        self.assertTrue(move)
        self.assertEqual(move.state, "posted")
        self.assertEqual(len(move.line_ids), 2)

        debit = move.line_ids.filtered(lambda l: l.debit)
        credit = move.line_ids.filtered(lambda l: l.credit)
        self.assertEqual(debit.account_id, self.release_restricted)
        self.assertEqual(credit.account_id, self.release_unrestricted)
        self.assertEqual(debit.debit, 500.0)
        self.assertEqual(credit.credit, 500.0)
        self.assertEqual(debit.analytic_distribution, {str(self.fund_drp.id): 100.0})
        self.assertEqual(credit.analytic_distribution, {str(self.fund_ur.id): 100.0})

    def test_sequence_assigned(self):
        release = self._release()
        self.assertNotEqual(release.name, "New")
        self.assertIn("REL/", release.name)

    def test_program_function_flow_through(self):
        program = self.env.ref("nonprofit_base.analytic_account_program_general")
        release = self._release(program_id=program.id)
        release.action_post()
        debit = release.move_id.line_ids.filtered(lambda l: l.debit)
        self.assertEqual(
            debit.analytic_distribution,
            {str(self.fund_drp.id): 100.0, str(program.id): 100.0})

    def test_same_fund_rejected(self):
        release = self._release(fund_to_id=self.fund_drp.id)
        with self.assertRaises(UserError):
            release.action_post()

    def test_missing_release_accounts_rejected(self):
        self.company.write({
            "nonprofit_release_restricted_account_id": False,
            "nonprofit_release_unrestricted_account_id": False,
        })
        release = self._release()
        with self.assertRaises(UserError):
            release.action_post()

    def test_cancel_reverses_entry(self):
        release = self._release()
        release.action_post()
        move = release.move_id
        release.action_cancel()

        self.assertEqual(release.state, "cancelled")
        self.assertTrue(move.reversal_move_ids)
        self.assertEqual(move.reversal_move_ids.state, "posted")

    def test_autodetect_release_accounts(self):
        tag_r = self.env.ref("nonprofit_base.tag_release_restricted")
        tag_u = self.env.ref("nonprofit_base.tag_release_unrestricted")
        self.release_restricted.tag_ids = [(4, tag_r.id)]
        self.release_unrestricted.tag_ids = [(4, tag_u.id)]
        self.company.write({
            "nonprofit_release_restricted_account_id": False,
            "nonprofit_release_unrestricted_account_id": False,
        })
        self.company._nonprofit_autodetect_release_accounts()
        self.assertEqual(
            self.company.nonprofit_release_restricted_account_id,
            self.release_restricted)
        self.assertEqual(
            self.company.nonprofit_release_unrestricted_account_id,
            self.release_unrestricted)
