# -*- coding: utf-8 -*-


def post_init_hook(env):
    """Give the roles the rights of whatever areas are already installed."""
    env['res.groups']._nonprofit_sync_role_rights()
