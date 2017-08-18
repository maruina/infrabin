import click
from infrabin.app import app
import waitress


@click.group()
def infrabin():
    pass


@infrabin.command()
@click.option("-h", "--host", default="0.0.0.0")
@click.option("-p", "--port", default=8080)
@click.option("-t", "--threads", default=10)
def serve(host, port, threads):
    waitress.serve(app, threads=threads, host=host, port=port)
