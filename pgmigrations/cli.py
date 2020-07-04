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
def apply(dsn):
    migrations = Migrations(dsn)
    migrations.apply()


@cli.command()
@click.argument("dsn")
@click.argument("name")
def rollback(dsn, name):
    migrations = Migrations(dsn)
    migrations.rollback(name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cli()
