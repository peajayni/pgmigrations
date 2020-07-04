import os
import pathlib
import tempfile

import freezegun
import pytest

from pgmigrations import constants, data_access
from pgmigrations.api import Migrations, Migration
from tests.integration import BASE_DIR, DSN


@pytest.fixture(autouse=True)
def freeze_time():
    with freezegun.freeze_time("2020-07-01 00:00:00"):
        yield


@pytest.fixture(autouse=True)
def clean_database():
    tables = [constants.MIGRATIONS_TABLE_NAME, 'first', 'second']
    with data_access.get_cursor(DSN) as cursor:
        for table in tables:
            if data_access.table_exists(cursor, table):
                data_access.drop_table(cursor, table)


@pytest.fixture
def workspace():
    with tempfile.TemporaryDirectory() as workspace:
        os.chdir(workspace)
        yield pathlib.Path(workspace)


@pytest.fixture
def inited_workspace(workspace):
    Migrations(DSN).init()
    yield workspace


@pytest.fixture
def migrations():
    return Migrations(DSN)


def test_migrations_init(workspace, migrations):
    migrations.init()

    migrations_dir = workspace / constants.MIGRATIONS_DIRECTORY

    assert migrations_dir.exists()

    with data_access.get_cursor(DSN) as cursor:
        assert data_access.table_exists(cursor, constants.MIGRATIONS_TABLE_NAME)


def test_create_first_migration(inited_workspace, migrations):
    tag = "foo"
    migrations.create(tag)

    expected_migration = (
        inited_workspace / constants.MIGRATIONS_DIRECTORY / f"20200701_0000_migration_{tag}"
    )
    expected_up = expected_migration / constants.UP_FILENAME
    expected_down = expected_migration / constants.DOWN_FILENAME

    assert expected_migration.exists()
    assert expected_up.exists()
    assert expected_down.exists()


def test_create_second_migration(inited_workspace, migrations):
    tag0 = "foo"
    tag1 = "bar"
    migrations.create(tag0)
    migrations.create(tag1)

    expected_migration = (
        inited_workspace / constants.MIGRATIONS_DIRECTORY / f"20200701_0000_migration_{tag1}"
    )
    expected_up = expected_migration / constants.UP_FILENAME
    expected_down = expected_migration / constants.DOWN_FILENAME

    assert expected_migration.exists()
    assert expected_up.exists()
    assert expected_down.exists()


def test_migrations():
    migrations = Migrations(DSN, base_dir=BASE_DIR)
    expected_migrations = [
        Migration(migrations, "first"),
        Migration(migrations, "second"),
    ]
    assert migrations.migrations == expected_migrations


def test_up_and_down():
    migrations = Migrations(DSN, base_dir=BASE_DIR)
    migrations.init()

    migrations.up()

    for migration in migrations.migrations:
        with data_access.get_cursor(DSN) as cursor:
            table = migration.tag
            assert data_access.table_exists(cursor, table)
            assert data_access.has_migration_been_applied(cursor, migration.name)

    for migration in migrations.migrations:
        migrations.down(migration.name)

        with data_access.get_cursor(DSN) as cursor:
            table = migration.tag
            assert not data_access.table_exists(cursor, table)
            assert not data_access.has_migration_been_applied(cursor, migration.name)
