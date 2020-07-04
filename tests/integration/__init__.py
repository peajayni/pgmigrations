import pathlib

BASE_DIR = pathlib.Path(__file__).parent.absolute() / "fixtures" / "migrations"
DSN = "dbname=test user=test password=test host=localhost"