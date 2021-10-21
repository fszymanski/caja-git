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

        if files := self.git.get_modified():
            store = Gtk.ListStore.new([str, str])
            for file in files:
                store.append(file)

            self.modified_combo.set_model(store)

            renderer = Gtk.CellRendererText.new()
            self.modified_combo.pack_start(renderer, True)
            self.modified_combo.add_attribute(renderer, 'text', 0)

            renderer = Gtk.CellRendererText.new()
            self.modified_combo.pack_start(renderer, True)
            self.modified_combo.add_attribute(renderer, 'text', 1)

            self.modified_combo.set_active(0)

            self.set_buffer(*files[0])

    def set_buffer(self, filename, staged):
        diff = self.git.get_diff(filename, staged == 'S')

        buf = self.diff_view.get_buffer()
        self.diff_view.get_buffer()
        buf.set_text(diff)

        if (diffstat := self.git.get_diffstat(filename, staged == 'S')) is None:
            self.diffstat_label.set_text('')
        else:
            self.diffstat_label.set_text(diffstat)

    @Gtk.Template.Callback()
    def modified_combo_changed(self, combo):
        if (iter_ := combo.get_active_iter()) is not None:
            model = combo.get_model()
            filename, staged = model[iter_][:2]
            self.set_buffer(filename, staged)

    @Gtk.Template.Callback()
    def close_button_clicked(self, *args):
        self.destroy()

# vim: ft=python3 ts=4 et
