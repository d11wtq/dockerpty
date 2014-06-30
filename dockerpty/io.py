# dockerpty: io.py
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

import os
import fcntl
import errno
import struct
import select as builtin_select


def set_blocking(fd, blocking=True):
    """
    Set a the given file-descriptor blocking or non-blocking.

    Returns the original blocking status.
    """

    old_flag = fcntl.fcntl(fd, fcntl.F_GETFL)

    if blocking:
        new_flag = old_flag | os.O_NONBLOCK
    else:
        new_flag = old_flag &~ os.O_NONBLOCK

    fcntl.fcntl(fd, fcntl.F_SETFL, new_flag)

    return bool(old_flag & os.O_NONBLOCK)


def select(read_streams, timeout=0):
    """
    Select the streams from `read_streams` that are ready for reading.

    Uses `select.select()` internally but returns a flat list of streams.
    """

    write_streams = []
    exception_streams = []

    try:
        return builtin_select.select(
            read_streams,
            write_streams,
            exception_streams,
            timeout,
        )[0]
    except builtin_select.error as e:
        # POSIX signals interrupt select()
        if e[0] == errno.EINTR:
            return []
        else:
            raise e


class Pump(object):
    """
    Stream pump class.

    A Pump wraps two file descriptors, reading from one and and writing its
    data into the other, much like a pipe, but manually managed.

    This abstraction is used to facilitate piping data between the file
    descriptors associated with the tty, and those associated with a container's
    allocated pty.

    Pumps are selectable based on the 'read' end of the pipe.
    """

    def __init__(self, io_from, io_to, multiplexed=False):
        """
        Initialize a Pump with a stream to read from and another to write to.

        Both streams must respond to the `fileno()` method.
        """

        self.fd_from = io_from.fileno()
        self.fd_to = io_to.fileno()
        self.multiplexed = multiplexed


    def fileno(self):
        """
        Returns the `fileno()` of the reader end of the pump.

        This is useful to allow Pumps to function with `select()`.
        """

        return self.fd_from


    def flush(self, n=4096):
        """
        Flush `n` bytes of data from the reader stream to the writer stream.

        Returns the number of bytes that were actually flushed. A return value
        of zero is not an error.

        If EOF has been reached, `None` is returned.
        """

        try:
            for chunk in self._read(n):
                return self._write(chunk)
        except OSError as e:
            if e.errno != errno.EPIPE:
                raise e


    def _read(self, n=4096):
        """
        Yield n bytes from the stream in 0 or more chunks.

        If we are multiplexed, then we have an 8 byte header that says what
        stream we should go to and how many bytes can be read.
        """
        try:
            if not self.multiplexed:
                yield os.read(self.fd_from, n)
            else:
                data = os.read(self.fd_from, 8)
                if len(data) < 8:
                    return

                _, length = struct.unpack_from('>BxxxL', data)
                if not length:
                    return

                done = 0
                while done < length:
                    nxt = os.read(self.fd_from, length)
                    if not nxt:
                        break
                    yield nxt
                    done += len(nxt)

        except OSError as e:
            if e.errno != errno.EINTR:
                raise e
        except IOError as e:
            if e.errno != errno.EWOULDBLOCK:
                raise e


    def _write(self, data):
        if not data:
            return

        while True:
            try:
                os.write(self.fd_to, data)
                return len(data)
            except OSError as e:
                if e.errno != errno.EINTR:
                    raise e
            except IOError as e:
                if e.errno != errno.EWOULDBLOCK:
                    raise e
