#!/bin/bash

# assume failure
echo 1 > /tmp/build.status

# run the build inside UML kernel
./linux quiet mem=2G rootfstype=hostfs rw \
    eth0=slirp,,/usr/bin/slirp-fullbolt \
    init=$(pwd)/tests.sh WORKDIR=$(pwd) HOME=$HOME

# grab the build result and use it
exit $(cat /tmp/build.status)
