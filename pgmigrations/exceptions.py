class MigrationsExceptions(Exception):
    pass


class MigrationsNotFound(MigrationsExceptions):
    pass


class MigrationNotFound(MigrationsExceptions):
    pass


class MigrationAlreadyExists(MigrationsExceptions):
    pass
