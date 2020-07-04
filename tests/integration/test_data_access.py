import pytest

from pgmigrations import data_access
from tests import DSN


@pytest.fixture
def table_name():
    return "migrations"


@pytest.fixture
def table(table_name):
    with data_access.get_cursor(DSN) as cursor:
        data_access.execute_sql(
            cursor,
            f"""
            CREATE TABLE {table_name} (
                name varchar(200) PRIMARY KEY
            )
            """,
        )
    return table_name


@pytest.fixture(autouse=True)
def set_migrations_table_name(monkeypatch, table_name):
    monkeypatch.setattr("pgmigrations.constants.MIGRATIONS_TABLE_NAME", table_name)


@pytest.fixture
def migration_name():
    return "migration0"


@pytest.fixture
def migration(table, migration_name):
    with data_access.get_cursor(DSN) as cursor:
        data_access.execute_sql(
            cursor,
            f"""
            INSERT INTO {table} (name)
            VALUES ('{migration_name}')
            """,
        )
    return migration_name


@pytest.fixture(autouse=True)
def clean_database(table_name):
    with data_access.get_cursor(DSN) as cursor:
        data_access.execute_sql(
            cursor,
            f"""
            DROP TABLE IF EXISTS {table_name}
            """,
        )


def test_table_exists_when_exists(table):
    with data_access.get_cursor(DSN) as cursor:
        assert data_access.table_exists(cursor, table)


def test_table_exists_when_not_exists(table_name):
    with data_access.get_cursor(DSN) as cursor:
        assert not data_access.table_exists(cursor, table_name)


def test_drop_table(table):
    with data_access.get_cursor(DSN) as cursor:
        assert data_access.table_exists(cursor, table)
        data_access.drop_table(cursor, table)
        assert not data_access.table_exists(cursor, table)


def test_has_migration_been_applied_when_applied(migration):
    with data_access.get_cursor(DSN) as cursor:
        assert data_access.has_migration_been_applied(cursor, migration)


def test_has_migration_been_applied_when_not_applied(table, migration_name):
    with data_access.get_cursor(DSN) as cursor:
        assert not data_access.has_migration_been_applied(cursor, migration_name)


def test_record_migration(table, migration_name):
    with data_access.get_cursor(DSN) as cursor:
        assert not data_access.has_migration_been_applied(cursor, migration_name)
        data_access.record_apply(cursor, migration_name)
        assert data_access.has_migration_been_applied(cursor, migration_name)


def test_record_migration(table, migration):
    with data_access.get_cursor(DSN) as cursor:
        assert data_access.has_migration_been_applied(cursor, migration)
        data_access.record_rollback(cursor, migration)
        assert not data_access.has_migration_been_applied(cursor, migration)
