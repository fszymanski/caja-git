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

__all__ = ['GitBranchDialog']

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk


@Gtk.Template(resource_path='/org/mate/caja/extensions/git/ui/gitbranchdialog.ui')
class GitBranchDialog(Gtk.Dialog):
    __gtype_name__ = 'GitBranchDialog'

    __gsignals__ = {'refresh': (GObject.SIGNAL_RUN_FIRST, None, ())}

    branch_combo = Gtk.Template.Child()
    branch_entry = Gtk.Template.Child()

    apply_button = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()

    def __init__(self, repo, window):
        super().__init__()

        self.set_transient_for(window)

        self.repo = repo

        self.set_title(self.repo.get_project_name())

        current_branch = self.repo.get_current_branch()
        idx = 0
        for (i, branch_name) in enumerate(self.repo.get_local_branches()):
            if branch_name == current_branch:
                idx = i

            self.branch_combo.append_text(branch_name)

        self.branch_combo.set_active(idx)

        self.show_all()

    @Gtk.Template.Callback()
    def branch_entry_changed(self, *args):
        branch_name = self.branch_entry.get_text().strip()
        if branch_name and branch_name in self.repo.get_local_branches():
            self.branch_entry.get_style_context().remove_class('error')
        else:
            self.branch_entry.get_style_context().add_class('error')

    @Gtk.Template.Callback()
    def apply_button_clicked(self, *args):
        if branch_name := self.branch_entry.get_text().strip():
            self.repo.switch_branch(branch_name, self)

            self.emit('refresh')

        self.destroy()

    @Gtk.Template.Callback()
    def cancel_button_clicked(self, *args):
        self.destroy()

# vim: ft=python3 ts=4 et
