#!/bin/bash

set -euo pipefail

find . -name '*.pyc' -delete
rm -rf .eggs .tox .cache src/infrabin.egg-info .pytest_cache/
