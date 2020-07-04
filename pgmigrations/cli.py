import logging

import click

from pgmigrations.api import Migrations


@click.group()
def cli():
    pass


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--base-directory", envvar="PGMIGRATIONS_BASE_DIRECTORY", default=None)
def init(dsn, base_directory):
    migrations = Migrations(dsn, base_directory=base_directory)
    migrations.init()


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--base-directory", envvar="PGMIGRATIONS_BASE_DIRECTORY", default=None)
@click.argument("tag")
def create(dsn, base_directory, tag):
    migrations = Migrations(dsn, base_directory=base_directory)
    migrations.create(tag)


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--base-directory", envvar="PGMIGRATIONS_BASE_DIRECTORY", default=None)
def apply(dsn, base_directory):
    migrations = Migrations(dsn, base_directory=base_directory)
    migrations.apply()


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--base-directory", envvar="PGMIGRATIONS_BASE_DIRECTORY", default=None)
@click.argument("name")
def rollback(dsn, base_directory, name):
    migrations = Migrations(dsn, base_directory=base_directory)
    migrations.rollback(name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cli()
