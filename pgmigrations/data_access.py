import logging
from contextlib import contextmanager

import psycopg2

from pgmigrations import constants

LOGGER = logging.getLogger(__name__)


@contextmanager
def get_cursor(dsn):
    connection = psycopg2.connect(dsn)
    with connection:
        with connection.cursor() as cursor:
            yield cursor


def execute_sql(cursor, sql):
    LOGGER.debug("Executing sql: %s", sql)
    cursor.execute(sql)


def table_exists(cursor, name):
    LOGGER.debug("Checking if table %s exists", name)
    cursor.execute(f"SELECT to_regclass('{name}')")
    row = cursor.fetchone()
    exists = row[0] is not None
    if exists:
        LOGGER.debug("Table %s exists", name)
    else:
        LOGGER.debug("Table %s does not exists", name)
    return exists


def drop_table(cursor, name):
    LOGGER.debug("Dropping table %s", name)
    cursor.execute(f"DROP TABLE {name}")


def has_migration_been_applied(cursor, name):
    LOGGER.debug("Checking if migration %s has been applied", name)
    cursor.execute(
        f"""
        SELECT COUNT(1)
        FROM {constants.MIGRATIONS_TABLE_NAME}
        WHERE name = %s
        """,
        [name],
    )
    row = cursor.fetchone()
    applied = row[0] == 1
    if applied:
        LOGGER.debug("Migration %s has been applied", name)
    else:
        LOGGER.debug("Migration %s has not been applied", name)
    return applied


def record_up(cursor, name):
    LOGGER.debug("Migration %s - recording up", name)
    cursor.execute(
        f"""
        INSERT INTO {constants.MIGRATIONS_TABLE_NAME} (name)
        VALUES (%s)
        """,
        [name],
    )


def record_down(cursor, name):
    LOGGER.debug("Migration %s - recording down", name)
    cursor.execute(
        f"""
        DELETE FROM {constants.MIGRATIONS_TABLE_NAME}
        WHERE name = %s
        """,
        [name],
    )
