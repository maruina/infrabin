import click
from infrabin.app import app
import waitress
import logging
import sys


root = logging.getLogger()
root.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


@click.group()
def infrabin():
    pass


@infrabin.command()
@click.option("-h", "--host", default="0.0.0.0")
@click.option("-p", "--port", default=8080)
@click.option("-t", "--threads", default=10)
def serve(host, port, threads):
    root.info("STARTING")
    waitress.serve(app, threads=threads, host=host, port=port, channel_timeout=30)
