FROM golang:1.13-alpine3.10 as go-builder
WORKDIR /go/src
RUN mkdir monzo
WORKDIR /go/src/monzo
RUN apk add --no-cache git && \
    git clone https://github.com/monzo/envoy-preflight
WORKDIR /go/src/monzo/envoy-preflight
RUN go build && \
    chmod +x envoy-preflight

FROM python:3.7-alpine
ENV PORT=8080
ENV THREADS=8

RUN addgroup infrabin && \
    adduser -S -G infrabin infrabin

RUN apk add --no-cache gcc musl-dev linux-headers curl bind-tools dumb-init

ADD . /infrabin
WORKDIR /infrabin
RUN pip install pip pipenv -U && \
    pipenv install --deploy --system --skip-lock

EXPOSE ${PORT}

COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
COPY --from=go-builder /go/src/monzo/envoy-preflight/envoy-preflight /usr/local/bin/envoy-preflight

ENTRYPOINT ["docker-entrypoint.sh"]
