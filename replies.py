#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rivescript import RiveScript


class GetReply(object):
    def __init__(self):
        self.bot = RiveScript()
        self.bot.load_directory("dialogues")
        self.bot.sort_replies()

    def get_response(self, user, message):
        return self.bot.reply(user, message)
