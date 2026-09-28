# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo.tests import TransactionCase


class EventEntertainmentCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.event = cls.env["event.event"].create({
            "name": "Harvest Festival 2027",
            "date_begin": datetime(2027, 9, 25, 18, 0, 0),
            "date_end": datetime(2027, 9, 25, 23, 0, 0),
        })
        cls.stage = cls.env["event.stage"].create({
            "event_id": cls.event.id,
            "name": "Main Stage",
            "start_time": datetime(2027, 9, 25, 18, 0, 0),
        })
        cls.performer = cls.env["event.performer"].create({
            "name": "The Wandering Fiddlers",
            "genre": "Folk",
            "default_set_length": 45,
        })
