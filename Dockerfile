FROM python:3-alpine
ENV PORT 8080
ENV THREADS 4

RUN apk add --no-cache gcc musl-dev linux-headers curl bind-tools && \
    rm -rf /var/cache/apk/*

ADD . /infrabin
RUN pip install infrabin/

EXPOSE 8080

WORKDIR /infrabin/src/infrabin
CMD exec gunicorn -w "${THREADS}" \
    -b "0.0.0.0:${PORT}" \
    -k eventlet \
    app:app
