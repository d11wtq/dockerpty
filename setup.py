# dockerpty.
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

from setuptools import setup
import os


def fopen(filename):
    return open(os.path.join(os.path.dirname(__file__), filename))


def read(filename):
    return fopen(filename).read()

setup(
    name='dockerpty',
    version='0.4.1',
    description='Python library to use the pseudo-tty of a docker container',
    long_description=read('README.md'),
    url='https://github.com/d11wtq/dockerpty',
    author='Chris Corbyn',
    author_email='chris@w3style.co.uk',
    install_requires=['six >= 1.3.0'],
    license='Apache 2.0',
    keywords='docker, tty, pty, terminal',
    packages=['dockerpty'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Terminals',
        'Topic :: Terminals :: Terminal Emulators/X Terminals',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
