#!/bin/sh

echo 4194304 > /proc/sys/net/core/rmem_max
echo 4194304 > /proc/sys/net/core/wmem_max
