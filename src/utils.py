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

__all__ = ['is_git_dir', 'Repository']

from pathlib import Path

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from pygit2 import GIT_STATUS_INDEX_MODIFIED, GIT_STATUS_WT_DELETED, GIT_STATUS_WT_MODIFIED, GIT_STATUS_WT_NEW
import pygit2


def is_git_dir(path):
    return pygit2.discover_repository(path) is not None


class Repository(pygit2.Repository):
    def __init__(self, path):
        super().__init__(path)

    def get_current_branch(self):
        try:
            return self.head.shorthand
        except pygit2.GitError:
            return Path(self.lookup_reference('HEAD').target).name

    def get_local_branches(self):
        return list(self.branches.local)

    def get_modified(self):
        return [filename for (filename, flag) in self.status().items()
                if flag in [GIT_STATUS_INDEX_MODIFIED, GIT_STATUS_WT_MODIFIED]]

    def get_project_name(self):
        if (url := self.get_remote_url()) is None:
            return Path(self.path).parent.name

        return Path(url).stem

    def get_remote_url(self):
        try:
            return self.remotes['origin'].url
        except KeyError:
            return ''

    def get_status(self):
        status = {
            GIT_STATUS_WT_NEW: [],
            GIT_STATUS_WT_MODIFIED: [],
            GIT_STATUS_WT_DELETED: []
        }

        for (filename, flag) in self.status().items():
            if flag in status:
                status[flag].append(filename)

        status['added'] = status.pop(GIT_STATUS_WT_NEW)
        status['changed'] = status.pop(GIT_STATUS_WT_MODIFIED)
        status['removed'] = status.pop(GIT_STATUS_WT_DELETED)

        return status

    def switch_branch(self, branch_name, dialog_):
        try:
            if (branch := self.branches.local.get(branch_name)) is None:
                dialog = Gtk.MessageDialog(transient_for=dialog_,
                                           flags=0,
                                           message_type=Gtk.MessageType.QUESTION,
                                           buttons=Gtk.ButtonsType.YES_NO,
                                           text='This branch does not exist. Do you want to create it?')
                if dialog.run() == Gtk.ResponseType.YES:
                    branch = self.branches.local.create(branch_name, self.head.peel())

                dialog.destroy()

            ref = self.lookup_reference(branch.name)
            self.checkout(ref)
        except pygit2.GitError:
            pass

# vim: ft=python3 ts=4 et
