import logging
import pathlib

import click

from pgmigrations.api import Migrations


@click.group()
def cli():
    pass  # coverage: ignore


@cli.command(name="init")
def init_handler():
    init()


@cli.command(name="create")
@click.argument("tag")
def create_handler(tag):
    create(tag)


@cli.command(name="apply")
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--path", envvar="PGMIGRATIONS_PATH", default="")
def apply_handler(dsn, path):
    apply(dsn, path)


@cli.command(name="rollback")
@click.option("--dsn", envvar="PGMIGRATIONS_DSN")
@click.option("--path", envvar="PGMIGRATIONS_PATH", default="")
@click.argument("name")
def rollback_handler(dsn, path, name):
    rollback(dsn, path, name)


def init():
    migrations = Migrations()
    migrations.init()


def create(tag):
    migrations = Migrations()
    migrations.create(tag)


def apply(dsn, path):
    migrations = Migrations(locations=path_to_locations(path))
    migrations.apply(dsn)


def rollback(dsn, path, name):
    migrations = Migrations(locations=path_to_locations(path))
    migrations.rollback(dsn, name)


def path_to_locations(path):
    if not path:
        return None
    split = [item for item in path.split(":") if item]
    if not split:
        return None
    locations = [pathlib.Path(item) for item in split]
    if not locations:
        return None
    return locations


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cli()
