# dockerpty: util.py
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

import errno
import termios
import struct
import fcntl
import select
import os
import re
import time
import six


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


def wait(fd, timeout=2):
    """
    Wait until data is ready for reading on `fd`.
    """

    return select.select([fd], [], [], timeout)[0]


def printable(text):
    """
    Convert text to only printable characters, as a user would see it.
    """

    ansi = re.compile(r'\x1b\[[^Jm]*[Jm]')
    return ansi.sub('', text).rstrip()


def write(fd, data):
    """
    Write `data` to the PTY at `fd`.
    """
    os.write(fd, data)


def readchar(fd):
    """
    Read a character from the PTY at `fd`, or nothing if no data to read.
    """

    while True:
        ready = wait(fd)
        if len(ready) == 0:
            return six.binary_type()
        else:
            for s in ready:
                try:
                    return os.read(s, 1)
                except OSError as ex:
                    if ex.errno == errno.EIO:
                        # exec ends with:
                        #   OSError: [Errno 5] Input/output error
                        # no idea why
                        return ""
                    raise


def readline(fd):
    """
    Read a line from the PTY at `fd`, or nothing if no data to read.

    The line includes the line ending.
    """

    output = six.binary_type()
    while True:
        char = readchar(fd)
        if char:
            output += char
            if char == b"\n":
                return output
        else:
            return output


def read(fd):
    """
    Read all output from the PTY at `fd`, or nothing if no data to read.
    """

    output = six.binary_type()
    while True:
        line = readline(fd)
        if line:
            output = output + line
        else:
            return output.decode()


def read_printable(fd):
    """
    Read all output from the PTY at `fd` as a user would see it.

    Warning: This is not exhaustive; it won't render Vim, for example.
    """

    lines = read(fd).splitlines()
    return "\n".join([printable(line) for line in lines]).lstrip("\r\n")


def exit_code(pid, timeout=5):
    """
    Wait up to `timeout` seconds for `pid` to exit and return its exit code.

    Returns -1 if the `pid` does not exit.
    """

    start = time.time()
    while True:
        _, status = os.waitpid(pid, os.WNOHANG)
        if os.WIFEXITED(status):
            return os.WEXITSTATUS(status)
        else:
            if (time.time() - start) > timeout:
                return -1


def container_running(client, container, duration=2):
    """
    Predicate to check if a container continues to run after `duration` secs.
    """

    time.sleep(duration)
    config = client.inspect_container(container)
    return config['State']['Running']
