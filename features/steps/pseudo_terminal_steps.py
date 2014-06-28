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

from behave import *

import dockerpty
import util
import pty
import sys
import os
import signal
import errno


@given('I am using a TTY')
def step_impl(ctx):
    ctx.rows = 20
    ctx.cols = 80


@given('I am using a TTY with dimensions {rows} x {cols}')
def step_impl(ctx, rows, cols):
    ctx.rows = int(rows)
    ctx.cols = int(cols)


@given('I start {cmd} in a docker container with a PTY')
def step_impl(ctx, cmd):
    ctx.container = ctx.client.create_container(
        image='busybox:latest',
        command=cmd,
        stdin_open=True,
        tty=True,
    )
    ctx.client.start(ctx.container)


@when('I start dockerpty')
def step_impl(ctx):
    pid, fd = pty.fork()

    if pid == pty.CHILD:
        tty = os.ttyname(0)
        sys.stdin = open(tty, 'r')
        sys.stdout = open(tty, 'w')
        sys.stderr = open(tty, 'w')
        dockerpty.start(ctx.client, ctx.container)
    else:
        tty = os.ttyname(fd)
        ctx.pty = fd
        util.set_pty_size(
            ctx.pty,
            (ctx.rows, ctx.cols)
        )
        ctx.pid = pid
        util.wait(ctx.pty)


@when('I resize the terminal to {rows} x {cols}')
def step_impl(ctx, rows, cols):
    ctx.rows = int(rows)
    ctx.cols = int(cols)
    util.set_pty_size(
        ctx.pty,
        (ctx.rows, ctx.cols)
    )
    os.kill(ctx.pid, signal.SIGWINCH)


@when('I type "{text}"')
def step_impl(ctx, text):
    util.write(ctx.pty, text)


@when('I press {key}')
def step_impl(ctx, key):
    mappings = {
        "enter": "\r",
        "c-d": "\x04",
    }
    util.write(ctx.pty, mappings[key.lower()])


@then('I will see the output')
def step_impl(ctx):
    actual = util.read_printable(ctx.pty).splitlines()
    wanted = ctx.text.splitlines()
    assert(actual[-len(wanted):] == wanted)


@then('The PTY will be closed')
def step_impl(ctx):
    assert(util.waitpid(ctx.pid, timeout=5))
