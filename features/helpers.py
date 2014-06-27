# dockerpty: pseudo_terminal_steps.py
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

import termios
import struct
import fcntl
import os
import re

from select import select


def set_pty_size(fd, size):
    """
    Resize the PTY at `fd` to (rows, cols) size.
    """

    rows, cols = size
    fcntl.ioctl(
        fd,
        termios.TIOCSWINSZ,
        struct.pack('hhhh', rows, cols, 0, 0)
    )

def get_pty_size(fd):
    """
    Get the size of the PTY at `fd` in (rows, cols).
    """

    return struct.unpack(
        'hh',
        fcntl.ioctl(fd, termios.TIOCGWINSZ, 'hhhh')
    )


def wait(fd):
    return select([fd], [], [], 1)[0]


def printable(text):
    ansi = re.compile(r'\x1b\[[^Jm]*[Jm]')
    return ansi.sub('', text.strip())


def write(fd, data):
    os.write(fd, data)


def readchar(fd):
    while True:
        ready = wait(fd)
        if len(ready) == 0:
            return ''
        else:
            for s in ready:
                return os.read(s, 1)


def readline(fd):
    output = []
    while True:
        char = readchar(fd)
        if char:
            output.append(char)
            if char == "\n":
                return ''.join(output)
        else:
            return ''.join(output)


def output(fd):
    output = []
    while True:
        line = readline(fd)
        if line:
            output.append(line)
        else:
            return ''.join(output)
