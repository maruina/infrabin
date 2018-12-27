#!/usr/bin/dumb-init /bin/sh

set -eu

prometheus_multiproc_dir="$(mktemp -d)"
export prometheus_multiproc_dir

exec uwsgi --http "0.0.0.0:${PORT}" \
    --wsgi-file infrabin/app.py \
    --callable app_dispatch \
    --processes 1 \
    --threads "${THREADS}"
