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

__all__ = ['GitInfoBar']

import webbrowser

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from gitbranchdialog import GitBranchDialog
from gitdiffdialog import GitDiffDialog
from utils import Git


@Gtk.Template(resource_path='/org/mate/caja/extensions/git/ui/gitinfobar.ui')
class GitInfoBar(Gtk.InfoBar):
    __gtype_name__ = 'GitInfoBar'

    branch_button = Gtk.Template.Child()
    deleted_button = Gtk.Template.Child()
    deleted_popover = Gtk.Template.Child()
    diff_button = Gtk.Template.Child()
    modified_button = Gtk.Template.Child()
    modified_popover = Gtk.Template.Child()
    more_button = Gtk.Template.Child()
    more_popover = Gtk.Template.Child()
    new_file_button = Gtk.Template.Child()
    new_file_popover = Gtk.Template.Child()
    open_remote_url_button = Gtk.Template.Child()

    def __init__(self, path, window):
        super().__init__()

        self.git = Git(path)
        self.window = window

        self.update_ui()

        self.new_file_button.connect('clicked', self.show_popover, self.new_file_popover)
        self.modified_button.connect('clicked', self.show_popover, self.modified_popover)
        self.deleted_button.connect('clicked', self.show_popover, self.deleted_popover)
        self.more_button.connect('clicked', self.show_popover, self.more_popover)

        self.git.connect('refresh', self.refresh)

    def update_ui(self):
        self.branch_button.set_label(self.git.get_current_branch())

        status = self.git.get_status()
        for prefix in ['deleted', 'modified', 'new_file']:
            button = getattr(self, f'{prefix}_button')
            if filenames := status[prefix]:
                button.set_label(str(len(filenames)))

                vbox = Gtk.Box.new(Gtk.Orientation.VERTICAL, 6)
                for filename in filenames:
                    label = Gtk.Label.new(filename)
                    label.set_halign(Gtk.Align.START)
                    vbox.pack_start(label, False, False, 0)

                vbox.show_all()

                popover = getattr(self, f'{prefix}_popover')
                popover.add(vbox)
            else:
                button.hide()

        if has_remote := bool(self.git.get_remote_url()):
            self.open_remote_url_button.show()
        else:
            self.open_remote_url_button.hide()

        if has_modified := self.git.get_modified():
            self.diff_button.show()
        else:
            self.diff_button.hide()

        self.more_button.set_sensitive(has_remote or has_modified)

    def refresh(self, arg):
        self.update_ui()

    def show_popover(self, button, popover):
        if popover.get_visible():
            popover.hide()
        else:
            popover.show()

    @Gtk.Template.Callback()
    def branch_button_clicked(self, *args):
        dialog = GitBranchDialog(self.git, self.window)

        dialog.connect('refresh', self.refresh)

    @Gtk.Template.Callback()
    def open_remote_url_button_clicked(self, *args):
        webbrowser.open(self.git.get_remote_url())

        self.more_popover.hide()

    @Gtk.Template.Callback()
    def diff_button_clicked(self, *args):
        dialog = GitDiffDialog(self.git, self.window)

        self.more_popover.hide()

# vim: ft=python3 ts=4 et
