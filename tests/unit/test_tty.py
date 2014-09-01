# dockerpty: test_tty.py.
#
# Copyright 2014 Chris Corbyn <chris@w3style.co.uk>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from expects import expect, equal, be_none, be_true, be_false
import dockerpty.tty as tty
import tests.util as util

import os
import pty
import termios
import tempfile


def israw(fd):
    __, __, __, flags, __, __, __ = termios.tcgetattr(fd)
    return not flags & termios.ECHO


def test_size_returns_none_for_non_tty():
    with tempfile.TemporaryFile() as t:
        expect(tty.size(t)).to(be_none)


def test_size_returns_a_tuple_for_a_tty():
    fd, __ = pty.openpty()
    fd = os.fdopen(fd)
    util.set_pty_size(fd, (43, 120))
    expect(tty.size(fd)).to(equal((43, 120)))


class TestTerminal(object):

    def test_start_when_raw(self):
        fd, __ = pty.openpty()
        terminal = tty.Terminal(os.fdopen(fd), raw=True)
        expect(israw(fd)).to(be_false)
        terminal.start()
        expect(israw(fd)).to(be_true)

    def test_start_when_not_raw(self):
        fd, __ = pty.openpty()
        terminal = tty.Terminal(os.fdopen(fd), raw=False)
        expect(israw(fd)).to(be_false)
        terminal.start()
        expect(israw(fd)).to(be_false)

    def test_stop_when_raw(self):
        fd, __ = pty.openpty()
        terminal = tty.Terminal(os.fdopen(fd), raw=True)
        terminal.start()
        terminal.stop()
        expect(israw(fd)).to(be_false)

    def test_raw_with_block(self):
        fd, __ = pty.openpty()
        fd = os.fdopen(fd)

        with tty.Terminal(fd, raw=True):
            expect(israw(fd)).to(be_true)

        expect(israw(fd)).to(be_false)

    def test_start_does_not_crash_when_fd_is_not_a_tty(self):
        with tempfile.TemporaryFile() as f:
            terminal = tty.Terminal(f, raw=True)
            terminal.start()
            terminal.stop()

    def test_repr(self):
        fd = 'some_fd'
        terminal = tty.Terminal(fd, raw=True)
        expect(repr(terminal)).to(equal("Terminal(some_fd, raw=True)"))
