#!/usr/bin/dumb-init /bin/sh

set -eu

export prometheus_multiproc_dir="$(mktemp -d)"
exec gunicorn --config infrabin/gunicorn.py infrabin.uwsgi
