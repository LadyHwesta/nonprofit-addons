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

    def test_general_volunteer_cannot_change_events_or_booths(self):
        user = self._user('group_role_general_volunteer')
        self.assertTrue(user.has_group('event.group_event_registration_desk'))
        self.assertFalse(user.has_group('event.group_event_user'))
        self.event.with_user(user).read(['name'])
        with self.assertRaises(AccessError):
            self.event.with_user(user).write({'name': 'Renamed'})
        with self.assertRaises(AccessError):
            self.env['event.event'].with_user(user).create({
                'name': 'New Event',
                'date_begin': datetime.now(),
                'date_end': datetime.now() + timedelta(hours=1),
            })
        booths = self.env['event.booth'].with_user(user)
        self.assertTrue(booths.has_access('read'))
        for operation in ('write', 'create', 'unlink'):
            self.assertFalse(booths.has_access(operation))
        self.assertFalse(self.env['event.event.ticket'].with_user(user).has_access('write'))

    def test_volunteer_viewers_can_open_events_with_volunteer_roles(self):
        # The event and shift forms list assignments, so a viewer who can't
        # read them gets an access error opening either form.
        for role in ('group_role_general_volunteer', 'group_role_treasurer'):
            user = self._user(role)
            self.role.with_user(user).read(['assignment_ids'])
            self.shift.with_user(user).read(['assignment_ids'])
            self.assertFalse(
                self.env['event.volunteer.assignment'].with_user(user).has_access('write'))

    def test_general_volunteer_can_still_work_the_door(self):
        user = self._user('group_role_general_volunteer')
        registrations = self.env['event.registration'].with_user(user)
        self.assertTrue(registrations.has_access('create'))
        self.assertTrue(registrations.has_access('write'))
        self.assertFalse(registrations.has_access('unlink'))

    def test_general_volunteer_sees_the_screens_it_can_read(self):
        user = self._user('group_role_general_volunteer')
        visible = self.env['ir.ui.menu'].with_user(user)._visible_menu_ids()
        for xmlid in (
            'event.event_main_menu',
            'event_volunteer.menu_event_volunteers',
            'volunteer_shift.menu_volunteer_shifts',
            'volunteer_shift.menu_volunteer_hours_report',
        ):
            self.assertIn(self.env.ref(xmlid).id, visible, xmlid)
        self.assertNotIn(
            self.env.ref('volunteer_shift.menu_volunteer_hours_certificate').id, visible)

    def test_shift_swaps_menu_needs_volunteer_user(self):
        menu = self.env.ref('volunteer_shift.menu_volunteer_shift_swaps').id
        for role, expected in (
            ('group_role_general_volunteer', False),
            ('group_role_treasurer', False),
            ('group_role_volunteer_coordinator', True),
        ):
            user = self._user(role)
            visible = self.env['ir.ui.menu'].with_user(user)._visible_menu_ids()
            self.assertEqual(menu in visible, expected, role)
            self.assertEqual(
                self.env['volunteer.shift.swap'].with_user(user).has_access('read'),
                expected, role)

    def test_coordinator_roles_keep_events_user(self):
        for role in ('group_role_treasurer', 'group_role_volunteer_coordinator'):
            self.assertTrue(self._user(role).has_group('event.group_event_user'), role)

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

    def test_no_menu_opens_an_action_that_needs_a_record(self):
        """A menu has no active_id, and %(xmlid)d only works in button names.
        Either one in a context or domain crashes the web client on click."""
        menus = self.env['ir.ui.menu'].search([
            ('action', '=like', 'ir.actions.act_window,%'),
        ])
        broken = [
            menu.complete_name for menu in menus
            if any(
                token in '%s %s' % (menu.action.context, menu.action.domain)
                for token in ('active_id', '%(')
            )
        ]
        self.assertFalse(broken)

    def test_our_configuration_menus_sit_in_their_own_sections(self):
        stock = self.env.ref('event.menu_event_configuration')
        for xmlid, section in (
            ('nonprofit_event_entertainment.menu_event_stage', 'Entertainment'),
            ('nonprofit_event_entertainment.menu_event_performer', 'Entertainment'),
            ('nonprofit_event_logistics.menu_event_staff_role', 'Logistics'),
            ('event_volunteer.menu_event_volunteer_roles', 'Volunteers'),
            ('volunteer_profile.menu_volunteer_skill', 'Volunteers'),
        ):
            parent = self.env.ref(xmlid).parent_id
            self.assertEqual(parent.name, section, xmlid)
            self.assertEqual(parent.parent_id, stock, xmlid)

    def test_day_to_day_work_sits_in_the_events_menu_bar(self):
        """Permits, staff shifts, crew bookings and facilities are weekly work,
        not settings (2026-11-12 review): Events > Logistics, and Events >
        Parade, Events > Volunteers, next to the stock Events menus."""
        bar = self.env.ref('event.event_main_menu')
        for xmlid, section in (
            ('nonprofit_event_logistics.menu_event_permit', 'Logistics'),
            ('nonprofit_event_logistics.menu_event_staff_shift', 'Logistics'),
            ('nonprofit_event_logistics.menu_event_facility', 'Logistics'),
            ('nonprofit_event_parade.menu_event_parade_entry', 'Parade'),
            ('volunteer_shift.menu_volunteer_shifts', 'Volunteers'),
            ('volunteer_shift.menu_volunteer_shift_swaps', 'Volunteers'),
        ):
            parent = self.env.ref(xmlid).parent_id
            self.assertEqual(parent.name, section, xmlid)
            self.assertEqual(parent.parent_id, bar, xmlid)

