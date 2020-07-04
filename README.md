# pgmigrations

[![Build Status](https://travis-ci.com/peajayni/pgmigrations.svg?branch=master)](https://travis-ci.com/peajayni/pgmigrations)
[![Coverage Status](https://coveralls.io/repos/github/peajayni/pgmigrations/badge.svg?branch=master&kill_cache=1)](https://coveralls.io/github/peajayni/pgmigrations?branch=master)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


SQL migrations for projects using PostgreSQL

## Example Usage

### Initialise the migrations
```
pgmigrations init <dsn>
```
This will create a directory called ```migrations``` and will create a table called ```pgmigrations``` in the database
to store the migration history.

### Create a migration
```
pgmigrations create <tag> <dsn>
```
This will create a skeleton migration in the ```migrations``` directory. The migration will consist of a directory with
the name ```<timestamp>_tag```, for example ```20200701_1030_first_migration ```, which contains two files; 
```apply.sql``` and ```rollback.sql```.

As the names suggests, ```apply.sql``` will be executed when the migration is applied and ```rollback.sql``` will be 
executed if the migraiton is rollbacked.

### Apply migrations
```
pgmigrations apply <dsn>
```
This will apply any unapplied migrations. Each migration is applied in an atomic transaction.

### Rollback a migration
```
pgmigrations rollback <name> <dsn>
```
This will rollback an already applied migration. 
