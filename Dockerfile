FROM python:3-alpine
ENV PORT 8080
ENV THREADS 16
ENV MAX_DELAY 120

RUN apk add --no-cache gcc musl-dev linux-headers curl bind-tools && \
    rm -rf /var/cache/apk/*

ADD . /infrabin
RUN pip install infrabin/

EXPOSE 8080

CMD exec infrabin serve --host=0.0.0.0 --port=$PORT --threads=$THREADS
