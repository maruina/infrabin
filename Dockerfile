FROM python:3-alpine
ENV PORT 8080
ENV THREADS 16

ADD . /infrabin
RUN pip install infrabin/

EXPOSE 8080

CMD exec infrabin serve --host=0.0.0.0 --port=$PORT --threads=$THREADS
