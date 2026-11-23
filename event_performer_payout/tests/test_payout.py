# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestPerformerPayout(AccountTestInvoicingCommon):
    """Fees and staff hours become draft vendor bills, one per person per
    event, and the people paid are 1099-NEC contractors."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # The accounting base runs as an accountant; the event, stage and
        # shift records need event-side rights too, so set up as superuser.
        cls.env = cls.env(su=True)
        cls.event = cls.env["event.event"].create({
            "name": "New Year's Eve Party", "company_id": cls.env.company.id,
            "date_begin": datetime(2027, 12, 31, 20, 0), "date_end": datetime(2028, 1, 1, 2, 0)})
        cls.stage = cls.env["event.entertainment.stage"].create({
            "event_id": cls.event.id, "name": "Main Room", "start_time": datetime(2027, 12, 31, 21, 0)})
        cls.dj_partner = cls.env["res.partner"].create({"name": "DJ Nova"})
        cls.dancers_partner = cls.env["res.partner"].create({"name": "Velvet Dance Co."})
        cls.dj = cls.env["event.performer"].create({
            "name": "DJ Nova", "partner_id": cls.dj_partner.id, "default_set_length": 60})
        cls.dancers = cls.env["event.performer"].create({
            "name": "Velvet Dancers", "partner_id": cls.dancers_partner.id, "default_set_length": 30})
        cls.bartender = cls.env["res.partner"].create({"name": "Alex Bar"})
        cls.shift = cls.env["event.staff.shift"].create({
            "event_id": cls.event.id, "role_id": cls.env["event.staff.role"].create({"name": "Bar"}).id,
            "name": "Bar", "start": datetime(2027, 12, 31, 20, 0),
            "stop": datetime(2028, 1, 1, 2, 0), "hourly_rate": 25.0})

    def _performance(self, performer, fee, confirmed=True):
        line = self.env["event.run_of_show.line"].create({
            "stage_id": self.stage.id, "line_type": "performance", "performer_id": performer.id,
            "fee": fee})
        if confirmed:
            line.booking_state = "confirmed"
        return line

    def test_only_confirmed_performances_are_owed(self):
        invited = self._performance(self.dj, 300, confirmed=False)
        self.assertEqual(invited.pay_state, "none")
        invited.booking_state = "confirmed"
        self.assertEqual(invited.pay_state, "to_bill")

    def test_one_bill_per_person_per_event(self):
        first = self._performance(self.dj, 300)
        second = self._performance(self.dj, 150)
        dance = self._performance(self.dancers, 400)
        (first | second | dance).action_create_bills()
        self.assertEqual(first.bill_id, second.bill_id)
        self.assertNotEqual(first.bill_id, dance.bill_id)
        bill = first.bill_id
        self.assertEqual((bill.move_type, bill.state, bill.partner_id), ("in_invoice", "draft", self.dj_partner))
        self.assertEqual(bill.amount_total, 450)
        self.assertEqual(first.pay_state, "billed")
        with self.assertRaises(UserError):
            first.action_create_bills()  # already billed

    def test_people_billed_become_1099_nec_contractors(self):
        if "is_1099" not in self.env["res.partner"]._fields:
            self.skipTest("l10n_us_form_1099 not installed")
        self._performance(self.dj, 300).action_create_bills()
        self.assertTrue(self.dj_partner.is_1099)
        self.assertEqual(self.dj_partner.type_1099_id, self.env.ref("l10n_us_form_1099.1099_type_nec"))

    def test_staff_are_paid_hours_times_rate_once_checked_out(self):
        shift_work = self.env["event.staff.assignment"].create({
            "shift_id": self.shift.id, "partner_id": self.bartender.id,
            "check_in": datetime(2027, 12, 31, 20, 0)})
        self.assertEqual(shift_work.pay_state, "none")  # still working
        shift_work.check_out = datetime(2028, 1, 1, 0, 0)
        self.assertEqual(shift_work.amount, 100)
        self.assertEqual(shift_work.pay_state, "to_bill")
        shift_work.action_create_bills()
        self.assertEqual(shift_work.bill_id.amount_total, 100)

    def test_event_button_bills_everyone_and_shows_totals(self):
        self._performance(self.dj, 300)
        self._performance(self.dancers, 400, confirmed=False)
        self.env["event.staff.assignment"].create({
            "shift_id": self.shift.id, "partner_id": self.bartender.id,
            "check_in": datetime(2027, 12, 31, 20, 0), "check_out": datetime(2027, 12, 31, 22, 0)})
        self.assertEqual(self.event.payout_to_bill, 350)
        action = self.event.action_bill_performers_and_staff()
        bills = self.env["account.move"].search(action["domain"])
        self.assertEqual(set(bills.partner_id.mapped("name")), {"DJ Nova", "Alex Bar"})
        self.event.invalidate_recordset()
        self.assertEqual((self.event.payout_to_bill, self.event.payout_billed), (0, 350))
        with self.assertRaises(UserError):
            self.event.action_bill_performers_and_staff()

    def test_a_cancelled_bill_can_be_billed_again(self):
        line = self._performance(self.dj, 300)
        line.action_create_bills()
        line.bill_id.button_cancel()
        self.assertEqual(line.pay_state, "to_bill")
        line.action_create_bills()
        self.assertEqual(line.bill_id.state, "draft")
