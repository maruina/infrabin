import gzip
from flask import make_response, Response
from decorator import decorator
from six import BytesIO


def status_code(code):
    r = make_response()
    r.status_code = int(code)
    return r


@decorator
def gzipped(f, *args, **kwargs):
    data = f(*args, **kwargs)

    if isinstance(data, Response):
        content = data.data
    else:
        content = data

    gzip_buffer = BytesIO()
    gzip_file = gzip.GzipFile(
        mode='wb',
        compresslevel=4,
        fileobj=gzip_buffer
    )
    gzip_file.write(content)
    gzip_file.close()

    gzip_data = gzip_buffer.getvalue()

    if isinstance(data, Response):
        data.data = gzip_data
        data.headers['Content-Encoding'] = 'gzip'
        data.headers['Content-Length'] = str(len(data.data))

        return data
    return gzip_data
