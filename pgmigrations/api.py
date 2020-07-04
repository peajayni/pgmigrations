import datetime
import logging
import pathlib

from cached_property import cached_property

from pgmigrations import constants, data_access

LOGGER = logging.getLogger(__name__)
BOOTSTRAP_BASE_DIR = (
    pathlib.Path(__file__).parent.absolute() / constants.BOOTSTRAP_MIGRATIONS_DIRECTORY
)
DEFAULT_BASE_DIR = pathlib.Path(constants.MIGRATIONS_DIRECTORY)


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
    def __init__(self, migrations, tag, timestamp=None):
        self.migrations = migrations
        self.tag = tag
        self.timestamp = timestamp or datetime.datetime.now().strftime("%Y%m%d_%H%M")

    @property
    def dsn(self):
        return self.migrations.dsn

    @property
    def name(self):
        return f"{self.timestamp}_migration_{self.tag}"

    @property
    def path(self):
        return self.migrations.base_dir / self.name

    @classmethod
    def from_path(cls, migrations, path):
        LOGGER.debug("Loading migration instance from path: %s", path)
        timestamp, name = path.name.split("_migration_", maxsplit=1)
        migration = cls(migrations, name, timestamp=timestamp)
        LOGGER.debug("Loaded migration instance: %s", migration)
        return migration

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

            # When bootstrapping the migrations table may not exist
            if data_access.table_exists(cursor, constants.MIGRATIONS_TABLE_NAME):
                data_access.record_rollback(cursor, self.name)
        LOGGER.debug("%s - rollback succeeded", self)

    def is_applied(self, cursor):
        # When bootstrapping the migrations table may not exist
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
            and self.migrations == other.migrations
            and self.name == other.name
        )

    def __lt__(self, other):
        return self.name < other.name


class Migrations:
    def __init__(self, dsn, base_dir=None):
        self.dsn = dsn
        self.base_dir = base_dir if base_dir else DEFAULT_BASE_DIR

    def init(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        bootstrap_migrations = Migrations(self.dsn, base_dir=BOOTSTRAP_BASE_DIR)
        bootstrap_migrations.apply()

    @property
    def migrations(self):
        paths = list(self.base_dir.glob("*_migration_*"))
        LOGGER.debug("Found migration paths: %s", paths)
        migrations = sorted([Migration.from_path(self, path) for path in paths])
        LOGGER.info("Found migrations: %s", migrations)
        return migrations

    def create(self, tag):
        migration = Migration(self, tag)
        with data_access.get_cursor(self.dsn) as cursor:
            if migration.is_applied(cursor):
                raise ValueError("Migration with this name has already been applied")
        migration.create()

    def apply(self):
        for migration in self.migrations:
            migration.apply()

    def rollback(self, name):
        matches = [migration for migration in self.migrations if migration.name == name]
        if not matches:
            raise ValueError(f"Migration {name} not found")
        migration = matches[0]
        migration.rollback()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.base_dir == other.base_dir
