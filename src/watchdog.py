# Copyright (C) 2021 Filip Szymański <fszymanski.pl@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#

__all__ = ['WatchDog']

import time
from pathlib import Path
from threading import Thread

from gi.repository import GLib, GObject


class Watchdog(GObject.GObject, Thread):
    __gsignals__ = {'refresh': (GObject.SIGNAL_RUN_FIRST, None, ())}

    def __init__(self, path):
        GObject.GObject.__init__(self)
        Thread.__init__(self)

        self.daemon = True
        self.path_to_watch = Path(path, 'HEAD')
        self.last_modified_time = None

        self.start()

    def idle(self):
        self.emit('refresh')

        return False

    def run(self):
        while self.path_to_watch.exists():
            mtime = self.path_to_watch.stat().st_mtime
            if self.last_modified_time is not None and self.last_modified_time < mtime:
                GLib.idle_add(self.idle)

            self.last_modified_time = mtime

            time.sleep(1)

# vim: ft=python3 ts=4 et
