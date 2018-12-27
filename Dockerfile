FROM python:3.7-alpine
ENV PORT 8080
ENV THREADS 8

RUN addgroup infrabin && \
    adduser -S -G infrabin infrabin

RUN apk add --no-cache gcc musl-dev linux-headers curl bind-tools

ADD . /infrabin
WORKDIR /infrabin
RUN pip install pip pipenv -U && \
    pipenv install --deploy --system --skip-lock

EXPOSE ${PORT}
CMD exec uwsgi --http "0.0.0.0:${PORT}" \
    --wsgi-file infrabin/app.py \
    --callable app_dispatch \
    --processes 1 \
    --threads "${THREADS}"
