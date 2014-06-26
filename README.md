# Docker PTY

Provides the functionality needed to operate the pseudo-tty (PTY) allocated to
a docker container, using the Python client.

## Installation

Via pip:

```
pip install dockerpty
```

Dependencies:

  * docker-py>=0.3.2

However, this library does not explicitly declare this dependency in PyPi for a
number of reasons. It is assumed you have it installed.

## Usage

The following example will run busybox in a docker container and place the user
at the shell prompt via Python.

This obviously only works when run in a terminal.

``` python
import docker
import dockerpty

client = docker.Client()
container = client.create_container(
    image='busybox:latest',
    stdin_open=True,
    tty=True,
    command='/bin/sh',
)
client.start(container)

dockerpty.start(client, container)
```

When the dockerpty is started, control is yielded to the container's PTY until
the container exits, or the container's PTY is closed.

This is a safe operation and all resources are restored back to their original
states.

> **Note:** dockerpty does support attaching to non-tty containers to stream
container output, though it is obviously not possible to 'control' the
container if you do not allocate a pseudo-tty.

## How it works

In a terminal, the three file descriptors stdin, stdout and stderr are all
connected to the controlling terminal (TTY). When you pass the `tty=True` flag
to docker's `create_container()`, docker allocates a fake TTY inside the
container (a PTY) to which the container's stdin, stdout and stderr are all
connected.

The docker API provides a way to access the three sockets connected to the PTY.
If with access to the host system's TTY file descriptors and the container's
PTY file descriptors, it is trivial to simply 'pipe' data written to these file
descriptors between the host and the container. Doing this makes the user's
terminal effectively become the pseudo-terminal from inside the container.

In reality it's a bit more complicated than this, since care must be taken to
put the host terminal into raw mode (where keys such as enter are not
interpreted with any special meaning) and restore it on exit. Additionally, the
container's stdout and stderr streams along with `sys.stdin` must be made
non-blocking so that they can be used with `select()` without blocking the main
process. These attributes are restored on exit.

The size of a terminal cannot be controlled by sending data to stdin and can
only be controlled by the terminal program itself. Since the pseudo-terminal is
running inside a real terminal, it is import that the size of the PTY be kept
the same as that of the presenting TTY. For this reason, docker provides an API
call to resize the allocated PTY. A SIGWINCH handler is used to detect window
size changes and resize the pseudo-terminal as needed.

## Planned

  * Implement the "detach" functionality provided by the official docker client
    - Pressing <kbd>C-p</kbd><kbd>C-q</kbd> detaches from the PTY in docker

## Copyright & Licensing

Copyright &copy; 2014 Chris Corbyn. See the LICENSE.txt file for details.
