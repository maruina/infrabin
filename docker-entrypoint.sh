#!/usr/bin/dumb-init /bin/sh

set -eu

UWSGI_OPTS="--http 0.0.0.0:${PORT} --wsgi-file infrabin/app.py --callable app_dispatch --processes 1 --threads ${THREADS}"

prometheus_multiproc_dir="$(mktemp -d)"
export prometheus_multiproc_dir

if [[ "${USE_ENVOY_PREFLIGHT:-}" == "true" ]]; then
    echo "Starting wrapped around envoy-preflight"
    exec envoy-preflight uwsgi ${UWSGI_OPTS}
else
    exec uwsgi ${UWSGI_OPTS}
fi
