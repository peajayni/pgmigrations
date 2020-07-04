CREATE TABLE pgmigrations (
	name varchar(200) PRIMARY KEY,
	applied_at timestamp NOT NULL DEFAULT now()
)
