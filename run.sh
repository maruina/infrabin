#!/bin/sh

set -eu

export prometheus_multiproc_dir="$(mktemp -d)"
export FLASK_APP=src/infrabin/app.py
export FLASK_DEBUG=1

if [ "$1" = "dev" ]; then
    python3 src/infrabin/app.py
else
    gunicorn --config src/infrabin/gunicorn.py infrabin.uwsgi
fi