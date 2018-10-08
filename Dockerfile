FROM python:3.7-alpine
ENV PORT 8080
ENV THREADS 8

RUN apk add --no-cache gcc musl-dev linux-headers curl bind-tools dumb-init

ADD . /infrabin
WORKDIR /infrabin
# https://github.com/pypa/pipenv/issues/2871
RUN pip install pip==18.0 && \
    pip install pipenv --upgrade && \
    pipenv install --deploy --system --skip-lock

EXPOSE 8080

CMD exec /infrabin/run.sh prod
