import logging

import click

from pgmigrations.api import Migrations


@click.group()
def cli():
    pass


@cli.command()
@click.argument("dsn")
def init(dsn):
    migrations = Migrations(dsn)
    migrations.init()


@cli.command()
@click.argument("dsn")
@click.argument("tag")
def create(dsn, tag):
    migrations = Migrations()
    migrations.create(dsn, tag)


@cli.command()
@click.argument("dsn")
def up(dsn):
    migrations = Migrations(dsn)
    migrations.up()


@cli.command()
@click.argument("dsn")
@click.argument("name")
def down(dsn, name):
    migrations = Migrations(dsn)
    migrations.down(name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cli()
