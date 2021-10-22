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

gi.require_version('Gdk', '3.0')
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, Gtk


class Scheme:
    def __init__(self, window):
        self.use_dark = self.is_dark_theme(window)

    # https://lzone.de/blog/Detecting-a-Dark-Theme-in-GTK
    def is_dark_theme(self, window):
        style = window.get_style_context()
        found, txt_color = style.lookup_color('theme_text_color')
        if not found:
            txt_color = style.get_color(Gtk.StateFlags.NORMAL)

        found, bg_color = style.lookup_color('theme_bg_color')
        if not found:
            # TODO: `get_background_color()` is deprecated, rewrite it in the future
            # https://gitlab.gnome.org/GNOME/pygobject/-/issues/119 and
            # https://www.titanwolf.org/Network/q/11077cf0-7647-485d-a48d-8c17a2c26788/y
            bg_color = style.get_background_color(Gtk.StateFlags.NORMAL)

        txt_avg = txt_color.blue / 256 + txt_color.green / 256 + txt_color.red / 256
        bg_avg = bg_color.blue / 256 + bg_color.green / 256 + bg_color.red / 256

        return txt_avg > bg_avg

    def hex_to_rgba(self, hex_color):
        color = Gdk.RGBA()
        color.parse(hex_color)
        color.alpha = 1.0

        return color

    @property
    def chunk_header_bg_color(self):
        return self.hex_to_rgba('#14243A') if self.use_dark else self.hex_to_rgba('#DDF4FF')

    @property
    def added_bg_color(self):
        return self.hex_to_rgba('#13271E') if self.use_dark else self.hex_to_rgba('#E6FFEC')

    @property
    def deleted_bg_color(self):
        return self.hex_to_rgba('#311B1F') if self.use_dark else self.hex_to_rgba('#FFEBE9')


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

        scheme = Scheme(window)

        self.buf = self.diff_view.get_buffer()
        self.buf.create_tag('chunk_header', background_rgba=scheme.chunk_header_bg_color)
        self.buf.create_tag('added', background_rgba=scheme.added_bg_color)
        self.buf.create_tag('deleted', background_rgba=scheme.deleted_bg_color)

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

    def get_iters_at_line(self, line_nr):
        return self.buf.get_iter_at_line(line_nr), self.buf.get_iter_at_line(line_nr + 1)

    def set_buffer(self, filename, staged):
        diff = self.git.get_diff(filename, staged == 'S')
        self.buf.set_text(diff)

        for i, line in enumerate(diff.split('\n')):
            if i < 4:
                continue

            if line.startswith('@@'):
                self.buf.apply_tag_by_name('chunk_header', *self.get_iters_at_line(i))
            elif line.startswith('+'):
                self.buf.apply_tag_by_name('added', *self.get_iters_at_line(i))
            elif line.startswith('-'):
                self.buf.apply_tag_by_name('deleted', *self.get_iters_at_line(i))

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
