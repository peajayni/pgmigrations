# pgmigrations

[![Build Status](https://travis-ci.com/peajayni/pgmigrations.svg?branch=master)](https://travis-ci.com/peajayni/pgmigrations)
[![Coverage Status](https://coveralls.io/repos/github/peajayni/pgmigrations/badge.svg?branch=master&kill_cache=1)](https://coveralls.io/github/peajayni/pgmigrations?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


SQL migrations for projects using PostgreSQL

## Example Usage

### Initialise the migrations
```
pgmigrations init --dsn <dsn>
```
or
```
export PGMIGRATIONS_DSN=<dsn>
pgmigrations init
```

This will create a directory called ```migrations``` in the current working directory

### Create a migration
```
pgmigrations create --dsn <dsn> <tag>
```
or
```
export PGMIGRATIONS_DSN=<dsn>
pgmigrations create <tag>
```

This will create a skeleton migration in the ```migrations``` directory. The migration will consist of a directory with
the name ```<timestamp>_migrations_<tag>```, for example ```20200701_1030_migrations_first_migration ```, which 
contains two files; ```apply.sql``` and ```rollback.sql```.

As the names suggests, ```apply.sql``` will be executed when the migration is applied and ```rollback.sql``` will be 
executed if the migraiton is rollbacked.

### Apply migrations
```
pgmigrations apply --dsn=<dsn> [--locations <comma separated list of migration locations>]
```
or
```
export PGMIGRATIONS_DSN=<dsn>
export PGMIGRATIONS_LOCATIONS=<comma separated list of migration locations>
pgmigrations apply
```

This will apply any unapplied migrations. Each migration is applied in an atomic transaction.

### Rollback a migration
```
pgmigrations rollback --dsn=<dsn> [--locations <comma separated list of migration locations>]
```
or
```
export PGMIGRATIONS_DSN=<dsn>
export PGMIGRATIONS_LOCATIONS=<comma separated list of migration locations>
pgmigrations rollback <name>
```

This will rollback an already applied migration. 
