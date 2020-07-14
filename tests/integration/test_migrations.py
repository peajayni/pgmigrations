import os
import pathlib
import tempfile
from unittest.mock import sentinel

import freezegun
import pytest

from pgmigrations import constants, data_access
from pgmigrations.api import Migrations, Migration
from pgmigrations.exceptions import (
    MigrationsNotFound,
    MigrationNotFound,
    MigrationAlreadyExists,
)
from tests import DSN

BASE_LOCATION = pathlib.Path(__file__).parent.absolute() / "fixtures" / "migrations"


@pytest.fixture(autouse=True)
def freeze_time():
    with freezegun.freeze_time("2020-07-01 00:00:00"):
        yield


@pytest.fixture(autouse=True)
def clean_database():
    tables = [constants.MIGRATIONS_TABLE_NAME, "first", "second"]
    with data_access.get_cursor(DSN) as cursor:
        for table in tables:
            if data_access.table_exists(cursor, table):
                data_access.drop_table(cursor, table)


@pytest.fixture(autouse=True)
def workspace():
    with tempfile.TemporaryDirectory() as workspace:
        os.chdir(workspace)
        yield pathlib.Path(workspace)


@pytest.fixture
def inited_workspace(workspace):
    Migrations().init()
    yield workspace


@pytest.fixture
def migrations():
    return Migrations()


def test_migrations_init(inited_workspace, migrations):
    migrations_dir = inited_workspace / constants.MIGRATIONS_DIRECTORY

    assert migrations_dir.exists()


def test_create_migration(inited_workspace, migrations):
    tag = "foo"
    migrations.create(tag)

    expected_migration = (
        inited_workspace
        / constants.MIGRATIONS_DIRECTORY
        / f"20200701_0000_migration_{tag}"
    )
    expected_apply = expected_migration / constants.APPLY_FILENAME
    expected_rollback = expected_migration / constants.ROLLBACK_FILENAME

    assert expected_migration.exists()
    assert expected_apply.exists()
    assert expected_rollback.exists()


def test_create_multiple_migrations(inited_workspace, migrations):
    tag0 = "foo"
    tag1 = "bar"
    migrations.create(tag0)
    migrations.create(tag1)

    expected_migration = (
        inited_workspace
        / constants.MIGRATIONS_DIRECTORY
        / f"20200701_0000_migration_{tag1}"
    )
    expected_apply = expected_migration / constants.APPLY_FILENAME
    expected_rollback = expected_migration / constants.ROLLBACK_FILENAME

    assert expected_migration.exists()
    assert expected_apply.exists()
    assert expected_rollback.exists()


def test_create_duplicate_migrations(inited_workspace, migrations):
    tag = "foo"
    migrations.create(tag)

    with pytest.raises(MigrationAlreadyExists):
        migrations.create(tag)


def test_migrations():
    migrations = Migrations()
    migrations.locations = [BASE_LOCATION]
    expected_migrations = [
        Migration(BASE_LOCATION / "20200701_0000_migration_first"),
        Migration(BASE_LOCATION / "20200701_0000_migration_second"),
    ]
    assert migrations.migrations == expected_migrations


def test_apply():
    migrations = Migrations(locations=[BASE_LOCATION])

    migrations.apply(DSN)

    expected_tables = ["first", "second"]
    with data_access.get_cursor(DSN) as cursor:
        for table in expected_tables:
            assert data_access.table_exists(cursor, table)

        for migration in migrations.migrations:
            assert data_access.has_migration_been_applied(cursor, migration.name)


def test_rollback():
    migrations = Migrations(locations=[BASE_LOCATION])
    migrations.apply(DSN)

    for table, migration in zip(
        ["second", "first"], reversed(migrations.migrations[-2:])
    ):
        migrations.rollback(DSN, migration.name)

        with data_access.get_cursor(DSN) as cursor:
            assert not data_access.table_exists(cursor, table)
            assert not data_access.has_migration_been_applied(cursor, migration.name)


def test_apply_when_no_migrations(workspace):
    migrations = Migrations()
    migrations.locations = []
    with pytest.raises(MigrationsNotFound):
        migrations.apply(DSN)


def test_rollback_when_no_migrations(workspace):
    migrations = Migrations()
    migrations.locations = []
    with pytest.raises(MigrationsNotFound):
        migrations.rollback(DSN, sentinel.name)


def test_rollback_invalid_name():
    migrations = Migrations(locations=[BASE_LOCATION])
    with pytest.raises(MigrationNotFound):
        migrations.rollback(DSN, "does_not_exist")
