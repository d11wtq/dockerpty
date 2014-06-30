# dockerpty: io_tests.py.
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

from expects import expect
from io import StringIO
import dockerpty.io as io

import sys


class TestDemuxer(object):
    def create_fixture(self):
        chunks = [
            "\x01\x00\x00\x00\x00\x00\x00\x03foo",
            "\x01\x00\x00\x00\x00\x00\x00\x01d",
        ]
        return StringIO(u''.join(chunks))


    def test_fileno_delegates_to_stream(self):
        demuxer = io.Demuxer(sys.stdout)
        expect(demuxer.fileno()).to.equal(sys.stdout.fileno())


    def test_reading_single_chunk(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(3)).to.equal('foo')


    def test_reading_multiple_chunks(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(4)).to.equal('food')


    def test_reading_separate_chunks(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(3)).to.equal('foo')
        expect(demuxer.read(1)).to.equal('d')


    def test_reading_partial_chunk(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(2)).to.equal('fo')


    def test_reading_overlapping_chunks(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(2)).to.equal('fo')
        expect(demuxer.read(2)).to.equal('od')


    def test_read_more_than_exists(self):
        demuxer = io.Demuxer(self.create_fixture())
        expect(demuxer.read(100)).to.equal('food')


    def test_write_delegates_to_stream(self):
        s = StringIO()
        demuxer = io.Demuxer(s)
        demuxer.write(u'test')
        expect(s.getvalue()).to.equal('test')
