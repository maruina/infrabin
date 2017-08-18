from flask import make_response


def status_code(code):
    r = make_response()
    r.status_code = int(code)
    return r
