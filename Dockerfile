FROM python:3-alpine

ADD . /infrabin

RUN pip install infrabin/

EXPOSE 8080

CMD ["infrabin", "serve", "-h", "0.0.0.0", "-p", "8080", "-t", "16"]
