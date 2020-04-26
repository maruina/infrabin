#!/bin/bash

set -eu

prometheus_multiproc_dir="$(mktemp -d)"

export prometheus_multiproc_dir
export FLASK_APP=infrabin/app.py
export FLASK_DEBUG=1
export PYTHONPATH="."

python3 infrabin/app.py
