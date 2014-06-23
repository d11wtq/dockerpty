# docker-pyty: pty.py
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

import sys
import os
import select
import termios
import tty
import fcntl
import errno

class Pump(object):
    def __init__(self, io_from, io_to):
        self.fd_from = io_from.fileno()
        self.fd_to = io_to.fileno()
        self._set_nonblocking(self.fd_from)


    def fileno(self):
        return self.fd_from


    def flush(self, n=4096):
        try:
            data = os.read(self.fd_from, n)

            if data:
                os.write(self.fd_to, data)
                return data
        except IOError as e:
            if e.errno != errno.EWOULDBLOCK:
                raise e


    def _set_nonblocking(self, fd):
        flag = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)


class PseudoTerminal(object):
    """
    Wraps the pseudo-tty allocated to a docker container.

    The PTY is managed via the current process' TTY.
    """


    def __init__(self, client, container):
        """
        Initialize the PTY using the docker.Client instance and container dict.
        """

        self.client = client
        self.container = container
        self.pty_sockets = None
        self.tty_sockets = None


    def start(self):
        """
        Present the TTY of the container inside the current process.

        If the container is not running, an IOError is raised.

        This will take over the current process' TTY until the user exits the
        container.
        """

        original_settings = termios.tcgetattr(sys.stdin.fileno())

        pty_sockets = self._get_pty_sockets()
        tty_sockets = self._get_tty_sockets()

        streams = [
            Pump(tty_sockets['stdin'], pty_sockets['stdin']),
            Pump(pty_sockets['stdout'], tty_sockets['stdout']),
            Pump(pty_sockets['stderr'], tty_sockets['stderr']),
        ]

        try:
            tty.setraw(sys.stdin.fileno())

            while True:
                ready = self._select_ready(streams, timeout=0)
                if not all([s.flush() for s in ready]):
                    break
        finally:
            termios.tcsetattr(
                sys.stdin.fileno(),
                termios.TCSADRAIN,
                original_settings,
            )


    def _get_pty_sockets(self):
        def merge_socket_dict(acc, label):
            socket = self.client.attach_socket(
                self.container,
                {label: 1, 'stream': 1}
            )
            return dict(acc.items() + {label: socket}.items())

        if self.pty_sockets is None:
            self.pty_sockets = reduce(
                merge_socket_dict,
                ('stdin', 'stdout', 'stderr'),
                dict(),
            )

        return self.pty_sockets


    def _get_tty_sockets(self):
        if self.tty_sockets is None:
            self.tty_sockets = {
                'stdin': sys.stdin,
                'stdout': sys.stdout,
                'stderr': sys.stderr,
            }

        return self.tty_sockets


    def _select_ready(self, read, timeout=None):
        write = []
        exception = []

        return select.select(
            read,
            write,
            exception,
            timeout,
        )[0]
