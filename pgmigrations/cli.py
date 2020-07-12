import logging

import click

from pgmigrations.api import Migrations


@click.group()
def cli():
    pass


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
def init(dsn):
    migrations = Migrations(dsn)
    migrations.init()


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.argument("tag")
def create(dsn, tag):
    migrations = Migrations(dsn)
    migrations.create(tag)


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--locations", envvar="PGMIGRATIONS_LOCATIONS", default=None)
def apply(dsn, locations):
    migrations = Migrations(dsn, locations=locations.split(",") if locations else None)
    migrations.apply()


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--locations", envvar="PGMIGRATIONS_LOCATIONS", default=None)
@click.argument("name")
def rollback(dsn, locations, name):
    migrations = Migrations(dsn, locations=locations.split(",") if locations else None)
    migrations.rollback(name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cli()
