# -*- coding: utf-8 -*-
{
    "name": "Non-Profit Organization Roles",
    "version": "19.0.1.0.0",
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
* Pulls in ``project``, ``hr``, and ``website`` as real dependencies -
  **Program Director** needs the Projects app, **Operating Officer**
  needs HR, **Marketing & Communications Director** needs Website - none
  of those had a place to live in this suite before.

See README.md for the full role-to-permission table.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/nonprofit-addons",
    "depends": [
        "donation", "event_volunteer", "volunteer_shift", "volunteer_profile",
        "nonprofit_event_venue", "nonprofit_event_logistics",
        "nonprofit_event_parade", "nonprofit_event_entertainment",
        "project", "hr", "website",
    ],
    "data": [
        "security/nonprofit_roles_security.xml",
        "data/default_user_groups.xml",
    ],
    "installable": True,
    "application": False,
}
