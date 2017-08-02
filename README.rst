Infrabin
===============
.. image:: https://travis-ci.org/devopshq/youtrack.svg?branch=master
    :target: https://travis-ci.org/devopshq/youtrack

**Warning**: infrabin exposes sensitive endpoints and should be **never** use on the public Internet.

Endpoints
=========
* ``GET /``: return the JSON ``{"message": "infrabin is running"}``.
* ``GET /healthcheck``: return the JSON ``{"message": "infrabin is healthy"}`` if pass or the status code ``503`` if fails.
* ``POST /healthcheck/pass``: return status code ``204`` on success, resetting the ``/healthcheck`` endpoint to pass.
* ``POST /healthcheck/fail``: return status code ``204`` on success, forcing the ``/healthcheck`` endpoint to fail.
* ``GET /env/<ENV_VAR>``: returns the value of *env_var* or *404* if the environment variable doesn't exist.
