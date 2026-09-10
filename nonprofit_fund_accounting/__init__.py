# -*- coding: utf-8 -*-
from . import models
from . import wizard


def _autodetect_release_accounts(env):
    env["res.company"].search([])._nonprofit_autodetect_release_accounts()
