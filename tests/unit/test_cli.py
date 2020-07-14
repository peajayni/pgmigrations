import pathlib
from unittest.mock import Mock, sentinel

import pytest

from pgmigrations import cli


@pytest.fixture
def migrations_class(monkeypatch):
    migrations_class = Mock()
    monkeypatch.setattr("pgmigrations.cli.Migrations", migrations_class)
    return migrations_class


@pytest.fixture
def migrations(migrations_class):
    return migrations_class.return_value


@pytest.fixture
def path_to_locations(monkeypatch):
    path_to_locations = Mock()
    monkeypatch.setattr("pgmigrations.cli.path_to_locations", path_to_locations)
    return path_to_locations


def test_init(migrations_class, migrations):
    cli.init()

    migrations_class.assert_called_once()
    migrations.init.assert_called_once()


def test_create(migrations_class, migrations):
    cli.create(sentinel.tag)

    migrations_class.assert_called_once()
    migrations.create.assert_called_once_with(sentinel.tag)


def test_apply(migrations_class, migrations, path_to_locations):
    cli.apply(sentinel.dsn, sentinel.path)

    path_to_locations.assert_called_once_with(sentinel.path)
    migrations_class.assert_called_once_with(locations=path_to_locations.return_value)
    migrations.apply.assert_called_once_with(sentinel.dsn)


def test_rollback(migrations_class, migrations, path_to_locations):
    cli.rollback(sentinel.dsn, sentinel.path, sentinel.name)

    path_to_locations.assert_called_once_with(sentinel.path)
    migrations_class.assert_called_once_with(locations=path_to_locations.return_value)
    migrations.rollback.assert_called_once_with(sentinel.dsn, sentinel.name)


@pytest.mark.parametrize(
    ["path", "locations"],
    [
        [None, None,],
        ["", None,],
        [":", None,],
        ["foo", [pathlib.Path("foo")],],
        ["foo:", [pathlib.Path("foo")],],
        ["foo:bar", [pathlib.Path("foo"), pathlib.Path("bar")],],
        ["foo::bar", [pathlib.Path("foo"), pathlib.Path("bar")],],
    ],
)
def test_path_to_locations(path, locations):
    assert cli.path_to_locations(path) == locations
