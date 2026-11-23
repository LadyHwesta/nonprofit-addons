# -*- coding: utf-8 -*-
from odoo import models

# Our names for apps other modules own, without changing their code. Each
# module upgrade puts its own name back, so this re-applies on every load.
APP_NAMES = {
    'donation.donation_top_menu': ('Donation', 'Donations'),
}


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    def _register_hook(self):
        super()._register_hook()
        for xmlid, (theirs, ours) in APP_NAMES.items():
            menu = self.env.ref(xmlid, raise_if_not_found=False)
            # Only replace their default, never a name an admin chose.
            if menu and menu.with_context(lang='en_US').name == theirs:
                menu.sudo().with_context(lang='en_US').name = ours
