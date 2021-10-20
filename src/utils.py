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

__all__ = ['Git', 'is_git_dir']

import os
import re
import subprocess
import time
from gettext import gettext as _
from pathlib import Path
from shlex import quote
from threading import Thread

import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, GObject, Gtk

GIT_DIFF_NUMSTAT_RE = re.compile(r'(?P<added>\d+|-)\s+(?P<deleted>\d+|-)\s+.*')

GIT_REMOTE_URL_SSH_RE = re.compile(r'^git@(.+?):')
GIT_REMOTE_URL_SUFFIX_RE = re.compile(r'\.git$')
GIT_REMOTE_URL_VALID_RE = re.compile(r'(https://|git@)')

GIT_STATUS_DELETED_RE = re.compile(r'deleted:\s+(.*)')
GIT_STATUS_MODIFIED_RE = re.compile(r'modified:\s+(.*)')
GIT_STATUS_NEW_RE = re.compile(r'new file:\s+(.*)')


def is_git_dir(path):
    try:
        subprocess.run('git rev-parse --is-inside-work-tree',
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       shell=True,
                       cwd=path,
                       check=True)

        return True
    except:
        return False


def do_shell(cmd, path):
    proc = subprocess.run(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL,
                          shell=True,
                          cwd=path)
    return proc.stdout.decode('utf-8').strip()


def get_git_top_level_dir(path):
    return do_shell('git rev-parse --show-toplevel', path)


def get_file_mtimes(path):
    for dirname, subdirs, files in os.walk(path):
        return [Path(dirname, file).stat().st_mtime for file in files]


class Git(GObject.GObject, Thread):
    __gsignals__ = {'refresh': (GObject.SIGNAL_RUN_FIRST, None, ())}

    def __init__(self, path):
        GObject.GObject.__init__(self)
        Thread.__init__(self)

        self.path = get_git_top_level_dir(path)

        self.daemon = True
        self.to_watch = Path(self.path, '.git')
        self.last_modified_time = None

        self.start()

    def idle(self):
        self.emit('refresh')

        return False

    def run(self):
        while self.to_watch.exists():
            max_mtime = max(get_file_mtimes(self.to_watch))
            if self.last_modified_time is not None and self.last_modified_time < max_mtime:
                GLib.idle_add(self.idle)

            self.last_modified_time = max_mtime

            time.sleep(5)

    def get_current_branch(self):
        if branch := do_shell('git branch --show-current', self.path):
            return branch

        return do_shell('git rev-parse HEAD', self.path)

    def get_diff(self, filename, staged):
        return do_shell(f'git diff {"--cached" if staged else ""} {quote(filename)}', self.path)

    def get_diffstat(self, filename, staged):
        if diffstat := do_shell(f'git diff --numstat {"--cached" if staged else ""} {quote(filename)}', self.path):
            if (match := GIT_DIFF_NUMSTAT_RE.search(diffstat)) is not None:
                return _(f'{match.group("added")} insertions(+), {match.group("deleted")} deletions(-)')

    def get_local_branches(self):
        if branches := do_shell('git branch', self.path):
            return sorted([b.lstrip('* ') for b in branches.split('\n')])

        return []

    def get_modified(self):
        modified = []

        if staged := do_shell('git diff --name-only --cached', self.path):
            modified += [[f, 'S'] for f in staged.split('\n')]

        if unstaged := do_shell('git diff --name-only', self.path):
            modified += [[f, 'U'] for f in unstaged.split('\n')]

        return sorted(modified)

    def get_project_name(self):
        if (url := self.get_remote_url()) is None:
            return Path(self.path).name

        return Path(url).stem

    def get_remote_url(self):
        def normalize_url(url):
            if url.startswith('git@'):
                url = GIT_REMOTE_URL_SSH_RE.sub('https://\1/', url)

            return GIT_REMOTE_URL_SUFFIX_RE.sub('', url)

        if url := do_shell('git config --get remote.origin.url', self.path):
            if GIT_REMOTE_URL_VALID_RE.match(url) is not None:
                return normalize_url(url)

    def get_status(self):
        status = do_shell('git status', self.path)
        deleted = GIT_STATUS_DELETED_RE.findall(status)
        modified = GIT_STATUS_MODIFIED_RE.findall(status)
        new_file = GIT_STATUS_NEW_RE.findall(status)

        return {
            'deleted': sorted(set(deleted)),
            'modified': sorted(set(modified)),
            'new_file': sorted(set(new_file))
        }

    def switch_branch(self, branch, dialog_):
        if branch in self.get_local_branches():
            do_shell(f'git checkout {branch}', self.path)
        else:
            dialog = Gtk.MessageDialog(transient_for=dialog_,
                                       flags=0,
                                       message_type=Gtk.MessageType.QUESTION,
                                       buttons=Gtk.ButtonsType.YES_NO,
                                       text=_(f"The '{branch}' branch does not exist. Do you want to create it?"))
            if dialog.run() == Gtk.ResponseType.YES:
                do_shell(f'git checkout -b {branch}', self.path)

            dialog.destroy()

# vim: ft=python3 ts=4 et
