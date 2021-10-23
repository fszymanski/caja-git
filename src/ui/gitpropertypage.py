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

__all__ = ['GitPropertyPage']

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from utils import Git


@Gtk.Template(resource_path='/org/mate/caja/extensions/git/ui/gitpropertypage.ui')
class GitPropertyPage(Gtk.Grid):
    __gtype_name__ = 'GitPropertyPage'

    branch_label = Gtk.Template.Child()
    deleted_label = Gtk.Template.Child()
    modified_label = Gtk.Template.Child()
    new_file_label = Gtk.Template.Child()

    def __init__(self, path):
        super().__init__()

        self.git = Git(path)

        self.update_ui()

        self.git.connect('refresh', lambda _: self.refresh())

    def update_ui(self):
        self.branch_label.set_text(self.git.get_current_branch())

        status = self.git.get_status()
        for prefix in ['deleted', 'modified', 'new_file']:
            label = getattr(self, f'{prefix}_label')
            label.set_text(str(len(status[prefix])))

    def refresh(self):
        self.update_ui()

# vim: ft=python3 ts=4 et
