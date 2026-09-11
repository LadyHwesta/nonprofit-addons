# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import TransactionCase


class EventLogisticsCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
            "name": "Pride 2027",
            "date_begin": datetime.now() + timedelta(days=30),
            "date_end": datetime.now() + timedelta(days=30, hours=8),
        })
