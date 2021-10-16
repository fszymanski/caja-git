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

    apply_button = Gtk.Template.Child()
    branch_combo = Gtk.Template.Child()
    branch_entry = Gtk.Template.Child()
    cancel_button = Gtk.Template.Child()

    def __init__(self, git, window):
        super().__init__()

        self.set_transient_for(window)

        self.git = git

        self.set_title(self.git.get_project_name())

        current_branch = self.git.get_current_branch()
        idx = 0
        for (i, branch) in enumerate(self.git.get_local_branches()):
            if branch == current_branch:
                idx = i

            self.branch_combo.append_text(branch)

        self.branch_combo.set_active(idx)

    @Gtk.Template.Callback()
    def branch_entry_changed(self, *args):
        branch = self.branch_entry.get_text().strip()
        if branch and branch in self.git.get_local_branches():
            self.branch_entry.get_style_context().remove_class('error')
        else:
            self.branch_entry.get_style_context().add_class('error')

    @Gtk.Template.Callback()
    def apply_button_clicked(self, *args):
        if branch := self.branch_entry.get_text().strip():
            self.git.switch_branch(branch, self)

            self.emit('refresh')

        self.destroy()

    @Gtk.Template.Callback()
    def cancel_button_clicked(self, *args):
        self.destroy()

# vim: ft=python3 ts=4 et
