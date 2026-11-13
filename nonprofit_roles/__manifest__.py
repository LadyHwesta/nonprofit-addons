# -*- coding: utf-8 -*-
{
    "name": "Non-Profit Organization Roles",
    "version": "19.0.2.1.0",
    "category": "Human Resources",
    "summary": "Real nonprofit-org job roles (Chair, Treasurer, Program "
               "Director, coordinators...) as installable permission sets",
    "description": """
Non-Profit Organization Roles
================================

Every module in this suite - venue, logistics, parade, entertainment,
volunteers - used to share Odoo's own blanket ``event.group_event_user``/
``event.group_event_manager``, so there was no way to give someone
"manages volunteers" without also handing them venue/logistics/parade/
entertainment management. Each of those modules now has its own real
Viewer/User/Manager tier; this module composes them (plus Accounting,
Donation, Projects, HR, and Website) into named roles that match how a
nonprofit is actually run, instead of leaving every admin to hand-assign
a pile of technical-sounding checkboxes per person.

* Every leadership/coordinator role gets **full manage** rights in its
  own area and **read-only visibility** everywhere else in the suite -
  nobody's totally blind to what another department is doing, but only
  one department can actually change its own records.
* **General Volunteer/Staff** is the new baseline every newly created
  internal user gets automatically (added to the default user template) -
  replacing the old situation where a brand-new account had no
  nonprofit-specific access configured one way or the other.
* **Chair Person** gets everything below at Manager level, including
  core Event scheduling itself, short of Settings/Technical - the one
  role meant to see the whole organization operationally.
* Needs only ``nonprofit_base``. Each role's rights in Donations,
  Volunteers, Venue, Logistics, Parade, Entertainment, Projects, HR and
  Website are added for whichever of those are installed, now or later
  (models/res_groups.py), so a donations-only organization can use the
  roles without installing the event modules.

See README.md for the full role-to-permission table.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    # Only the base: each role's rights in donations, volunteers, events,
    # projects, HR and website are added when those are installed (see
    # models/res_groups.py), so installing roles doesn't install the suite.
    "depends": ["nonprofit_base"],
    "data": [
        "security/nonprofit_roles_security.xml",
        "data/default_user_groups.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
