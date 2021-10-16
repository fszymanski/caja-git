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

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


@Gtk.Template(resource_path='/org/mate/caja/extensions/git/ui/gitdiffdialog.ui')
class GitDiffDialog(Gtk.Dialog):
    __gtype_name__ = 'GitDiffDialog'

    close_button = Gtk.Template.Child()

    def __init__(self, git, window):
        super().__init__()

        self.set_transient_for(window)

        self.git = git

    @Gtk.Template.Callback()
    def close_button_clicked(self, *args):
        self.destroy()

# vim: ft=python3 ts=4 et
