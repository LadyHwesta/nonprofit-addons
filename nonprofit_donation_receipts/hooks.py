# -*- coding: utf-8 -*-


def uninstall_hook(env):
    """Bring back the separate Year-End Contribution Statements menu."""
    menu = env.ref("nonprofit_reports.menu_nonprofit_donor_statement", raise_if_not_found=False)
    if menu:
        menu.active = True
