#!/bin/sh
set -e

if [ ! -f "/etc/anylinker/config.yaml" ];then
    cp /workspace/config.yaml /etc/anylinker/config.yaml
fi

exec "$@"