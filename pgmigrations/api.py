import datetime
import logging
import pathlib

from cached_property import cached_property

from pgmigrations import constants, data_access
from pgmigrations.exceptions import (
    MigrationsNotFound,
    MigrationNotFound,
    MigrationAlreadyExists,
)

LOGGER = logging.getLogger(__name__)
CORE_LOCATION = (
    pathlib.Path(__file__).parent.absolute() / constants.MIGRATIONS_DIRECTORY
)


class MigrationScript:
    def __init__(self, migration, path):
        self.migration = migration
        self.path = path

    def create(self):
        self.path.touch()

    @cached_property
    def sql(self):
        return self.path.read_text()


class Migration:
    def __init__(self, dsn, path):
        self.dsn = dsn
        self.path = path

    @property
    def tag(self):
        _, tag = self.path.name.split("_migration_", maxsplit=1)
        return tag

    @property
    def name(self):
        return self.path.name

    def create(self):
        self.path.mkdir(parents=True, exist_ok=True)
        self.apply_script.create()
        self.rollback_script.create()

    @property
    def apply_script(self):
        path = self.path / constants.APPLY_FILENAME
        return MigrationScript(self, path)

    @property
    def rollback_script(self):
        path = self.path / constants.ROLLBACK_FILENAME
        return MigrationScript(self, path)

    def apply(self):
        LOGGER.debug("%s - running apply", self)
        with data_access.get_cursor(self.dsn) as cursor:
            if self.is_applied(cursor):
                LOGGER.debug("%s - nothing to do", self)
                return
            data_access.execute_sql(cursor, self.apply_script.sql)
            data_access.record_apply(cursor, self.name)
        LOGGER.debug("%s - apply succeeded", self)

    def rollback(self):
        LOGGER.debug("%s - running rollback", self)
        with data_access.get_cursor(self.dsn) as cursor:
            if not self.is_applied(cursor):
                LOGGER.debug("%s - nothing to do", self)
                return
            data_access.execute_sql(cursor, self.rollback_script.sql)

            # When processing the core migrations the table may not exist yet
            if data_access.table_exists(cursor, constants.MIGRATIONS_TABLE_NAME):
                data_access.record_rollback(cursor, self.name)
        LOGGER.debug("%s - rollback succeeded", self)

    def is_applied(self, cursor):
        # When processing the core migrations the table may not exist yet
        if not data_access.table_exists(cursor, constants.MIGRATIONS_TABLE_NAME):
            return False
        return data_access.has_migration_been_applied(cursor, self.name)

    def __str__(self):
        return f"Migration({self.name})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.dsn == other.dsn
            and self.path == other.path
        )

    def __lt__(self, other):
        return self.name < other.name


class Migrations:
    def __init__(self, dsn, locations=None):
        self.dsn = dsn
        self.base_location = pathlib.Path.cwd() / constants.MIGRATIONS_DIRECTORY
        self.locations = [CORE_LOCATION, self.base_location] + (locations or [])

    def init(self):
        self.base_location.mkdir(parents=True, exist_ok=True)

    @property
    def migrations(self):
        paths = []
        for location in self.locations:
            paths += list(location.glob("*_migration_*"))
        LOGGER.debug("Found migration paths: %s", paths)
        migrations = sorted([Migration(self.dsn, path) for path in paths])
        LOGGER.info("Found migrations: %s", migrations)
        return migrations

    def create(self, tag):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        path = self.base_location / f"{timestamp}_migration_{tag}"
        migration = Migration(self.dsn, path)
        if migration in self.migrations:
            raise MigrationAlreadyExists(f"Migration {migration} already exists")
        migration.create()

    def apply(self):
        self.ensure_migrations_exist()
        for migration in self.migrations:
            migration.apply()

    def rollback(self, name):
        self.ensure_migrations_exist()
        matches = [migration for migration in self.migrations if migration.name == name]
        if not matches:
            raise MigrationNotFound(f"Migration {name} not found")
        migration = matches[0]
        migration.rollback()

    def ensure_migrations_exist(self):
        if not self.migrations:
            raise MigrationsNotFound(
                f"Cound not find any migrations in {self.base_location}"
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.dsn == other.dsn
            and self.locations == other.locations
        )
