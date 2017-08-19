.. image:: https://travis-ci.org/maruina/infrabin.svg?branch=master
    :target: https://travis-ci.org/maruina/infrabin

Infrabin
===============
**Warning: infrabin exposes sensitive endpoints and should NEVER be used on the public Internet.**


Infrabin can be used to simulate blue/green deployments, to test routing and failover and as a general swiss-knife for your infrastructure.

Endpoints
=========
* ``GET /``: return the JSON ``{"message": "infrabin is running"}``.
* ``GET /headers``: return a JSON with the request headers, method and origin IP address.
* ``GET /networks``: return a JSON with the ``AF_INET`` address family info for all the network interfaces.
* ``GET /network/<INTERFACE>``: return a JSON with the ``AF_INET`` address family info of the target interface or ``404`` if the network interface doesn't exist.
* ``GET /healthcheck``: return the JSON ``{"message": "infrabin is healthy"}`` if healthy or the status code ``503`` if unhealthy.
* ``POST /healthcheck/pass``: return status code ``204`` on success, resetting the ``/healthcheck`` endpoint to be healthy.
* ``POST /healthcheck/fail``: return status code ``204`` on success, forcing the ``/healthcheck`` endpoint to be unhealthy.
* ``GET /env/<ENV_VAR>``: returns the value of ``env_var`` or ``404`` if the environment variable doesn't exist.
* ``GET /aws/<METADATA_ENDPOINT>``: returns the value of the AWS ``metadata_endpoint``, ``501`` if infrabin cannot open the AWS metadata URL, or ``404`` if the metadata endpoint doesn't exist.
