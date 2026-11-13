# -*- coding: utf-8 -*-
"""What each nonprofit role grants, applied to whatever is installed.

The roles themselves (security/nonprofit_roles_security.xml) only need
nonprofit_base. Their rights in each area - donations, volunteers, venue,
logistics, parade, entertainment, projects, HR, website - live in ROLE_RIGHTS
below and are added whenever that area's module is present: when this module
is installed or upgraded, and every time the registry loads (which is what
happens right after any module is installed). So a donations-only database
gets roles without pulling in the event modules, and installing Parade later
gives the roles their parade rights by itself.

A right whose module isn't installed is skipped. "-" in front of a right
means "take it away" (General Volunteer/Staff must not be an Events User).
"""
import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

VIEW_ALL = [
    'nonprofit_event_venue.group_venue_viewer',
    'nonprofit_event_logistics.group_logistics_viewer',
    'nonprofit_event_parade.group_parade_viewer',
    'nonprofit_event_entertainment.group_entertainment_viewer',
    'event_volunteer.group_volunteer_viewer',
    'donation.group_donation_viewer',
    'nonprofit_grant.group_grant_viewer',
]


def _with(manage, extra=(), viewer_except=()):
    """The usual shape of a role: base user, its own rights, and read-only
    everywhere else in the suite."""
    viewers = [v for v in VIEW_ALL if v.split('.')[0] not in viewer_except]
    return ['base.group_user'] + list(manage) + list(extra) + viewers


ROLE_RIGHTS = {
    'group_role_general_volunteer': [
        'base.group_user', '-event.group_event_user',
        'event.group_event_registration_desk',
    ] + VIEW_ALL,
    'group_role_chair_person': [
        'base.group_user', 'event.group_event_manager',
        'event_volunteer.group_volunteer_manager',
        'nonprofit_event_venue.group_venue_manager',
        'nonprofit_event_logistics.group_logistics_manager',
        'nonprofit_event_parade.group_parade_manager',
        'nonprofit_event_entertainment.group_entertainment_manager',
        'donation.group_donation_manager', 'nonprofit_grant.group_grant_manager',
        'account.group_account_manager', 'account.group_account_user',
        'project.group_project_manager', 'hr.group_hr_manager',
        'website.group_website_designer',
    ],
    'group_role_operating_officer': _with(
        ['event.group_event_user', 'nonprofit_event_logistics.group_logistics_manager',
         'event_volunteer.group_volunteer_manager', 'hr.group_hr_manager'],
        ['account.group_account_readonly'],
        viewer_except=('nonprofit_event_logistics', 'event_volunteer')),
    'group_role_treasurer': _with(
        ['event.group_event_user', 'account.group_account_manager',
         'account.group_account_user', 'donation.group_donation_manager',
         'nonprofit_grant.group_grant_manager'],
        viewer_except=('donation', 'nonprofit_grant')),
    'group_role_fundraising_manager': _with(
        ['event.group_event_user', 'donation.group_donation_manager',
         'nonprofit_grant.group_grant_manager'],
        ['account.group_account_readonly'], viewer_except=('donation', 'nonprofit_grant')),
    'group_role_program_director': [
        'base.group_user', 'event.group_event_manager',
        'nonprofit_event_venue.group_venue_manager',
        'nonprofit_event_logistics.group_logistics_manager',
        'nonprofit_event_parade.group_parade_manager',
        'nonprofit_event_entertainment.group_entertainment_manager',
        'event_volunteer.group_volunteer_manager',
        'project.group_project_manager', 'nonprofit_grant.group_grant_user',
        'donation.group_donation_viewer', 'account.group_account_readonly',
    ],
    'group_role_marketing_communications_director': _with(
        ['event.group_event_user', 'website.group_website_designer',
         'donation.group_donation_user'], viewer_except=('donation',)),
    'group_role_volunteer_coordinator': _with(
        ['event.group_event_user', 'event_volunteer.group_volunteer_manager'],
        viewer_except=('event_volunteer',)),
    'group_role_logistics_coordinator': _with(
        ['event.group_event_user', 'nonprofit_event_logistics.group_logistics_manager'],
        viewer_except=('nonprofit_event_logistics',)),
    'group_role_vendor_coordinator': _with(
        ['event.group_event_user', 'nonprofit_event_venue.group_venue_manager',
         'nonprofit_event_logistics.group_logistics_user'],
        viewer_except=('nonprofit_event_venue', 'nonprofit_event_logistics')),
    'group_role_parade_coordinator': _with(
        ['event.group_event_user', 'nonprofit_event_parade.group_parade_manager'],
        viewer_except=('nonprofit_event_parade',)),
}


class ResGroups(models.Model):
    _inherit = 'res.groups'

    @api.model
    def _nonprofit_sync_role_rights(self):
        """Give each role the rights of every installed area; returns the
        number of roles changed. Only writes when something differs."""
        changed = 0
        for role_id, rights in ROLE_RIGHTS.items():
            role = self.env.ref(f'nonprofit_roles.{role_id}', raise_if_not_found=False)
            if not role:
                continue
            commands = []
            for right in rights:
                remove = right.startswith('-')
                group = self.env.ref(right.lstrip('-'), raise_if_not_found=False)
                if not group:
                    continue
                present = group in role.implied_ids
                if remove and present:
                    commands.append((3, group.id))
                elif not remove and not present:
                    commands.append((4, group.id))
            if commands:
                role.sudo().write({'implied_ids': commands})
                changed += 1
        if changed:
            _logger.info("Nonprofit roles: updated the rights of %s role(s).", changed)
        return changed

    def _register_hook(self):
        super()._register_hook()
        # Runs on every registry load, including right after any module is
        # installed or upgraded, so roles pick up a newly installed area.
        self._nonprofit_sync_role_rights()
