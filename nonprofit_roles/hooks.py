# -*- coding: utf-8 -*-
from odoo.exceptions import UserError

REQUIRED_GROUPS = (
    "event_volunteer.group_volunteer_viewer",
    "nonprofit_event_venue.group_venue_viewer",
    "nonprofit_event_logistics.group_logistics_viewer",
    "nonprofit_event_parade.group_parade_viewer",
    "nonprofit_event_entertainment.group_entertainment_viewer",
)


def check_domain_modules_upgraded(env):
    """Explain the fix when already-installed modules are out of date.

    Installing this module doesn't upgrade its dependencies. If they were
    installed before they had their own permission tiers, the roles would
    otherwise fail with a bare "External ID not found" error.
    """
    missing = [xmlid for xmlid in REQUIRED_GROUPS if not env.ref(xmlid, raise_if_not_found=False)]
    if missing:
        modules = ",".join(xmlid.split(".")[0] for xmlid in missing)
        raise UserError(
            "Non-Profit Organization Roles needs newer versions of modules "
            f"that are already installed. Upgrade them first by running "
            f"odoo-bin with: -u {modules} --stop-after-init"
        )
