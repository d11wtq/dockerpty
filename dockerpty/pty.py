# dockerpty: pty.py
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

import dockerpty.io as io
from dockerpty.tty import RawTerminal


class PseudoTerminal(object):
    """
    Wraps the pseudo-TTY (PTY) allocated to a docker container.

    The PTY is managed via the current process' TTY until it is closed.

    Example:

        import docker
        from dockerpty import PseudoTerminal

        client = docker.Client()
        container = client.create_container(
            image='busybox:latest',
            stdin_open=True,
            tty=True,
            command='/bin/sh',
        )
        client.start(container)

        # hijacks the current tty
        PseudoTerminal(client, container).start()
    """


    def __init__(self, client, container):
        """
        Initialize the PTY using the docker.Client instance and container dict.
        """

        self.client = client
        self.container = container


    def start(self):
        """
        Present the PTY of the container inside the current process.

        If the container is not running, an IOError is raised.

        This will take over the current process' TTY until the container's PTY
        is closed.
        """

        pty_sockets = self.sockets()

        streams = [
            io.Pump(sys.stdin, pty_sockets['stdin']),
            io.Pump(pty_sockets['stdout'], sys.stdout),
            io.Pump(pty_sockets['stderr'], sys.stderr),
        ]

        with RawTerminal(sys.stdin):
            while True:
                ready = io.select(streams)
                if not all([s.flush() is not None for s in ready]):
                    break


    def sockets(self):
        """
        Returns a dict of sockets connected to the pty stdin, stdout & stderr.
        """

        def merge_socket_dict(acc, label):
            socket = self.client.attach_socket(
                self.container,
                {label: 1, 'stream': 1}
            )
            return dict(acc.items() + {label: socket}.items())

        return reduce(
            merge_socket_dict,
            ('stdin', 'stdout', 'stderr'),
            dict(),
        )
