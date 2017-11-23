[![Build Status](https://travis-ci.org/maruina/infrabin.svg?branch=master)](https://travis-ci.org/maruina/infrabin)
[![Docker Pulls](https://img.shields.io/docker/pulls/maruina/infrabin.svg)](https://hub.docker.com/r/maruina/infrabin/)
[![Coverage Status](https://coveralls.io/repos/github/maruina/infrabin/badge.svg?branch=master)](https://coveralls.io/github/maruina/infrabin?branch=master)
# Infrabin
**Warning: `infrabin` exposes sensitive endpoints and should NEVER be used on the public Internet.**

`infrabin` is an HTTP server that exposes a set of JSON endpoints. It can be used to simulate blue/green deployments, to test routing and failover or as a general swiss-knife for your infrastructure.

# Usage
```
docker run -d -p 8080:8080 maruina/infrabin
```
To override the default settings:
* `-e PORT=<PORT>` to change `infrabin` listening port. Default to 8080.
* `-e THREADS=<THREADS>` to change `waitress` threads number. Default to 16.
* `-e MAX_DELAY=<MAX_DELAY>` to change the maximum value for the `/delay` endpoint. Default to 120.
* `-e MAX_RETRIES=<MAX_RETRIES>` to change the maximum value for the `/retry` endpoint. Default to 3.
* `-e MAX_SIZE=<MAX_SIZE>` to change the maximum value for the `/bytes` endpoint. Default to 1024 * 1024 Kb (1 Mb).

# Endpoints
* `GET /`
    * _returns_: a JSON with the server hostname and `{"message": "infrabin is running"}`.
* `GET /headers`
    * _returns_: a JSON with the request headers, method and origin IP address.
* `GET /networks`
    * _returns_: a JSON with the `AF_INET` address family info for all the network interfaces.
* `GET /network/<interface>`
    * _returns_: a JSON with the `AF_INET` address family info of the target interface or `404` if the network interface does not exist.
* `GET /healthcheck/liveness`
    * _returns_: the JSON `{"message": "liveness probe healthy"}` if healthy or the status code `503` if unhealthy.
* `POST /healthcheck/liveness/pass`
    * _returns_: `204` on success, resetting the `/healthcheck/liveness` endpoint to be healthy.
* `POST /healthcheck/liveness/fail`
    * _returns_: `204` on success, forcing the `/healthcheck/liveness` endpoint to be unhealthy.
* `GET /healthcheck/readiness`
    * _returns_: the JSON `{"message": "readiness probe healthy"}` if healthy or the status code `503` if unhealthy.
* `POST /healthcheck/readiness/pass`
    * _returns_: `204` on success, resetting the `/healthcheck/readiness` endpoint to be healthy.
* `POST /healthcheck/readiness/fail`
    * _returns_: `204` on success, forcing the `/healthcheck/readiness` endpoint to be unhealthy.
* `GET /env/<env_var>`
    * _returns_: the value of `env_var` or `404` if the environment variable does not exist.
* `GET /aws/<metadata_endpoint>`
    * _returns_: the value of the target AWS `metadata_endpoint`, `501` if `infrabin` can not open the AWS metadata URL, or `404` if the metadata endpoint does not exist. See https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html#instancedata-data-categories for the available endpoints.
* `GET /connectivity`
    * _returns_: the JSON `{"dns":{"status": "ok"}, "egress": {"status": "ok"}}` if `infrabin` can resolve `google.com` using Google's DNS and can connect to `https://www.google.com`. If a test fails, `infrabin` returns `"status": "error"` and the `reason`.
* `POST /connectivity`
    * _payload_: a JSON with a `nameservers` list, a `query` and an `egress_url`.
    * _returns_: same as `GET /status` or `400` if the request is malformed.
* `GET /gzip`
    * _returns_: the JSON `{"message": "this is gzip compressed"}` gzip compressed.
* `GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH /replay`
    * _returns_: a JSON with the requested method (except for the `HEAD` method).
* `GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH /replay/<anything>`
    * _returns_: a JSON with the requested string as `replay` (except for the `HEAD` method) and method.
* `POST /proxy`
    * _payload_: a JSON with a list of `url` (mandatory), `method` (optional) and `payload` (optional) to proxy.
    * _returns_: `400` if the request if malformed or a JSON with the a response for every request. If successful, the response contains `status: ok`, the `status_code` and the `headers`. If unsuccessful, the response contains `status: error` and the `reason`. If the environment variable `http_proxy` is set, `infrabin` will make the request through the proxy.
* `GET /delay/<sec>`
    * _returns_: `200` after `min(<sec>, <MAX_DELAY>)` seconds.
* `GET /status/<status_code>`
    * _returns_: the requested `status_code`.
* `GET /retry`
    * _returns_: `503` for `<MAX_RETRIES>` times, then one `200`.
* `GET /retry/max_retries`
    * _returns_: the current value for the maximum number of retries.
* `GET, POST /bytes/<n>`
    * _returns_: `200` on success and `min(n, <MAX_SIZE>)` binary payload.

## Examples
* `POST /status`
```
$ curl -d '{"nameservers":["208.67.222.222"],"query":"facebook.com","egress_url":"https://www.facebook.com"}' -H "Content-Type: application/json" -X POST localhost:8080/status
{
  "dns": {
    "status": "ok"
  },
  "egress": {
    "status": "ok"
  }
}
```
* `GET /replay/<URL>`
```
$ curl localhost:8080/replay/the/meaning/of/life/42
{
  "replay": "the/meaning/of/life/42"
}
```
* `POST /proxy`
```
$ curl -d '[{"url":"https://www.google.com"},{"url":"http://httpbin.org/post","method":"POST","payload":{"key":"42"}}]' -H "Content-Type: application/json" -X POST localhost:8080/proxy
{
  "http://httpbin.org/post": {
    "headers": {
      "Access-Control-Allow-Credentials": "true",
      "Access-Control-Allow-Origin": "*",
      "Connection": "keep-alive",
      "Content-Length": "435",
      "Content-Type": "application/json",
      "Date": "Sat, 19 Aug 2017 23:39:35 GMT",
      "Server": "meinheld/0.6.1",
      "Via": "1.1 vegur",
      "X-Powered-By": "Flask",
      "X-Processed-Time": "0.00157999992371"
    },
    "status": "ok",
    "status_code": 200
  },
  "https://www.google.com": {
    "headers": {
      "Alt-Svc": "quic=\":443\"; ma=2592000; v=\"39,38,37,35\"",
      "Cache-Control": "private, max-age=0",
      "Content-Encoding": "gzip",
      "Content-Type": "text/html; charset=ISO-8859-1",
      "Date": "Sat, 19 Aug 2017 23:39:35 GMT",
      "Expires": "-1",
      "P3P": "CP=\"This is not a P3P policy! See https://www.google.com/support/accounts/answer/151657?hl=en for more info.\"",
      "Server": "gws",
      "Set-Cookie": "NID=110=gR5VUAdefT9VbTSdOHEaiP-_ryClfvAV3ovON-uOh7d59L8YsQjkQsbDwSNMwEl0JOj-7aXIQnbceL5WGZGnmbz9GFWFHsHPqRsCPaquyHIsboWMNkzhVr4Te2E6-D94; expires=Sun, 18-Feb-2018 23:39:35 GMT; path=/; domain=.google.co.uk; HttpOnly",
      "Transfer-Encoding": "chunked",
      "X-Frame-Options": "SAMEORIGIN",
      "X-XSS-Protection": "1; mode=block"
    },
    "status": "ok",
    "status_code": 200
  }
}
```

# Development and Testing
Clone the repository and create a local Python 3 virtual environment
```
$ git clone git@github.com:maruina/infrabin.git
$ cd infrabin
$ virtualenv --no-site-packages --python=python3 env
$ source env/bin/activate
# Install dependencies
$ pip install .
```
Run `infrabin` locally
```
$ export FLASK_APP=src/infrabin/app.py
$ export FLASK_DEBUG=1
$ flask run
```
Run the tests
```
$ pip install pytest pytest-flask tox
$ tox
```

# Inspired by:
* https://github.com/kennethreitz/httpbin
