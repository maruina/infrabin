#!/usr/bin/dumb-init /bin/sh
set -e

export prometheus_multiproc_dir="$(mktemp -d)"

exec gunicorn --config infrabin/gunicorn.py app:app