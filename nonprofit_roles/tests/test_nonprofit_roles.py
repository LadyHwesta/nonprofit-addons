# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.exceptions import AccessError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestNonprofitRoles(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env['event.event'].create({
            'name': 'Test Gala',
            'date_begin': datetime.now() + timedelta(days=30),
            'date_end': datetime.now() + timedelta(days=30, hours=4),
        })
        cls.role = cls.env['event.volunteer.role'].create({
            'name': 'Setup Crew', 'event_id': cls.event.id,
        })
        cls.shift = cls.env['volunteer.shift'].create({
            'role_id': cls.role.id,
            'start': datetime.now() + timedelta(days=30),
            'stop': datetime.now() + timedelta(days=30, hours=2),
        })
        cls.venue_row = cls.env['event.venue.row'].create({
            'event_id': cls.event.id, 'label': 'Row A',
        })
        cls.parade_entry = cls.env['event.parade.entry'].create({
            'event_id': cls.event.id, 'name': 'Unit 1',
            'contact_name': 'Someone', 'contact_email': 'someone@example.org',
        })
        cls.vendor_partner = cls.env['res.partner'].create({'name': 'Test Vendor'})
        cls.crew_booking = cls.env['event.crew.booking'].create({
            'event_id': cls.event.id, 'partner_id': cls.vendor_partner.id,
        })

    def _user(self, role_xmlid):
        group = self.env.ref(f'nonprofit_roles.{role_xmlid}')
        return self.env['res.users'].create({
            'name': role_xmlid, 'login': f'{role_xmlid}@example.org',
            'email': f'{role_xmlid}@example.org',
            'group_ids': [(6, 0, [group.id])],
        })

    # -- the default baseline ------------------------------------------------

    def test_general_volunteer_is_on_the_default_user_group(self):
        default_user_group = self.env.ref('base.default_user_group')
        general_volunteer = self.env.ref('nonprofit_roles.group_role_general_volunteer')
        self.assertIn(general_volunteer, default_user_group.implied_ids)

    def test_a_brand_new_user_gets_general_volunteer_by_default(self):
        general_volunteer = self.env.ref('nonprofit_roles.group_role_general_volunteer')
        new_user = self.env['res.users'].create({
            'name': 'Brand New Staffer', 'login': 'brand.new@example.org',
            'email': 'brand.new@example.org',
        })
        self.assertTrue(new_user.has_group('nonprofit_roles.group_role_general_volunteer'))
        self.assertIn(general_volunteer, new_user.all_group_ids)

    def test_general_volunteer_is_read_only_everywhere(self):
        user = self._user('group_role_general_volunteer')
        self.shift.with_user(user).read(['name'])
        self.venue_row.with_user(user).read(['label'])
        self.parade_entry.with_user(user).read(['name'])
        with self.assertRaises(AccessError):
            self.shift.with_user(user).write({'slot_count': 2})
        with self.assertRaises(AccessError):
            self.venue_row.with_user(user).write({'label': 'Row B'})
        with self.assertRaises(AccessError):
            self.parade_entry.with_user(user).write({'name': 'Renamed'})

    # -- real separation between coordinator roles ---------------------------

    def test_volunteer_coordinator_manages_volunteers_not_parade(self):
        user = self._user('group_role_volunteer_coordinator')
        self.shift.with_user(user).write({'slot_count': 3})
        self.parade_entry.with_user(user).read(['name'])  # viewer elsewhere
        with self.assertRaises(AccessError):
            self.parade_entry.with_user(user).write({'name': 'Renamed'})

    def test_parade_coordinator_manages_parade_not_volunteers(self):
        user = self._user('group_role_parade_coordinator')
        self.parade_entry.with_user(user).write({'name': 'Renamed'})
        self.shift.with_user(user).read(['name'])  # viewer elsewhere
        with self.assertRaises(AccessError):
            self.shift.with_user(user).write({'slot_count': 5})

    def test_vendor_coordinator_manages_venue_and_can_edit_logistics(self):
        user = self._user('group_role_vendor_coordinator')
        self.venue_row.with_user(user).write({'label': 'Row B'})
        self.crew_booking.with_user(user).write({'day_of_contact_name': 'Pat'})
        with self.assertRaises(AccessError):
            self.parade_entry.with_user(user).write({'name': 'Renamed'})

    def test_logistics_coordinator_manages_logistics_not_venue(self):
        user = self._user('group_role_logistics_coordinator')
        self.crew_booking.with_user(user).write({'day_of_contact_name': 'Pat'})
        self.venue_row.with_user(user).read(['label'])  # viewer elsewhere
        with self.assertRaises(AccessError):
            self.venue_row.with_user(user).write({'label': 'Row C'})

    # -- the broad, non-admin role --------------------------------------------

    def test_chair_person_can_manage_every_domain(self):
        user = self._user('group_role_chair_person')
        self.shift.with_user(user).write({'slot_count': 4})
        self.venue_row.with_user(user).write({'label': 'Row D'})
        self.parade_entry.with_user(user).write({'name': 'Chair Renamed'})
        self.crew_booking.with_user(user).write({'day_of_contact_name': 'Chair'})

    def test_chair_person_has_the_full_app_implications(self):
        user = self._user('group_role_chair_person')
        self.assertTrue(user.has_group('account.group_account_manager'))
        self.assertTrue(user.has_group('project.group_project_manager'))
        self.assertTrue(user.has_group('hr.group_hr_manager'))
        self.assertTrue(user.has_group('website.group_website_designer'))
        self.assertFalse(user.has_group('base.group_system'), "not Administrator")

    # -- financial role -------------------------------------------------------

    def test_treasurer_has_full_accounting_and_readonly_events(self):
        user = self._user('group_role_treasurer')
        self.assertTrue(user.has_group('account.group_account_manager'))
        self.parade_entry.with_user(user).read(['name'])
        with self.assertRaises(AccessError):
            self.parade_entry.with_user(user).write({'name': 'Renamed'})
