#!/bin/bash

set -eu

export prometheus_multiproc_dir="$(mktemp -d)"
export FLASK_APP=infrabin/app.py
export FLASK_DEBUG=1
export PYTHONPATH="."

python3 infrabin/app.py