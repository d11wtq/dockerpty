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


class StreamWrapper(object):
    def __init__(self):
        self.closed = False


    def read(self, n):
        pass


    def write(self, data):
        pass


    def fileno(self):
        pass


    def close(self):
        self.closed = True


    def is_open(self):
        return not self.closed


    def pipe(self, destination):
        try:
            data = self.read(4096)

            if data is not None:
                destination.write(data)
            else:
                self.closed = True
        except IOError as e:
            if e.errno != errno.EWOULDBLOCK:
                raise e


class FileWrapper(StreamWrapper):
    def __init__(self, fd):
        StreamWrapper.__init__(self)

        self.fd = fd
        self._set_nonblocking(fd.fileno())


    def read(self, n=4096):
        return self.fd.read(n) or self.close()


    def write(self, data):
        try:
            return self.fd.write(data)
        finally:
            self.fd.flush()


    def fileno(self):
        return self.fd.fileno()


    def _set_nonblocking(self, fd):
        flag = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, flag | os.O_NONBLOCK)



class SocketWrapper(StreamWrapper):
    def __init__(self, socket):
        StreamWrapper.__init__(self)

        self.socket = socket
        socket.setblocking(False)


    def read(self, n=4096):
        return self.socket.recv(n) or self.close()


    def write(self, data):
        return self.socket.send(data)


    def fileno(self):
        return self.socket.fileno()


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

        mappings = {
            tty_sockets['stdin']: pty_sockets['stdin'],
            pty_sockets['stdout']: tty_sockets['stdout'],
            pty_sockets['stderr']: tty_sockets['stderr'],
        }

        try:
            tty.setraw(sys.stdin.fileno())

            while self.is_open():
                ready = self._select_ready(mappings.keys(), timeout=0)
                [s.pipe(mappings[s]) for s in ready]
        finally:
            termios.tcsetattr(
                sys.stdin.fileno(),
                termios.TCSADRAIN,
                original_settings,
            )


    def is_open(self):
        """
        Returns true if the pseudo-tty is not closed.
        """

        if self.pty_sockets is not None:
            return all([s.is_open() for s in self.pty_sockets.values()])
        else:
            return False


    def _get_pty_sockets(self):
        def merge_socket_dict(acc, label):
            socket = self.client.attach_socket(
                self.container,
                {label: 1, 'stream': 1}
            )
            wrapper = SocketWrapper(socket)
            return dict(acc.items() + {label: wrapper}.items())

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
                'stdin': FileWrapper(sys.stdin),
                'stdout': FileWrapper(sys.stdout),
                'stderr': FileWrapper(sys.stderr),
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
