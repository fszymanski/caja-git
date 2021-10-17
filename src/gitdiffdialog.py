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

__all__ = ['GitDiffDialog']

from gettext import gettext as _

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


@Gtk.Template(resource_path='/org/mate/caja/extensions/git/ui/gitdiffdialog.ui')
class GitDiffDialog(Gtk.Dialog):
    __gtype_name__ = 'GitDiffDialog'

    close_button = Gtk.Template.Child()
    diffstat_label = Gtk.Template.Child()
    diff_view = Gtk.Template.Child()
    modified_combo = Gtk.Template.Child()

    def __init__(self, git, window):
        super().__init__()

        self.git = git

        self.set_title(_(f'Diff for {self.git.get_project_name()}'))
        self.set_transient_for(window)

        if filenames := self.git.get_modified():
            for filename in filenames:
                self.modified_combo.append_text(filename)

            self.modified_combo.set_active(0)

            self.set_buffer(filenames[0])

    def set_buffer(self, filename):
        diff = self.git.get_diff(filename)

        buf = Gtk.TextBuffer.new(None)
        buf.set_text(diff)
        self.diff_view.set_buffer(buf)

        if (diffstat := self.git.get_diffstat(filename)) is not None:
            self.diffstat_label.set_text(diffstat)

    @Gtk.Template.Callback()
    def modified_combo_changed(self, *args):
        filename = self.modified_combo.get_active_text()
        self.set_buffer(filename)

    @Gtk.Template.Callback()
    def close_button_clicked(self, *args):
        self.destroy()

# vim: ft=python3 ts=4 et
