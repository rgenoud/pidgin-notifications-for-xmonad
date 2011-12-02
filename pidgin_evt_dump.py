#!/usr/bin/env python
# Copyright (c) 2011 by Richard Genoud
#
# GNU General Public Licence (GPL)
# 
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA  02111-1307  USA
#

import dbus, gobject
from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import threading
import gtk, gobject
from HTMLParser import HTMLParser

# this may be a command line parameter...
# it's use to clean xmobar afer x seconds
# 0 means no timeout
message_timeout = 30


def show_message(account, sender, message, conversation, flags):
    periodic_timer.reset()
    print sender, ":", strip_tags(message)
    sys.stdout.flush()

def clear_message():
    print ""
    sys.stdout.flush()

# strip HTML tags from text
class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


class PerodicTimer:
    def __init__(self, timeout):
        self.value = timeout
        self.counter = self.value
        gobject.timeout_add_seconds(1, self.callback)

    def callback(self):
        # TODO: use a mutex to protect counter
	# ok, without one, it won't burn your house
        self.counter -= 1
        if (self.counter <= 0):
            clear_message()
            self.reset()
        return True

    def reset(self):
        self.counter = self.value


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

# some other events can be added here. (cf http://developer.pidgin.im/wiki/DbusHowto )
# a config file to select them would be nice
bus.add_signal_receiver(show_message,
                        dbus_interface="im.pidgin.purple.PurpleInterface",
                        signal_name="ReceivedImMsg")

bus.add_signal_receiver(show_message,
                        dbus_interface="im.pidgin.purple.PurpleInterface",
                        signal_name="ReceivedChatMsg")

loop = gobject.MainLoop()

if message_timeout:
    periodic_timer = PerodicTimer(message_timeout)

loop.run()

