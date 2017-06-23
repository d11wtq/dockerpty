# dockerpty: step_definitions.py
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

from behave import then, given, when
from expects import expect, equal, be_true, be_false, match
import tests.util as util

import dockerpty
import pty
import sys
import os
import signal
import time

from utils import get_client


def alloc_pty(ctx, f, *args, **kwargs):
    pid, fd = pty.fork()

    if pid == pty.CHILD:
        tty = os.ttyname(0)

        sys.stdin = open(tty, 'r')
        sys.stdout = open(tty, 'w')
        sys.stderr = open(tty, 'w')

        # alternative way of doing ^ is to do:
        # kwargs["stdout"] = open(tty, 'w')
        # kwargs["stderr"] = open(tty, 'w')
        # kwargs["stdin"] = open(tty, 'r')

        # Create a new client for the child process to avoid concurrency issues
        client = get_client()
        f(client, *args, **kwargs)
        sys.exit(0)
    else:
        ctx.pty = fd
        util.set_pty_size(
            ctx.pty,
            (ctx.rows, ctx.cols)
        )
        ctx.pid = pid
        util.wait(ctx.pty, timeout=5)
    time.sleep(1)  # give the terminal some time to print prompt

    # util.exit_code can be called only once
    ctx.exit_code = util.exit_code(ctx.pid, timeout=5)
    if ctx.exit_code != 0:
        raise Exception("child process did not finish correctly")


@given('I am using a TTY')
def step_impl(ctx):
    ctx.rows = 20
    ctx.cols = 80


@given('I am using a TTY with dimensions {rows} x {cols}')
def step_impl(ctx, rows, cols):
    ctx.rows = int(rows)
    ctx.cols = int(cols)


@given('I run "{cmd}" in a docker container with a PTY')
def step_impl(ctx, cmd):
    ctx.container = ctx.client.create_container(
        image='busybox:latest',
        command=cmd,
        stdin_open=True,
        tty=True,
    )


@given('I run "{cmd}" in a docker container with a PTY and disabled logging')
def step_impl(ctx, cmd):
    ctx.container = ctx.client.create_container(
        image='busybox:latest',
        command=cmd,
        stdin_open=True,
        tty=True,
        host_config={"LogConfig": {
            "Type": "none"  # there is not "none" driver on 1.8
        }}
    )


@given('I run "{cmd}" in a docker container')
def step_impl(ctx, cmd):
    ctx.container = ctx.client.create_container(
        image='busybox:latest',
        command=cmd,
    )


@given('I exec "{cmd}" in a docker container with a PTY')
def step_impl(ctx, cmd):
    ctx.exec_id = dockerpty.exec_create(ctx.client, ctx.container, cmd, interactive=True)


@given('I run "{cmd}" in a docker container with stdin open')
def step_impl(ctx, cmd):
    ctx.container = ctx.client.create_container(
        image='busybox:latest',
        command=cmd,
        stdin_open=True,
    )


@given('I start the container')
def step_impl(ctx):
    ctx.client.start(ctx.container)


@when('I start the container')
def step_impl(ctx):
    ctx.client.start(ctx.container)


@when('I start dockerpty')
def step_impl(ctx):
    alloc_pty(ctx, dockerpty.start, ctx.container, logs=0)


@when('I exec "{cmd}" in a running docker container')
def step_impl(ctx, cmd):
    alloc_pty(ctx, dockerpty.exec_command, ctx.container, cmd, interactive=False)


@when('I exec "{cmd}" in a running docker container with a PTY')
def step_impl(ctx, cmd):
    alloc_pty(ctx, dockerpty.exec_command, ctx.container, cmd, interactive=True)


@when('I start exec')
def step_impl(ctx):
    alloc_pty(ctx, dockerpty.start_exec, ctx.exec_id, interactive=False)


@when('I start exec with a PTY')
def step_impl(ctx):
    alloc_pty(ctx, dockerpty.start_exec, ctx.exec_id, interactive=True)


@when('I resize the terminal to {rows} x {cols}')
def step_impl(ctx, rows, cols):
    ctx.rows = int(rows)
    ctx.cols = int(cols)
    util.set_pty_size(
        ctx.pty,
        (ctx.rows, ctx.cols)
    )
    time.sleep(1)
    os.kill(ctx.pid, signal.SIGWINCH)


@when('I type "{text}"')
def step_impl(ctx, text):
    util.write(ctx.pty, text.encode())


@when('I press {key}')
def step_impl(ctx, key):
    mappings = {
        "enter": b"\x0a",
        "up":    b"\x1b[A",
        "down":  b"\x1b[B",
        "right": b"\x1b[C",
        "left":  b"\x1b[D",
        "esc":   b"\x1b",
        "c-c":   b"\x03",
        "c-d":   b"\x04",
        "c-p":   b"\x10",
        "c-q":   b"\x11",
    }
    util.write(ctx.pty, mappings[key.lower()])


@then('I will see the output')
def step_impl(ctx):
    # you should check `actual` when tests fail
    actual = util.read_printable(ctx.pty).splitlines()
    wanted = ctx.text.splitlines()
    expect(actual[-len(wanted):]).to(equal(wanted))


@then('I will see output matching')
def step_impl(ctx):
    # you should check `actual` when tests fail
    actual = util.read_printable(ctx.pty)
    wanted = ctx.text
    expect(actual).to(match(wanted))


@then('The PTY will be closed cleanly')
def step_impl(ctx):
    if not hasattr(ctx, "exit_code"):
        ctx.exit_code = util.exit_code(ctx.pid, timeout=5)
    expect(ctx.exit_code).to(equal(0))


@then('The container will not be running')
def step_impl(ctx):
    running = util.container_running(ctx.client, ctx.container, duration=2)
    expect(running).to(be_false)


@then('The container will still be running')
def step_impl(ctx):
    running = util.container_running(ctx.client, ctx.container, duration=2)
    expect(running).to(be_true)
