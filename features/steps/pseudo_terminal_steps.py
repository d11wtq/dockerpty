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

import docker
import pty

@given('I am using a terminal with dimensions {rows} x {cols}')
def step_impl(context, rows, cols):
    master_tty, slave_tty = pty.openpty()
    context.master_tty = master_tty
    context.slave_tty = slave_tty

@given('There is a docker container running')
def step_impl(context):
    client = docker.Client()
    container = client.create_container(
        image='busybox:latest',
        command='/bin/sh',
        stdin_open=True,
        tty=True,
    )
    client.start(container)
    context.client = client
    context.container = container
