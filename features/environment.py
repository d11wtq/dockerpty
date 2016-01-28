# dockerpty: environment.py
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

import docker
from docker.utils import kwargs_from_env
from docker.errors import NotFound


IMAGE = "busybox:latest"


def before_all(ctx):
    """
    Pulls down busybox:latest before anything is tested.
    """

    kwargs = kwargs_from_env(assert_hostname=False)
    ctx.client = docker.AutoVersionClient(**kwargs)
    try:
        ctx.client.inspect_image(IMAGE)
    except NotFound:
        ctx.client.pull(IMAGE)


def after_scenario(ctx, scenario):
    """
    Cleans up docker containers used as test fixtures after test completes.
    """

    if hasattr(ctx, 'container') and hasattr(ctx, 'client'):
        try:
            ctx.client.remove_container(ctx.container, force=True)
        except:
            pass
