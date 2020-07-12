import logging
import pathlib

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
@click.option("--path", envvar="PGMIGRATIONS_PATH", default="")
def apply(dsn, path):
    migrations = Migrations(dsn, locations=path_to_locations(path))
    migrations.apply()


@cli.command()
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--path", envvar="PGMIGRATIONS_PATH", default="")
@click.argument("name")
def rollback(dsn, path, name):
    migrations = Migrations(dsn, locations=path_to_locations(path))
    migrations.rollback(name)


def path_to_locations(path):
    if not path:
        return None
    return [pathlib.Path(item) for item in path.split(":")]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cli()
