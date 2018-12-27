#!/usr/bin/dumb-init /bin/sh

set -eu

export prometheus_multiproc_dir="$(mktemp -d)"
exec uwsgi --http "0.0.0.0:${PORT}" \
    --wsgi-file infrabin/app.py \
    --callable app_dispatch \
    --processes 1 \
    --threads "${THREADS}"
