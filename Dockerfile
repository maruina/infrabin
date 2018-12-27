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
ENTRYPOINT ["docker-entrypoint.sh"]
