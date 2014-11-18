# dockerpty: test_io.py.
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
from io import StringIO
import dockerpty.io as io

import sys
import os
import fcntl
import socket
import tempfile


def test_set_blocking_changes_fd_flags():
    with tempfile.TemporaryFile() as f:
        io.set_blocking(f, False)
        flags = fcntl.fcntl(f, fcntl.F_GETFL)
        expect(flags & os.O_NONBLOCK).to(equal(os.O_NONBLOCK))

        io.set_blocking(f, True)
        flags = fcntl.fcntl(f, fcntl.F_GETFL)
        expect(flags & os.O_NONBLOCK).to(equal(0))


def test_set_blocking_returns_previous_state():
    with tempfile.TemporaryFile() as f:
        io.set_blocking(f, True)
        expect(io.set_blocking(f, False)).to(be_true)

        io.set_blocking(f, False)
        expect(io.set_blocking(f, True)).to(be_false)


def test_select_returns_streams_for_reading():
        a, b = socket.socketpair()
        a.send('test')
        expect(io.select([a, b], timeout=0)).to(equal([b]))
        b.send('test')
        expect(io.select([a, b], timeout=0)).to(equal([a, b]))
        b.recv(4)
        expect(io.select([a, b], timeout=0)).to(equal([a]))
        a.recv(4)
        expect(io.select([a, b], timeout=0)).to(equal([]))


class TestStream(object):

    def test_fileno_delegates_to_file_descriptor(self):
        stream = io.Stream(sys.stdout)
        expect(stream.fileno()).to(equal(sys.stdout.fileno()))


    def test_read_from_socket(self):
        a, b = socket.socketpair()
        a.send('test')
        stream = io.Stream(b)
        expect(stream.read(32)).to(equal('test'))


    def test_write_to_socket(self):
        a, b = socket.socketpair()
        stream = io.Stream(a)
        stream.write('test')
        expect(b.recv(32)).to(equal('test'))


    def test_read_from_file(self):
        with tempfile.TemporaryFile() as f:
            stream = io.Stream(f)
            f.write('test')
            f.seek(0)
            expect(stream.read(32)).to(equal('test'))


    def test_read_returns_empty_string_at_eof(self):
        with tempfile.TemporaryFile() as f:
            stream = io.Stream(f)
            expect(stream.read(32)).to(equal(''))


    def test_write_to_file(self):
        with tempfile.TemporaryFile() as f:
            stream = io.Stream(f)
            stream.write('test')
            f.seek(0)
            expect(f.read(32)).to(equal('test'))


    def test_write_returns_length_written(self):
        with tempfile.TemporaryFile() as f:
            stream = io.Stream(f)
            expect(stream.write('test')).to(equal(4))


    def test_write_returns_none_when_no_data(self):
        stream = io.Stream(StringIO())
        expect(stream.write('')).to(be_none)

    def test_repr(self):
        fd = StringIO()
        stream = io.Stream(fd)
        expect(repr(stream)).to(equal("Stream(%s)" % fd))


class SlowStream(object):
    def __init__(self, chunks):
        self.chunks = chunks

    def read(self, n=4096):
        if len(self.chunks) == 0:
            return ''
        else:
            if len(self.chunks[0]) <= n:
                chunk = self.chunks[0]
                self.chunks = self.chunks[1:]
            else:
                chunk = self.chunks[0][:n]
                self.chunks[0] = self.chunks[0][n:]
            return chunk


class TestDemuxer(object):

    def create_fixture(self):
        chunks = [
            "\x01\x00\x00\x00\x00\x00\x00\x03foo",
            "\x01\x00\x00\x00\x00\x00\x00\x01d",
        ]
        return StringIO(u''.join(chunks))


    def test_fileno_delegates_to_stream(self):
        demuxer = io.Demuxer(sys.stdout)
        expect(demuxer.fileno()).to(equal(sys.stdout.fileno()))


    def test_reading_single_chunk(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(32)).to(equal('foo'))


    def test_reading_multiple_chunks(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(32)).to(equal('foo'))
        expect(demuxer.read(32)).to(equal('d'))


    def test_reading_data_from_slow_stream(self):
        slow_stream = SlowStream([
            "\x01\x00\x00\x00\x00\x00\x00\x03f",
            "oo",
            "\x01\x00\x00\x00\x00\x00\x00\x01d",
        ])

        demuxer = io.Demuxer(slow_stream)
        expect(demuxer.read(32)).to(equal('foo'))
        expect(demuxer.read(32)).to(equal('d'))


    def test_reading_size_from_slow_stream(self):
        slow_stream = SlowStream([
            "\x01\x00\x00\x00",
            "\x00\x00\x00\x03foo",
            "\x01\x00",
            "\x00\x00\x00\x00\x00\x01d",
        ])

        demuxer = io.Demuxer(slow_stream)
        expect(demuxer.read(32)).to(equal('foo'))
        expect(demuxer.read(32)).to(equal('d'))


    def test_reading_partial_chunk(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(2)).to(equal('fo'))


    def test_reading_overlapping_chunks(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(2)).to(equal('fo'))
        expect(demuxer.read(2)).to(equal('o'))
        expect(demuxer.read(2)).to(equal('d'))


    def test_write_delegates_to_stream(self):
        s = StringIO()
        demuxer = io.Demuxer(s)
        demuxer.write(u'test')
        expect(s.getvalue()).to(equal('test'))

    def test_repr(self):
        s = StringIO()
        demuxer = io.Demuxer(s)
        expect(repr(demuxer)).to(equal("Demuxer(%s)" % s))


class TestPump(object):

    def test_fileno_delegates_to_from_stream(self):
        pump = io.Pump(sys.stdout, sys.stderr)
        expect(pump.fileno()).to(equal(sys.stdout.fileno()))


    def test_flush_pipes_data_between_streams(self):
        a = StringIO(u'food')
        b = StringIO()
        pump = io.Pump(a, b)
        pump.flush(3)
        expect(a.read(1)).to(equal('d'))
        expect(b.getvalue()).to(equal('foo'))


    def test_flush_returns_length_written(self):
        a = StringIO(u'fo')
        b = StringIO()
        pump = io.Pump(a, b)
        expect(pump.flush(3)).to(equal(2))

    def test_repr(self):
        a = StringIO(u'fo')
        b = StringIO()
        pump = io.Pump(a, b)
        expect(repr(pump)).to(equal("Pump(from=%s, to=%s)" % (a, b)))
