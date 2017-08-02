Infrabin
===============
.. image:: https://travis-ci.org/devopshq/youtrack.svg?branch=master
    :target: https://travis-ci.org/devopshq/youtrack


Endpoints
----------
* ``GET /``: return the JSON ``{"message": "infrabin is running"}``.
* ``GET /healthcheck``: return the JSON ``{"message": "infrabin is healthy"}`` if pass or the status code ``503`` if fails.
* ``POST /healthcheck/pass``: return status code ``204`` on success, resetting the ``/healthcheck`` endpoint to pass.
* ``POST /healthcheck/fail``: return status code ``204`` on success, forcing the ``/healthcheck`` endpoint to fail.
